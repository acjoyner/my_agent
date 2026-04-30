"""
Job search tool
Searches job boards via Claude's web search (no extra keys needed).
For production use, swap search_jobs() internals with Indeed/LinkedIn APIs.
"""

import json
import re


def search_jobs(
    title: str,
    location: str = None,
    min_salary: int = None,
    keywords: list = None,
    remote: bool = False
) -> dict:
    """
    Search for job listings matching the given criteria.
    Returns a structured list of jobs.
    """

    # Build a natural-language search query
    parts = [f'"{title}" jobs']
    if remote:
        parts.append("remote")
    if location:
        parts.append(f"in {location}")
    if min_salary:
        parts.append(f"salary at least ${min_salary:,}")
    if keywords:
        parts.append(" ".join(keywords))
    parts.append("site:linkedin.com OR site:indeed.com OR site:remoteok.com 2025")

    query = " ".join(parts)

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=2000,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": (
                f"Search for jobs matching: {query}\n\n"
                "Return a JSON object with this exact structure:\n"
                "{\n"
                '  "total_found": 12,\n'
                '  "search_criteria": {"title": "...", "location": "...", "remote": true},\n'
                '  "jobs": [\n'
                "    {\n"
                '      "id": "job_1",\n'
                '      "title": "Senior Marketing Manager",\n'
                '      "company": "Acme Corp",\n'
                '      "location": "Remote",\n'
                '      "salary": "$90,000 - $120,000",\n'
                '      "type": "Full-time",\n'
                '      "posted": "2 days ago",\n'
                '      "url": "https://...",\n'
                '      "highlights": ["5 years experience", "health benefits", "equity"]\n'
                "    }\n"
                "  ]\n"
                "}\n\n"
                "Include at least 5 real jobs if available. Only return JSON."
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
        return {
            "total_found": 0,
            "search_criteria": {"title": title, "location": location, "remote": remote},
            "jobs": [],
            "raw": text
        }


def get_job_details(job_id: str) -> dict:
    """
    Get full details for a specific job by ID.
    In a real implementation this would fetch the URL scraped during search.
    """
    return {
        "job_id": job_id,
        "note": (
            "In production, store the job URL during search_jobs and fetch its full "
            "description here using a browser tool or scraping library like requests + "
            "BeautifulSoup. For now, use the highlights from search_jobs."
        )
    }
