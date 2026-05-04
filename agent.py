"""
Personal Assistant Agent
========================
Researches jobs, business trends, and handles personal assistant tasks.
Run: python agent.py
"""

import json
import os
import base64
from openai import OpenAI
from dotenv import load_dotenv
from config.settings import RESUME_TEXT, OLLAMA_BASE_URL, OLLAMA_MODEL
from memory.memory import Memory
from skills import load_skills

load_dotenv()

client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")

# ── Skill Management ──────────────────────────────────────────────────────────

SKILLS = load_skills()

def get_all_tools():
    """Aggregates tool schemas from all loaded skills."""
    all_tools = []
    for skill in SKILLS:
        all_tools.extend(skill.get_tools())
    return all_tools

def run_tool(name: str, inputs: dict, memory=None) -> str:
    """Dispatches tool execution to the appropriate skill module."""
    for skill in SKILLS:
        result = skill.handle_tool(name, inputs, memory)
        if result is not None:
            return result
    return f"Unknown tool: {name}"

def get_skills_context():
    """Aggregates system prompts from all loaded skills."""
    context = ""
    for skill in SKILLS:
        if hasattr(skill, "get_system_prompt"):
            context += f"\n- {skill.get_system_prompt()}"
    return context

# ── Ollama Agent Logic ────────────────────────────────────────────────────────

def _tools_to_ollama(tools: list) -> list:
    return [{"type": "function", "function": {"name": t["name"], "description": t["description"], "parameters": t.get("input_schema", {})}} for t in tools]

def _encode_image(image_path):
    """Encodes a local image file to base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def stream_agent_ollama(user_message: str, memory: Memory):
    global client
    # 1. ROUTER: Detect if we need 'Eyes' (Vision) or 'Brain' (Tools)
    vision_keywords = ['.jpg', '.png', '.jpeg', '.webp', 'photo', 'picture', 'image', 'look at']
    is_vision_request = any(word in user_message.lower() for word in vision_keywords)
    
    # Switch models: llava:latest for images (better for ID cards), gemma4 for logic/tools
    selected_model = "llava:latest" if is_vision_request else "gemma4"

    system_prompt = (
        f"You are Anthony's Assistant. Context:\n{RESUME_TEXT}\n"
        f"\nUser Context:\n{memory.get_context()}"
        f"\nActive Skills:{get_skills_context()}"
    )
    messages = [{"role": "system", "content": system_prompt}]
    
    # Add history from memory
    for msg in memory.get_recent_messages():
        if msg.get("content"):
            messages.append(msg)
    
    # 2. Add Local File Context for the Vision Model
    user_content = []
    if is_vision_request:
        uploads_dir = "uploads"
        if os.path.exists(uploads_dir):
            image_extensions = ('.png', '.jpg', '.jpeg', '.webp')
            files = [os.path.join(uploads_dir, f) for f in os.listdir(uploads_dir) if f.lower().endswith(image_extensions)]
            if files:
                latest_file = max(files, key=os.path.getctime)
                try:
                    base64_image = _encode_image(latest_file)
                    user_content.append({"type": "text", "text": f"[Analyzing file: {latest_file}] {user_message}"})
                    user_content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}
                    })
                except Exception as e:
                    user_content = f"[Error loading image {latest_file}: {e}] {user_message}"
            else:
                user_content = user_message
        else:
            user_content = user_message
    else:
        user_content = user_message

    messages.append({"role": "user", "content": user_content})

    # 3. TOOL GUARD: Only send tools to models that support them (Gemma 4)
    tool_params = {}
    if selected_model == "gemma4":
        tool_params = {
            "tools": _tools_to_ollama(get_all_tools()),
            "tool_choice": "auto"
        }

    try:
        # 4. Call Ollama
        response = client.chat.completions.create(
            model=selected_model,
            messages=messages,
            **tool_params
        )

        msg = response.choices[0].message
        
        # 5. Handle Tool/Text logic
        if hasattr(msg, 'tool_calls') and msg.tool_calls:
            for tool_call in msg.tool_calls:
                name = tool_call.function.name
                inputs = json.loads(tool_call.function.arguments)
                yield f"data: {json.dumps({'type': 'tool', 'name': name, 'input': inputs})}\n\n"
                
                result = run_tool(name, inputs, memory)
                
                # Try to extract display_text if available
                display_content = result
                try:
                    res_json = json.loads(result)
                    if isinstance(res_json, dict) and "display_text" in res_json:
                        display_content = res_json["display_text"]
                except: pass

                yield f"data: {json.dumps({'type': 'result', 'name': name})}\n\n"
                yield f"data: {json.dumps({'type': 'text', 'content': display_content})}\n\n"
        else:
            yield f"data: {json.dumps({'type': 'text', 'content': msg.content})}\n\n"

        yield f"data: {json.dumps({'type': 'done'})}\n\n"
        
    except Exception as e:
        yield f"data: {json.dumps({'type': 'text', 'content': f'Error: {str(e)}'})}\n\n"

def run_agent(user_message: str, memory: Memory) -> str:
    gen, final_text = stream_agent_ollama(user_message, memory), ""
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
        try:
            u_in = input("You: ")
            if u_in.lower() in ['exit', 'quit']: break
            print("Agent: ", end="", flush=True)
            for chunk in stream_agent(u_in, memory):
                if "data: " in chunk:
                    data = json.loads(chunk.replace("data: ", ""))
                    if data['type'] == 'text':
                        print(data['content'], end="", flush=True)
            print("\n")
        except KeyboardInterrupt:
            break
