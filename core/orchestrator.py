"""
Lilu — Orchestrator
The central loop that connects the LLM, memory, tools, and I/O.
"""

import json
import logging
from typing import Callable

from rich.console import Console
from rich.markdown import Markdown

import config
from core.llm import LLMBrain, parse_tool_args
from core.memory import MemoryManager
from core.prompt import get_system_prompt
from tools.registry import ToolRegistry

# Import tools to register them
from tools import system_info, file_ops, python_exec, web_search, google_calendar, notion_api

logger = logging.getLogger("lilu.orchestrator")
console = Console()


class Orchestrator:
    """Manages the conversation flow and tool execution."""

    def __init__(self):
        self.brain = LLMBrain()
        self.memory = MemoryManager()
        self.registry = ToolRegistry()
        self._register_tools()

    def _register_tools(self):
        """Register all available tools."""
        modules = [
            system_info,
            file_ops,
            python_exec,
            web_search,
            google_calendar,
            notion_api,
        ]
        
        for module in modules:
            if hasattr(module, "TOOL_DEFINITIONS"):
                for t in module.TOOL_DEFINITIONS:
                    self.registry.register(
                        name=t["name"],
                        description=t["description"],
                        parameters=t["parameters"],
                        handler=t["handler"],
                        destructive=t.get("destructive", False),
                    )

    def process_input(self, text_input: str, on_chunk: Callable[[str], None] | None = None) -> str:
        """
        Process a user input, handle tool calls if needed, and return the final response.
        """
        # 1. Add user message to memory
        self.memory.add_message("user", text_input)

        # 2. Prepare context
        system_prompt = get_system_prompt(self.memory.user_profile)
        messages = self.memory.get_messages(system_prompt=system_prompt)
        tools_schema = self.registry.get_schemas()

        while True:
            # 3. Call LLM
            logger.info("Calling LLM...")
            response_msg = self.brain.chat(messages=messages, tools=tools_schema)
            self.memory.add_raw_message(response_msg)
            messages.append(response_msg)

            # 4. Check for tool calls
            if "tool_calls" in response_msg and response_msg["tool_calls"]:
                for tool_call in response_msg["tool_calls"]:
                    fn_name = tool_call["function"]["name"]
                    args_str = tool_call["function"]["arguments"]
                    args_dict = parse_tool_args(args_str)

                    logger.info(f"LLM requested tool: {fn_name}")
                    
                    # 5. Execute tool (with approval gate inside registry)
                    result = self.registry.execute(fn_name, args_dict)
                    
                    # 6. Append tool result to messages and loop
                    tool_msg = {
                        "role": "tool",
                        "tool_call_id": tool_call["id"],
                        "name": fn_name,
                        "content": result,
                    }
                    self.memory.add_raw_message(tool_msg)
                    messages.append(tool_msg)
                
                # Loop back to let LLM read tool results and answer
                continue
            
            # 7. No tool calls -> final response
            final_content = response_msg.get("content", "")
            
            # 8. Housekeeping
            self.memory.trim_history()
            if config.MEMORY_ENABLED:
                self.memory.save_conversation()
                
            return final_content
