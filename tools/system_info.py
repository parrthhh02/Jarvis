"""
Lilu — System Info Tool
Safe, read-only tool for OS, time, and hardware information.
"""

import platform
import datetime
import os


def get_system_info() -> dict:
    """Get comprehensive system information."""
    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "python_version": platform.python_version(),
        "hostname": platform.node(),
        "cpu_count": os.cpu_count(),
    }


def get_current_time(timezone: str = "local") -> dict:
    """Get the current date and time."""
    now = datetime.datetime.now()
    return {
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%H:%M:%S"),
        "day_of_week": now.strftime("%A"),
        "iso": now.isoformat(),
        "timestamp": now.timestamp(),
    }


# ── Tool Definitions for Registry ────────────────────

TOOL_DEFINITIONS = [
    {
        "name": "get_system_info",
        "description": "Get information about the user's operating system, hardware, and Python version.",
        "parameters": {
            "type": "object",
            "properties": {},
            "required": [],
        },
        "handler": get_system_info,
        "destructive": False,
    },
    {
        "name": "get_current_time",
        "description": "Get the current date, time, and day of the week.",
        "parameters": {
            "type": "object",
            "properties": {
                "timezone": {
                    "type": "string",
                    "description": "Timezone name (currently only 'local' is supported).",
                    "default": "local",
                },
            },
            "required": [],
        },
        "handler": get_current_time,
        "destructive": False,
    },
]
