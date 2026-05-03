"""
Lilu — Tool Registry
Central registry for all tools. Generates OpenAI function-calling schemas
and dispatches tool calls with an approval gate for destructive actions.
"""

import json
import logging
from typing import Any, Callable

from rich.console import Console
from rich.prompt import Confirm

logger = logging.getLogger("lilu.tools")
console = Console()

# Tools that modify state — require user approval before execution
DESTRUCTIVE_TOOLS = {"write_file", "execute_python", "create_notion_page", "create_calendar_event"}


class ToolRegistry:
    """Manages tool registration, schema generation, and execution."""

    def __init__(self):
        self._tools: dict[str, dict] = {}

    def register(
        self,
        name: str,
        description: str,
        parameters: dict,
        handler: Callable,
        destructive: bool = False,
    ):
        """
        Register a tool.

        Args:
            name: Unique tool name (snake_case).
            description: What the tool does (shown to LLM).
            parameters: JSON Schema for parameters.
            handler: The Python function to execute.
            destructive: If True, requires user approval.
        """
        self._tools[name] = {
            "name": name,
            "description": description,
            "parameters": parameters,
            "handler": handler,
            "destructive": destructive,
        }
        logger.info(f"Tool registered: {name} {'[destructive]' if destructive else ''}")

    def get_schemas(self) -> list[dict]:
        """Generate OpenAI-compatible tool schemas for all registered tools."""
        schemas = []
        for tool in self._tools.values():
            schemas.append({
                "type": "function",
                "function": {
                    "name": tool["name"],
                    "description": tool["description"],
                    "parameters": tool["parameters"],
                },
            })
        return schemas

    def execute(self, name: str, arguments: dict) -> str:
        """
        Execute a tool by name with given arguments.
        Destructive tools require user confirmation.

        Returns:
            Tool result as a string.
        """
        if name not in self._tools:
            return json.dumps({"error": f"Unknown tool: {name}"})

        tool = self._tools[name]

        # ── Approval gate for destructive actions ──
        if tool["destructive"] or name in DESTRUCTIVE_TOOLS:
            console.print(f"\n[bold yellow]⚠ Lilu wants to use:[/] [bold]{name}[/]")
            console.print(f"[dim]Arguments: {json.dumps(arguments, indent=2)}[/]")

            if not Confirm.ask("[yellow]Allow this action?[/]", default=False):
                return json.dumps({"status": "denied", "message": "User denied this action."})

        # ── Execute ──
        try:
            result = tool["handler"](**arguments)
            if isinstance(result, dict):
                return json.dumps(result, indent=2, default=str)
            return str(result)
        except Exception as e:
            logger.error(f"Tool '{name}' failed: {e}")
            return json.dumps({"error": str(e)})

    def list_tools(self) -> list[str]:
        """Return names of all registered tools."""
        return list(self._tools.keys())

    def get_tool_info(self, name: str) -> dict | None:
        """Get info about a specific tool."""
        return self._tools.get(name)
