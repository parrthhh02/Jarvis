"""
Lilu — Notion API Tool (Stub)
Integration with Notion API for note and database management.
Requires Notion integration token to be configured.
"""

import logging

logger = logging.getLogger("lilu.tools.notion")


def search_notion(query: str) -> dict:
    """Search Notion pages and databases."""
    return {
        "status": "not_configured",
        "message": (
            "Notion is not configured yet. "
            "To enable: 1) Create an integration at notion.so/my-integrations, "
            "2) Get the API key, "
            "3) Set NOTION_API_KEY in .env, "
            "4) Share target pages with your integration"
        ),
    }


def create_notion_page(title: str, content: str, database_id: str = "") -> dict:
    """Create a new page in Notion."""
    return {
        "status": "not_configured",
        "message": "Notion is not configured. See search_notion for setup instructions.",
    }


# ── Tool Definitions for Registry ────────────────────

TOOL_DEFINITIONS = [
    {
        "name": "search_notion",
        "description": "Search for pages and content in the user's Notion workspace.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query."},
            },
            "required": ["query"],
        },
        "handler": search_notion,
        "destructive": False,
    },
    {
        "name": "create_notion_page",
        "description": "Create a new page in a Notion database.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Page title."},
                "content": {"type": "string", "description": "Page content in markdown."},
                "database_id": {"type": "string", "description": "Target database ID (uses default if empty)."},
            },
            "required": ["title", "content"],
        },
        "handler": create_notion_page,
        "destructive": True,
    },
]
