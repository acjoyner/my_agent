"""
Job skills tools
================
Skill gap analysis, learning resources, and in-demand skill research.
"""

import json


def analyze_skill_gap(job_title: str, current_skills: str) -> dict:
    """
    Compare current skills against what's required for a job title.
    Returns matched skills, missing skills, and priority actions.
    """

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": (
                f"Search job postings and hiring guides for: {job_title}\n\n"
                f"The candidate currently has these skills:\n{current_skills}\n\n"
                "Identify the most commonly required skills for this role and compare.\n\n"
                "Return JSON:\n"
                "{\n"
                f'  "job_title": "{job_title}",\n'
                '  "matched_skills": ["skills the candidate already has"],\n'
                '  "missing_skills": [\n'
                "    {\n"
                '      "skill": "skill name",\n'
                '      "importance": "critical | important | nice-to-have",\n'
                '      "why": "why employers want this skill"\n'
                "    }\n"
                "  ],\n"
                '  "competitive_advantage": ["strengths that stand out for this role"],\n'
                '  "summary": "2-3 sentence overall assessment"\n'
                "}\n\n"
                "Only return JSON."
            )
        }]
    )

    text = " ".join(
        block.text for block in response.content if hasattr(block, "text")
    ).strip()

    try:
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except (json.JSONDecodeError, IndexError):
        return {"job_title": job_title, "summary": text, "matched_skills": [], "missing_skills": []}


def find_learning_resources(skill: str, level: str = "intermediate") -> dict:
    """
    Find courses, tutorials, certifications, and resources for learning a skill.
    """

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": (
                f"Find the best learning resources for: {skill}\n"
                f"Learner level: {level}\n\n"
                "Search for top-rated courses, certifications, tutorials, and free resources.\n\n"
                "Return JSON:\n"
                "{\n"
                f'  "skill": "{skill}",\n'
                f'  "level": "{level}",\n'
                '  "estimated_time_to_proficiency": "e.g. 4-6 weeks",\n'
                '  "resources": [\n'
                "    {\n"
                '      "title": "Course or resource name",\n'
                '      "provider": "Coursera / Udemy / YouTube / etc.",\n'
                '      "url": "link if available",\n'
                '      "cost": "free | $X | subscription",\n'
                '      "type": "course | certification | tutorial | book | practice",\n'
                '      "why_recommended": "brief reason"\n'
                "    }\n"
                "  ],\n"
                '  "learning_path": ["Step 1: ...", "Step 2: ...", "Step 3: ..."],\n'
                '  "pro_tip": "One actionable tip to learn this faster"\n'
                "}\n\n"
                "Include 4-6 resources. Only return JSON."
            )
        }]
    )

    text = " ".join(
        block.text for block in response.content if hasattr(block, "text")
    ).strip()

    try:
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except (json.JSONDecodeError, IndexError):
        return {"skill": skill, "resources": [], "learning_path": [], "pro_tip": text}


def get_in_demand_skills(job_title: str) -> dict:
    """
    Find the most in-demand and trending skills for a job title right now.
    """

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": (
                f"Search current job postings, LinkedIn data, and hiring reports for: {job_title}\n\n"
                "Find the most in-demand skills employers are asking for RIGHT NOW in 2025-2026.\n\n"
                "Return JSON:\n"
                "{\n"
                f'  "job_title": "{job_title}",\n'
                '  "market_snapshot": "1-2 sentence summary of hiring demand",\n'
                '  "top_skills": [\n'
                "    {\n"
                '      "skill": "skill name",\n'
                '      "demand_level": "very high | high | moderate",\n'
                '      "trend": "rising | stable | declining",\n'
                '      "avg_salary_impact": "e.g. +$10k/year",\n'
                '      "notes": "context or why it matters now"\n'
                "    }\n"
                "  ],\n"
                '  "emerging_skills": ["Skills becoming important in the next 1-2 years"],\n'
                '  "certifications_worth_getting": ["Most valued certs for this role"]\n'
                "}\n\n"
                "Include 6-10 top skills. Only return JSON."
            )
        }]
    )

    text = " ".join(
        block.text for block in response.content if hasattr(block, "text")
    ).strip()

    try:
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except (json.JSONDecodeError, IndexError):
        return {"job_title": job_title, "market_snapshot": text, "top_skills": [], "emerging_skills": []}
