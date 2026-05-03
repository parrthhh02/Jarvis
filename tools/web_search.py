"""
Lilu — Web Search Tool
Search the web using DuckDuckGo (no API key required).
"""

import logging

logger = logging.getLogger("lilu.tools.search")


def web_search(query: str, max_results: int = 5) -> dict:
    """
    Search the web using DuckDuckGo.

    Args:
        query: Search query string.
        max_results: Maximum number of results to return (1-10).

    Returns:
        dict with search results.
    """
    try:
        from duckduckgo_search import DDGS
    except ImportError:
        return {
            "error": "duckduckgo-search not installed. Run: pip install duckduckgo-search"
        }

    max_results = min(max(1, max_results), 10)

    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))

        formatted = []
        for r in results:
            formatted.append({
                "title": r.get("title", ""),
                "url": r.get("href", r.get("link", "")),
                "snippet": r.get("body", r.get("snippet", "")),
            })

        return {
            "query": query,
            "result_count": len(formatted),
            "results": formatted,
        }

    except Exception as e:
        logger.error(f"Web search failed: {e}")
        return {"error": f"Search failed: {str(e)}"}


# ── Tool Definition for Registry ─────────────────────

TOOL_DEFINITIONS = [
    {
        "name": "web_search",
        "description": (
            "Search the web using DuckDuckGo. Returns titles, URLs, and snippets. "
            "Use this to find current information, documentation, tutorials, or answers."
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query.",
                },
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of results (1-10).",
                    "default": 5,
                },
            },
            "required": ["query"],
        },
        "handler": web_search,
        "destructive": False,
    },
]
