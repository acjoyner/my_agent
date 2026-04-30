"""
Trends & business ideas tool
=============================
Uses Claude's web search to find industry trends and business opportunities.
"""

import json


def search_trends(topic: str, timeframe: str = "month") -> dict:
    """
    Search for current trends in a topic.
    Returns a structured list of trends with growth signals.
    """

    timeframe_label = {
        "week":  "past 7 days",
        "month": "past 30 days",
        "year":  "past 12 months"
    }.get(timeframe, "past 30 days")

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": (
                f"Search for the latest trends in {topic} over the {timeframe_label}.\n\n"
                "Return JSON with this structure:\n"
                "{\n"
                f'  "topic": "{topic}",\n'
                f'  "timeframe": "{timeframe_label}",\n'
                '  "headline_summary": "2-3 sentence overview of what\'s happening",\n'
                '  "trends": [\n'
                "    {\n"
                '      "name": "Trend name",\n'
                '      "signal": "Why it\'s growing — data, stats, examples",\n'
                '      "growth": "rising | peaking | stable | declining",\n'
                '      "opportunity": "How someone could capitalize on this"\n'
                "    }\n"
                "  ],\n"
                '  "sources": ["url1", "url2"]\n'
                "}\n\n"
                "Include 5-8 trends. Only return JSON."
            )
        }]
    )

    text = " ".join(
        getattr(block, "text", "") for block in response.content if hasattr(block, "text")
    ).strip()

    try:
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except (json.JSONDecodeError, IndexError):
        return {"topic": topic, "headline_summary": text, "trends": [], "sources": []}


def search_business_ideas(area: str, budget: str = "low") -> dict:
    """
    Find underserved niches and business opportunities in a given area.
    Returns pain points, gaps, and actionable ideas.
    """

    budget_desc = {
        "low":    "under $5,000 startup cost",
        "medium": "$5,000–$50,000 startup cost",
        "high":   "$50,000+ startup cost"
    }.get(budget, "low startup cost")

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": (
                f"Research underserved business opportunities in: {area}\n"
                f"Budget range: {budget_desc}\n\n"
                "Search for recent complaints, forum posts, Reddit threads, and news "
                "showing what problems people are paying to solve right now in this space.\n\n"
                "Return JSON:\n"
                "{\n"
                f'  "area": "{area}",\n'
                '  "market_summary": "Current state of this market",\n'
                '  "ideas": [\n'
                "    {\n"
                '      "name": "Business idea name",\n'
                '      "problem_it_solves": "Specific pain point",\n'
                '      "target_customer": "Who would pay for this",\n'
                '      "revenue_model": "How it makes money",\n'
                '      "estimated_startup_cost": "$X",\n'
                '      "competition_level": "low | medium | high",\n'
                '      "evidence": "Why there is demand — forums, searches, growth data"\n'
                "    }\n"
                "  ],\n"
                '  "avoid": ["Things that are saturated or declining in this space"]\n'
                "}\n\n"
                "Return 4-6 ideas. Only return JSON."
            )
        }]
    )

    text = " ".join(
        getattr(block, "text", "") for block in response.content if hasattr(block, "text")
    ).strip()

    try:
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except (json.JSONDecodeError, IndexError):
        return {"area": area, "market_summary": text, "ideas": [], "avoid": []}
