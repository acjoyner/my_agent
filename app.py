"""
Web server for the Personal Assistant Agent
============================================
Run: python -m uvicorn app:app --reload --port 8000
Then open: http://localhost:8000
"""

from dotenv import load_dotenv
load_dotenv()

import base64
import io
import os
from typing import List

from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from agent import stream_agent, stream_agent_ollama
from memory.memory import Memory

app = FastAPI(title="Personal Assistant Agent")

# Single shared memory instance (personal single-user tool)
memory = Memory()


def _extract_file_content(upload: UploadFile) -> dict:
    """
    Return a dict describing the file for the agent:
      - text files / code → {"type": "text", "name": ..., "content": ...}
      - PDFs              → {"type": "text", "name": ..., "content": ...}
      - images            → {"type": "image", "name": ..., "media_type": ..., "data": <base64>}
    """
    data = upload.file.read()
    name = upload.filename or "attachment"
    mime = upload.content_type or ""

    # ── Images ────────────────────────────────────────────────────────────────
    if mime.startswith("image/"):
        return {
            "type": "image",
            "name": name,
            "media_type": mime,
            "data": base64.standard_b64encode(data).decode("utf-8"),
        }

    # ── PDFs ──────────────────────────────────────────────────────────────────
    if mime == "application/pdf" or name.lower().endswith(".pdf"):
        try:
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(data))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)
        except Exception as e:
            text = f"[Could not extract PDF text: {e}]"
        return {"type": "text", "name": name, "content": text}

    # ── Word documents ────────────────────────────────────────────────────────
    if mime in ("application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                "application/msword") or name.lower().endswith((".docx", ".doc")):
        try:
            from docx import Document
            doc = Document(io.BytesIO(data))
            text = "\n".join(p.text for p in doc.paragraphs if p.text.strip())
        except Exception as e:
            text = f"[Could not extract Word document text: {e}]"
        return {"type": "text", "name": name, "content": text}

    # ── Everything else as plain text ─────────────────────────────────────────
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        text = data.decode("latin-1", errors="replace")
    return {"type": "text", "name": name, "content": text}


def _build_message(text: str, file_infos: list) -> str | list:
    """
    Build the message to pass to the agent.
    - No files → plain string.
    - Text files → prepend file contents to the string.
    - Images → return a list of Claude content blocks (vision API).
    """
    if not file_infos:
        return text

    images = [f for f in file_infos if f["type"] == "image"]
    texts  = [f for f in file_infos if f["type"] == "text"]

    # Append text file contents to the user message
    extra = ""
    for f in texts:
        extra += f"\n\n--- Attached file: {f['name']} ---\n{f['content']}\n---"

    if not images:
        return (text + extra).strip()

    # Mix of text + images → Claude content block list
    content = []
    for img in images:
        content.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": img["media_type"],
                "data": img["data"],
            }
        })
    content.append({
        "type": "text",
        "text": (text + extra).strip() or "What is in this image?"
    })
    return content


def _is_usage_limit_error(err: str) -> bool:
    return any(p in err for p in ("usage limits", "rate limit", "529", "overloaded", "quota"))


def _safe_stream(message, mem):
    """
    Try Anthropic first. On usage-limit errors, automatically fall back to
    Ollama (if OLLAMA_FALLBACK is True in config/settings.py).
    All other exceptions surface as a readable SSE error message.
    """
    import json
    from config.settings import OLLAMA_FALLBACK

    try:
        yield from stream_agent(message, mem)
    except Exception as e:
        err = str(e)
        if _is_usage_limit_error(err) and OLLAMA_FALLBACK:
            yield f"data: {json.dumps({'type': 'text', 'content': '⚠️ Anthropic API limit reached — switching to local Ollama model...'})}\n\n"
            try:
                yield from stream_agent_ollama(message, mem)
            except Exception as e2:
                yield f"data: {json.dumps({'type': 'text', 'content': f'Ollama fallback also failed: {e2}'})}\n\n"
                yield f"data: {json.dumps({'type': 'done'})}\n\n"
        elif _is_usage_limit_error(err):
            msg = "API usage limit reached. Add `OLLAMA_FALLBACK = True` in config/settings.py to use a local model, or check console.anthropic.com to increase your limit."
            yield f"data: {json.dumps({'type': 'text', 'content': msg})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        elif "401" in err or "authentication" in err.lower():
            yield f"data: {json.dumps({'type': 'text', 'content': 'Invalid API key. Check ANTHROPIC_API_KEY in your .env file.'})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
        else:
            yield f"data: {json.dumps({'type': 'text', 'content': f'Agent error: {err}'})}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"


@app.post("/api/chat")
async def chat(request: Request):
    """
    Stream agent responses as Server-Sent Events.
    Accepts JSON (text-only) or multipart/form-data (with file attachments).
    """
    content_type = request.headers.get("content-type", "")
    if "multipart/form-data" in content_type:
        form = await request.form()
        message = str(form.get("message", ""))
        raw_files = form.getlist("files")
        file_infos = [
            _extract_file_content(f) for f in raw_files
            if hasattr(f, "filename") and f.filename
        ]
    else:
        body = await request.json()
        message = body.get("message", "")
        file_infos = []

    full_message = _build_message(message, file_infos)

    return StreamingResponse(
        _safe_stream(full_message, memory),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


class TTSRequest(BaseModel):
    text: str
    voice: str = "nova"


@app.post("/api/tts")
async def tts(req: TTSRequest):
    """
    Convert text to speech using OpenAI TTS and stream back MP3 audio.
    Requires OPENAI_API_KEY in .env.
    Voices: alloy, echo, fable, onyx, nova, shimmer
    """
    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        return JSONResponse({"error": "OPENAI_API_KEY not set"}, status_code=503)

    from openai import OpenAI as OpenAIClient
    client = OpenAIClient(api_key=api_key)

    response = client.audio.speech.create(
        model="tts-1-hd",
        voice=req.voice,
        input=req.text[:4096],
    )
    return StreamingResponse(
        iter([response.content]),
        media_type="audio/mpeg",
        headers={"Cache-Control": "no-cache"},
    )


@app.get("/api/tts/available")
def tts_available():
    """Let the frontend know if OpenAI TTS is configured."""
    return JSONResponse({"available": bool(os.getenv("OPENAI_API_KEY", ""))})


@app.get("/api/memory")
def get_memory():
    """Return the current memory context for the sidebar (always reads fresh from file)."""
    return JSONResponse({"context": Memory().get_context()})


# Serve the static frontend — must be mounted last
app.mount("/", StaticFiles(directory="static", html=True), name="static")
