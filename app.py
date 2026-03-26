"""
Web server for the Personal Assistant Agent
============================================
Run: python -m uvicorn app:app --reload --port 8000
Then open: http://localhost:8000
"""

from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from agent import stream_agent
from memory.memory import Memory

app = FastAPI(title="Personal Assistant Agent")

# Single shared memory instance (personal single-user tool)
memory = Memory()


class ChatRequest(BaseModel):
    message: str


@app.post("/api/chat")
def chat(req: ChatRequest):
    """Stream agent responses as Server-Sent Events."""
    return StreamingResponse(
        stream_agent(req.message, memory),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        }
    )


@app.get("/api/memory")
def get_memory():
    """Return the current memory context for the sidebar."""
    return JSONResponse({"context": memory.get_context()})


# Serve the static frontend — must be mounted last
app.mount("/", StaticFiles(directory="static", html=True), name="static")
