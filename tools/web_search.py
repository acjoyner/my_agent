"""
Web search tool
===============
Uses the Anthropic API's built-in web search via a sub-call to Claude.
No extra API keys needed.
"""

import anthropic
import json


def search_web(query: str, num_results: int = 5) -> dict:
    """
    Search the web using Claude's built-in web search tool.
    Returns a dict with 'query', 'summary', and 'results' list.
    """
    client = anthropic.Anthropic()

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=1500,
        tools=[{"type": "web_search_20250305", "name": "web_search"}],
        messages=[{
            "role": "user",
            "content": (
                f"Search for: {query}\n\n"
                f"Return the top {num_results} results as JSON with this structure:\n"
                '{"summary": "...", "results": [{"title": "...", "url": "...", "snippet": "..."}]}\n'
                "Only return JSON, no other text."
            )
        }]
    )

    # Extract text from all response blocks
    text = " ".join(
        block.text for block in response.content if hasattr(block, "text")
    ).strip()

    # Try to parse JSON, fall back to raw text
    try:
        # Strip markdown fences if present
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        return json.loads(text.strip())
    except (json.JSONDecodeError, IndexError):
        return {
            "query": query,
            "summary": text,
            "results": []
        }
