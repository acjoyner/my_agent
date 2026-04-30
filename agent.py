"""
Personal Assistant Agent
========================
Researches jobs, business trends, and handles personal assistant tasks.
Run: python agent.py
"""

import json
import os
from dotenv import load_dotenv
from config.settings import RESUME_TEXT, OLLAMA_BASE_URL, OLLAMA_MODEL, OLLAMA_FALLBACK_MODELS
from memory.memory import Memory

# Tool Imports
from tools.web_search import search_web
from tools.job_search import search_jobs, get_job_details
from tools.trends import search_trends, search_business_ideas
from tools.skills import analyze_skill_gap, find_learning_resources, get_in_demand_skills
from tools.teach import generate_lesson, quiz_me, update_progress, get_study_plan, parse_job_description
from tools.file_tools import save_to_file, read_file, list_saved_files
from tools.notify import send_notification, send_email, send_telegram
from tools.google_tools import (
    sheets_create, sheets_read, sheets_write, sheets_append,
    docs_create, docs_read, drive_list, drive_upload,
    gmail_read_inbox, gmail_get_message, gmail_search, gmail_mark_read,
    slides_create, slides_read, slides_add_slide
)

load_dotenv()

# ── Tool Registry ──────────────────────────────────────────────────────────────

TOOLS = [
    {"name": "search_web", "description": "Search the web for any topic.", "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}},
    {"name": "search_jobs", "description": "Search for job listings.", "input_schema": {"type": "object", "properties": {"title": {"type": "string"}, "location": {"type": "string"}}, "required": ["title"]}},
    {"name": "save_to_file", "description": "Save content to a file.", "input_schema": {"type": "object", "properties": {"filename": {"type": "string"}, "content": {"type": "string"}}, "required": ["filename", "content"]}},
    {"name": "analyze_skill_gap", "description": "Compare skills against a target job.", "input_schema": {"type": "object", "properties": {"job_title": {"type": "string"}, "current_skills": {"type": "string"}}, "required": ["job_title", "current_skills"]}}
    # Note: Additional tools can be added here following the same schema
]

def run_tool(name: str, inputs: dict, memory=None) -> str:
    dispatch = {
        "search_web": lambda i: search_web(i["query"]),
        "search_jobs": lambda i: search_jobs(i["title"], location=i.get("location")),
        "analyze_skill_gap": lambda i: analyze_skill_gap(i["job_title"], i["current_skills"]),
        "save_to_file": lambda i: save_to_file(i["filename"], i["content"])
    }
    if name not in dispatch: return f"Unknown tool: {name}"
    try:
        result = dispatch[name](inputs)
        return json.dumps(result) if isinstance(result, (dict, list)) else str(result)
    except Exception as e: return f"Tool error: {e}"

# ── Ollama Agent Logic ────────────────────────────────────────────────────────

def _tools_to_ollama(tools: list) -> list:
    return [{"type": "function", "function": {"name": t["name"], "description": t["description"], "parameters": t.get("input_schema", {})}} for t in tools]

def stream_agent_ollama(user_message: str, memory: Memory, model: str = "gemma4"):
    from openai import OpenAI
    client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
    
    system_prompt = f"You are Anthony's AI Assistant. Use tools for job searches and research.\n\nResume Context:\n{RESUME_TEXT}"
    
    messages = [{"role": "system", "content": system_prompt}]
    for msg in memory.get_recent_messages():
        messages.append(msg)
    messages.append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=_tools_to_ollama(TOOLS),
            tool_choice="auto"
        )
        
        msg = response.choices[0].message
        if msg.tool_calls:
            for tool_call in msg.tool_calls:
                name = tool_call.function.name
                inputs = json.loads(tool_call.function.arguments)
                yield f"data: {json.dumps({'type': 'tool', 'name': name, 'input': inputs})}\n\n"
                result = run_tool(name, inputs, memory)
                yield f"data: {json.dumps({'type': 'result', 'name': name})}\n\n"
            
            # Final thought after tool use
            yield f"data: {json.dumps({'type': 'text', 'content': 'Tools executed. Processing results...'})}\n\n"
        else:
            yield f"data: {json.dumps({'type': 'text', 'content': msg.content})}\n\n"
            
        yield f"data: {json.dumps({'type': 'done'})}\n\n"
    except Exception as e:
        yield f"data: {json.dumps({'type': 'text', 'content': f'Error: {str(e)}'})}\n\n"

def run_agent(user_message: str, memory: Memory) -> str:
    # Synchronous wrapper for CLI
    gen = stream_agent_ollama(user_message, memory)
    final_text = ""
    for line in gen:
        if "data: " in line:
            data = json.loads(line.replace("data: ", ""))
            if data['type'] == 'text': final_text += data['content']
    return final_text

def stream_agent(user_message: str, memory: Memory):
    return stream_agent_ollama(user_message, memory)

if __name__ == "__main__":
    memory = Memory()
    while True:
        u_in = input("You: ")
        if u_in.lower() in ['exit', 'quit']: break
        print(f"Agent: {run_agent(u_in, memory)}")