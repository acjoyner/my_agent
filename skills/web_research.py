import json
from tools.web_search import search_web

def get_tools():
    return [
        {"name": "search_web", "description": "Search the web for any topic.", "input_schema": {"type": "object", "properties": {"query": {"type": "string"}}, "required": ["query"]}}
    ]

def handle_tool(name, inputs, memory):
    if name == "search_web":
        return json.dumps(search_web(inputs["query"]))
    return None

def get_system_prompt():
    return "You have the 'Web Research' skill. Use it to search for real-time information and trends."
