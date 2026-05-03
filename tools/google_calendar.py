"""
Lilu — Google Calendar Tool (Stub)
Integration with Google Calendar API.
Requires OAuth2 credentials to be configured.
"""

import logging

logger = logging.getLogger("lilu.tools.calendar")


def list_upcoming_events(max_results: int = 5) -> dict:
    """List upcoming calendar events."""
    # This is a placeholder — requires Google API credentials setup
    return {
        "status": "not_configured",
        "message": (
            "Google Calendar is not configured yet. "
            "To enable: 1) Create OAuth2 credentials in Google Cloud Console, "
            "2) Download credentials.json, "
            "3) Set GOOGLE_CREDENTIALS_PATH in .env"
        ),
    }


def create_calendar_event(
    title: str,
    start_time: str,
    end_time: str,
    description: str = "",
) -> dict:
    """Create a new calendar event."""
    return {
        "status": "not_configured",
        "message": "Google Calendar is not configured. See list_upcoming_events for setup instructions.",
    }


# ── Tool Definitions for Registry ────────────────────

TOOL_DEFINITIONS = [
    {
        "name": "list_upcoming_events",
        "description": "List upcoming events from Google Calendar. Requires Google API credentials to be configured.",
        "parameters": {
            "type": "object",
            "properties": {
                "max_results": {
                    "type": "integer",
                    "description": "Maximum number of events to return.",
                    "default": 5,
                },
            },
            "required": [],
        },
        "handler": list_upcoming_events,
        "destructive": False,
    },
    {
        "name": "create_calendar_event",
        "description": "Create a new event in Google Calendar. Requires Google API credentials.",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "description": "Event title."},
                "start_time": {"type": "string", "description": "Start time in ISO format."},
                "end_time": {"type": "string", "description": "End time in ISO format."},
                "description": {"type": "string", "description": "Event description.", "default": ""},
            },
            "required": ["title", "start_time", "end_time"],
        },
        "handler": create_calendar_event,
        "destructive": True,
    },
]
