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

import json
from datetime import datetime
from pathlib import Path

OUTPUT_DIR   = Path(__file__).parent.parent / "output"
KNOWLEDGE_DIR = Path(__file__).parent.parent / "knowledge"
OUTPUT_DIR.mkdir(exist_ok=True)
KNOWLEDGE_DIR.mkdir(exist_ok=True)

# Pre-create standard category folders under output/
for _folder in ("jobs", "trends", "learning", "skills"):
    (OUTPUT_DIR / _folder).mkdir(exist_ok=True)


def save_to_file(filename: str, content: str, format: str = "md", folder: str = "") -> dict:
    """Save content to a file in the output directory, optionally in a subfolder."""
    safe_name = "".join(c for c in filename if c.isalnum() or c in "-_ ").strip()
    safe_name = safe_name.replace(" ", "_")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    full_name = f"{safe_name}_{timestamp}.{format}"

    if folder:
        safe_folder = "".join(c for c in folder if c.isalnum() or c in "-_").strip()
        target_dir = OUTPUT_DIR / safe_folder
        target_dir.mkdir(exist_ok=True)
    else:
        target_dir = OUTPUT_DIR

    path = target_dir / full_name
    path.write_text(content, encoding="utf-8")

    return {
        "saved": True,
        "filename": full_name,
        "folder": folder or "(root)",
        "path": str(path),
        "size_bytes": len(content.encode("utf-8"))
    }


def read_file(filename: str) -> str:
    """Read a file from output/ or knowledge/."""
    for base in (OUTPUT_DIR, KNOWLEDGE_DIR):
        path = base / filename
        if path.exists():
            return path.read_text(encoding="utf-8")
        matches = list(base.rglob(f"*{filename}*"))
        if matches:
            return matches[0].read_text(encoding="utf-8")

    return f"File not found: {filename}. Use list_saved_files() to see available files."


def list_saved_files() -> dict:
    """List all files in output/ and knowledge/, grouped by folder."""
    folders = {}

    for base, label in ((OUTPUT_DIR, "output"), (KNOWLEDGE_DIR, "knowledge")):
        for path in sorted(base.rglob("*")):
            if not path.is_file():
                continue
            if path.parent == base:
                folder_name = label
            else:
                folder_name = f"{label}/{path.parent.name}"
            stat = path.stat()
            folders.setdefault(folder_name, []).append({
                "filename": path.name,
                "size": f"{stat.st_size / 1024:.1f} KB",
                "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%Y-%m-%d %H:%M")
            })

    total = sum(len(v) for v in folders.values())
    return {
        "output_directory": str(OUTPUT_DIR),
        "knowledge_directory": str(KNOWLEDGE_DIR),
        "total_files": total,
        "folders": folders
    }
