"""
File tools
==========
Save and read research results, job lists, notes, and learning docs.

Directory layout:
  output/jobs/        — agent-generated job search results
  output/trends/      — agent-generated market & business trends
  output/learning/    — agent-generated study notes
  output/skills/      — agent-generated skill gap reports and learning plans
  output/             — agent-generated, uncategorized
  knowledge/          — user-provided reference docs (learning notes, project docs, etc.)
"""
import os
import shutil
from datetime import datetime

def scan_directory(path):
    """Returns metadata for images in a directory."""
    if not os.path.exists(path):
        return {"error": f"Path {path} not found."}
    
    files_found = []
    valid_exts = ('.png', '.jpg', '.jpeg', '.gif', '.heic', '.webp')
    
    for root, _, files in os.walk(path):
        for file in files:
            if file.lower().endswith(valid_exts):
                full_path = os.path.join(root, file)
                stats = os.stat(full_path)
                files_found.append({
                    "name": file,
                    "path": full_path,
                    "created": datetime.fromtimestamp(stats.st_ctime).strftime('%Y-%m-%d'),
                    "size_kb": round(stats.st_size / 1024, 2)
                })
    return {"files": files_found}

def move_file(source, destination_folder):
    """Moves a file and ensures the destination exists."""
    try:
        os.makedirs(destination_folder, exist_ok=True)
        shutil.move(source, os.path.join(destination_folder, os.path.basename(source)))
        return {"success": True, "moved_to": destination_folder}
    except Exception as e:
        return {"error": str(e)}

def save_to_file(filename, content, folder="output"):
    """Saves text content to a specified file/folder."""
    try:
        os.makedirs(folder, exist_ok=True)
        file_path = os.path.join(folder, filename)
        with open(file_path, "w") as f:
            f.write(content)
        return f"Saved to {file_path}"
    except Exception as e:
        return f"Save failed: {e}"

def read_file(filename, folder="output"):
    """Reads content from a file."""
    try:
        file_path = os.path.join(folder, filename)
        with open(file_path, "r") as f:
            return f.read()
    except Exception as e:
        return f"Read failed: {e}"

def list_saved_files(folder="output"):
    """Lists files in the output folder."""
    try:
        if not os.path.exists(folder): return []
        return os.listdir(folder)
    except Exception:
        return []