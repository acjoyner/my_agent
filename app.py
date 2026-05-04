from fastapi import FastAPI, Request, Form, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.staticfiles import StaticFiles
from agent import stream_agent
from memory.memory import Memory
import uvicorn
import json
import os
from typing import List, Optional

app = FastAPI()
memory = Memory()

# --- API Endpoints ---

@app.post("/api/chat")
async def chat_endpoint(
    request: Request,
    message: Optional[str] = Form(None),
    files: Optional[List[UploadFile]] = File(None)
):
    """
    Handles both standard JSON chat and Multipart Form Data (file uploads).
    """
    user_message = ""

    # 1. Handle Multipart Form Data (when files/images are attached)
    if message is not None:
        user_message = message
        if files:
            # Ensure the uploads directory exists to avoid the 500 error
            os.makedirs("uploads", exist_ok=True)
            
            for file in files:
                contents = await file.read()
                file_path = os.path.join("uploads", file.filename)
                with open(file_path, "wb") as f:
                    f.write(contents)
                print(f"📁 File saved: {file_path}")
    
    # 2. Handle standard JSON (when no files are attached)
    else:
        try:
            data = await request.json()
            user_message = data.get("message", "")
        except Exception:
            user_message = ""
        
    return StreamingResponse(
        stream_agent(user_message, memory), 
        media_type="text/event-stream"
    )

@app.get("/api/memory")
async def get_memory():
    """Returns the current state of the agent's memory."""
    return {"context": memory.get_context()}

@app.get("/api/tts/available")
async def tts_available():
    """Tells the frontend that we are using local browser voices only."""
    return {"available": False}

@app.post("/api/tts")
async def tts_proxy():
    """Tells the frontend to fallback to browser."""
    from fastapi.responses import JSONResponse
    return JSONResponse(content={"error": "Local mode active: using browser speech synthesis."}, status_code=400)

# --- Skill-Based Route Mounting ---

from agent import SKILLS
import logging
logger = logging.getLogger(__name__)

for skill in SKILLS:
    if hasattr(skill, "app"):
        prefix = f"/{skill.__name__.split('.')[-1]}"
        app.mount(prefix, skill.app)
        logger.info(f"Mounted skill sub-app at {prefix}")

# --- Static File Serving ---

app.mount("/", StaticFiles(directory="static", html=True), name="static")

if __name__ == "__main__":
    # Ensure standard folders exist on startup
    os.makedirs("uploads", exist_ok=True)
    os.makedirs("output", exist_ok=True)
    
    print("🚀 Server starting at http://127.0.0.1:8000")
    uvicorn.run(app, host="127.0.0.1", port=8000)