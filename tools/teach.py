"""
Teaching tools for job role preparation
Interactive lessons, quizzes, progress tracking, and study plans.
Adapts to any job description stored in memory (defaults to WF AI Engineer role).
"""

import json
from tools.client import client
from datetime import datetime
from memory.memory import MEMORY_FILE
from config.settings import RESUME_TEXT

# Default fallback job context (Wells Fargo AI Engineer role)
_WF_DEFAULT = {
    "role_title": "Senior AI Engineer",
    "company": "Wells Fargo",
    "industry_domain": "banking and financial services",
    "required_skills": [
        "Foundation LLMs", "Advanced RAG / GraphRAG", "Embeddings at scale",
        "Knowledge graphs & ontology extraction", "Agentic AI systems",
        "MCP integrations", "LLMOps / MLOps", "Scalable REST APIs",
        "Cloud deployment", "Full-stack Python",
    ],
    "nice_to_have": [],
    "interview_themes": [
        "Production LLM systems you've built",
        "Handling hallucinations in regulated environments",
        "GraphRAG vs naive RAG trade-offs",
        "LLM observability and monitoring in prod",
    ],
}


def _load_memory() -> dict:
    """Read memory.json, return empty dict on failure."""
    if MEMORY_FILE.exists():
        try:
            return json.loads(MEMORY_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {}


def _save_memory(data: dict):
    MEMORY_FILE.parent.mkdir(exist_ok=True)
    MEMORY_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _load_job_context() -> dict:
    """Return active_job_target from memory, or WF defaults."""
    return _load_memory().get("active_job_target", _WF_DEFAULT)


def _parse_json(text: str):
    """Strip markdown fences and parse JSON; return None on failure."""
    t = text.strip()
    if t.startswith("```"):
        parts = t.split("```")
        t = parts[1].lstrip("json").strip() if len(parts) > 1 else t
    try:
        return json.loads(t)
    except (json.JSONDecodeError, ValueError):
        return None


def parse_job_description(jd_text: str) -> dict:
    """
    Parse any job description and save it as the active learning target in memory.
    Call this whenever the user pastes a new job description.
    """
    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=800,
        messages=[{
            "role": "user",
            "content": (
                "Extract key info from this job description. "
                "Return compact JSON with keys: role_title, company, industry_domain, "
                "required_skills(str[]), nice_to_have(str[]), interview_themes(str[]). "
                "Only JSON, no fences.\n\n"
                f"{jd_text[:3000]}"
            )
        }]
    )

    text = " ".join(b.text for b in response.content if hasattr(b, "text"))
    parsed = _parse_json(text)

    if not parsed or not isinstance(parsed, dict):
        parsed = {**_WF_DEFAULT, "raw": text}

    # Persist to memory
    data = _load_memory()
    data["active_job_target"] = parsed
    _save_memory(data)

    return {"saved": True, **parsed}


def generate_lesson(topic: str, skill_area: str, level: str = "intermediate") -> dict:
    """
    Teach a specific sub-topic within a skill area.
    Automatically uses the active job target (or WF defaults) for context.
    """
    job = _load_job_context()

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1500,
        messages=[{
            "role": "user",
            "content": (
                f"Teach a {level} lesson on '{topic}' (skill area: {skill_area}) "
                f"for a {job['role_title']} role at {job['company']} "
                f"({job['industry_domain']} industry). "
                "Use domain-relevant code examples. "
                "Return compact JSON — keys: topic, skill_area, level, "
                "explanation(2-3 sentences), code_example(runnable Python), "
                "gotchas(str[3]), next_steps(str[3]). Only JSON, no fences."
            )
        }]
    )

    text = " ".join(b.text for b in response.content if hasattr(b, "text"))
    result = _parse_json(text)

    if not result or not isinstance(result, dict):
        return {"topic": topic, "skill_area": skill_area, "level": level,
                "explanation": text, "code_example": "", "gotchas": [], "next_steps": []}
    return result


def quiz_me(topic: str, skill_area: str, num_questions: int = 3) -> dict:
    """
    Generate a quiz on a topic. Mix of multiple_choice, short_answer, code_completion.
    Uses active job context for domain framing.
    """
    job = _load_job_context()

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        messages=[{
            "role": "user",
            "content": (
                f"Create a {num_questions}-question quiz on '{topic}' ({skill_area}) "
                f"for a {job['role_title']} candidate at {job['company']}. "
                "Mix types: multiple_choice, short_answer, code_completion (one of each if ≥3 questions). "
                "Return compact JSON — keys: topic, skill_area, questions(array of "
                "{question, type, choices(str[]), answer, explanation}). Only JSON, no fences."
            )
        }]
    )

    text = " ".join(b.text for b in response.content if hasattr(b, "text"))
    result = _parse_json(text)

    if not result or not isinstance(result, dict):
        return {"topic": topic, "skill_area": skill_area, "questions": []}
    return result


def update_progress(skill_area: str, topic: str, score: int = -1, notes: str = "") -> dict:
    """
    Record learning progress. No LLM call — writes directly to memory.json.
    """
    data = _load_memory()
    if "learning" not in data:
        data["learning"] = {}

    area = data["learning"].setdefault(skill_area, {
        "topics_covered": [], "last_score": -1, "last_studied": None, "notes": ""
    })

    if topic not in area["topics_covered"]:
        area["topics_covered"].append(topic)
    if score >= 0:
        area["last_score"] = score
    if notes:
        area["notes"] = notes
    area["last_studied"] = datetime.now().isoformat()

    _save_memory(data)

    return {
        "saved": True,
        "skill_area": skill_area,
        "topics_covered_total": len(area["topics_covered"]),
        "last_score": area["last_score"],
    }


def get_study_plan(weeks_available: int = 8, target_weak_areas: str = "") -> dict:
    """
    Generate a personalized week-by-week study plan.
    Uses active job target skills + resume to identify gaps.
    """
    job = _load_job_context()
    skills_list = "\n".join(f"- {s}" for s in job["required_skills"])
    weak = f"Prioritize: {target_weak_areas}" if target_weak_areas else "Infer gaps from resume vs required skills."

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=3000,
        messages=[{
            "role": "user",
            "content": (
                f"Create a {weeks_available}-week study plan for: "
                f"{job['role_title']} at {job['company']} ({job['industry_domain']}).\n"
                f"Required skills:\n{skills_list}\n"
                f"Resume summary:\n{RESUME_TEXT}\n"
                f"{weak}\n"
                "1-2 hrs/day. Include a hands-on project milestone each week. "
                "Return compact JSON — keys: total_weeks, priority_order(str[]), "
                "weekly_plan(array of {week, focus, daily_goals(str[5]), hours_per_day, milestone}), "
                "interview_tips(str[]). Only JSON, no fences."
            )
        }]
    )

    text = " ".join(b.text for b in response.content if hasattr(b, "text"))
    result = _parse_json(text)

    if not result or not isinstance(result, dict):
        return {"total_weeks": weeks_available, "priority_order": job["required_skills"],
                "weekly_plan": [], "interview_tips": [text]}
    return result
