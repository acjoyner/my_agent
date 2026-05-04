import json
from tools.file_tools import scan_directory, move_file, save_to_file

def get_tools():
    return [
        {"name": "scan_directory", "description": "Scans a local directory for photos.", "input_schema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
        {"name": "move_file", "description": "Moves a photo to a destination folder.", "input_schema": {"type": "object", "properties": {"source": {"type": "string"}, "destination_folder": {"type": "string"}}, "required": ["source", "destination_folder"]}},
        {"name": "save_to_file", "description": "Saves content to a local file.", "input_schema": {"type": "object", "properties": {"filename": {"type": "string"}, "content": {"type": "string"}}, "required": ["filename", "content"]}}
    ]

def handle_tool(name, inputs, memory):
    if name == "scan_directory":
        return json.dumps(scan_directory(inputs["path"]))
    if name == "move_file":
        return json.dumps(move_file(inputs["source"], inputs["destination_folder"]))
    if name == "save_to_file":
        return json.dumps(save_to_file(inputs["filename"], inputs["content"]))
    return None

def get_system_prompt():
    return "You have the 'File Manager' skill. Use it to scan for images and organize files on the local machine."
