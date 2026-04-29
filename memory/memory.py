"""
Memory system
=============
Gives the agent persistent memory across sessions.
Stores:
  - User preferences (salary expectations, preferred locations, industries)
  - Conversation history (last N exchanges)
  - Saved facts and notes

Uses a simple JSON file — no database required.
"""

import json
from pathlib import Path
from datetime import datetime
# from typing import Optional

MEMORY_FILE = Path(__file__).parent.parent / "memory" / "memory.json"
MAX_HISTORY = 20   # Keep last 20 exchanges in context


class Memory:
    def __init__(self):
        MEMORY_FILE.parent.mkdir(exist_ok=True)
        self._data = self._load()

    # ── Persistence ────────────────────────────────────────────────────────────

    def _load(self) -> dict:
        if MEMORY_FILE.exists():
            try:
                return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                pass
        return {
            "preferences": {},
            "history": [],       # list of {role, content} pairs
            "notes": [],         # list of {timestamp, note}
            "profile": {}        # anything the agent learns about the user
        }

    def _save(self):
        MEMORY_FILE.write_text(
            json.dumps(self._data, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

    # ── History ────────────────────────────────────────────────────────────────

    def add_exchange(self, user_msg: str, agent_msg: str):
        """Record a completed exchange."""
        self._data["history"].append({
            "timestamp": datetime.now().isoformat(),
            "user": user_msg,
            "agent": agent_msg[:500]   # truncate long responses to save space
        })
        # Keep only the last MAX_HISTORY
        self._data["history"] = self._data["history"][-MAX_HISTORY:]
        self._save()

    def get_recent_messages(self) -> list:
        """
        Return recent history formatted as Claude API messages.
        Only returns the last 6 exchanges to avoid bloating context.
        """
        messages = []
        for exchange in self._data["history"][-6:]:
            messages.append({"role": "user",      "content": exchange["user"]})
            messages.append({"role": "assistant", "content": exchange["agent"]})
        return messages

    # ── Preferences ────────────────────────────────────────────────────────────

    def set_preference(self, key: str, value):
        """Save a user preference (e.g. min_salary=80000, location='remote')."""
        self._data["preferences"][key] = value
        self._save()

    def get_preference(self, key: str, default=None):
        return self._data["preferences"].get(key, default)

    # ── Context string for system prompt ──────────────────────────────────────

    def get_context(self) -> str:
        """
        Build a concise context string to inject into the system prompt.
        Tells Claude what it already knows about the user.
        """
        lines = []

        if self._data["preferences"]:
            lines.append("User preferences:")
            for k, v in self._data["preferences"].items():
                lines.append(f"  - {k}: {v}")

        if self._data["profile"]:
            lines.append("\nLearned about user:")
            for k, v in self._data["profile"].items():
                lines.append(f"  - {k}: {v}")

        if self._data["notes"]:
            lines.append("\nSaved notes:")
            for note in self._data["notes"][-5:]:
                lines.append(f"  - [{note['timestamp'][:10]}] {note['note']}")

        if self._data.get("active_job_target"):
            jt = self._data["active_job_target"]
            lines.append(f"\nActive job target: {jt.get('role_title', '')} at {jt.get('company', '')}")
            skills = jt.get("required_skills", [])
            if skills:
                preview = ", ".join(skills[:8])
                lines.append(f"  Required skills: {preview}" + (" ..." if len(skills) > 8 else ""))

        if self._data.get("learning"):
            lines.append("\nLearning progress:")
            for area, data in self._data["learning"].items():
                covered = len(data.get("topics_covered", []))
                score = data.get("last_score", "N/A")
                lines.append(f"  - {area}: {covered} topics covered, last score: {score}")

        if not lines:
            lines.append("No preferences saved yet. As you use the agent, it will remember your preferences.")

        return "\n".join(lines)

    # ── Notes ──────────────────────────────────────────────────────────────────

    def add_note(self, note: str):
        self._data["notes"].append({
            "timestamp": datetime.now().isoformat(),
            "note": note
        })
        self._save()

    # ── Profile ────────────────────────────────────────────────────────────────

    def update_profile(self, key: str, value: str):
        """Store something the agent inferred about the user."""
        self._data["profile"][key] = value
        self._save()
