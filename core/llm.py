"""
Lilu — LLM Brain
Handles all communication with LLM providers (OpenAI / Groq).
Supports function calling for tool usage.
"""

import json
import logging
from typing import Any

from openai import OpenAI

import config

logger = logging.getLogger("lilu.llm")


class LLMBrain:
    """Unified LLM interface supporting OpenAI and Groq with automatic fallback."""

    def __init__(self):
        self.provider = config.get_active_provider()
        self.client: OpenAI | None = None
        self.model: str = ""
        self._init_client()

    def _init_client(self):
        """Initialize the appropriate API client."""
        if self.provider == "openai":
            self.client = OpenAI(api_key=config.OPENAI_API_KEY)
            self.model = config.PRIMARY_MODEL
            logger.info(f"LLM initialized: OpenAI ({self.model})")

        elif self.provider == "groq":
            self.client = OpenAI(
                api_key=config.GROQ_API_KEY,
                base_url="https://api.groq.com/openai/v1",
            )
            self.model = config.FALLBACK_MODEL
            logger.info(f"LLM initialized: Groq ({self.model})")

        else:
            logger.error("No LLM provider configured.")
            raise RuntimeError("No LLM API key found. Set OPENAI_API_KEY or GROQ_API_KEY in .env")

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> dict:
        """
        Send a chat completion request.

        Args:
            messages: Conversation history in OpenAI format.
            tools: Optional list of tool definitions for function calling.
            temperature: Creativity control (0.0 - 2.0).
            max_tokens: Maximum response length.

        Returns:
            The complete API response message dict.
        """
        kwargs: dict[str, Any] = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }

        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        try:
            response = self.client.chat.completions.create(**kwargs)
            message = response.choices[0].message
            return self._serialize_message(message)

        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            # Attempt fallback if primary fails
            if self.provider == "openai" and config.GROQ_API_KEY:
                logger.info("Falling back to Groq...")
                return self._fallback_chat(messages, temperature, max_tokens)
            raise

    def _fallback_chat(
        self,
        messages: list[dict],
        temperature: float,
        max_tokens: int,
    ) -> dict:
        """Fallback to Groq when OpenAI fails."""
        fallback_client = OpenAI(
            api_key=config.GROQ_API_KEY,
            base_url="https://api.groq.com/openai/v1",
        )
        try:
            response = fallback_client.chat.completions.create(
                model=config.FALLBACK_MODEL,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            message = response.choices[0].message
            return self._serialize_message(message)
        except Exception as e:
            logger.error(f"Fallback also failed: {e}")
            return {
                "role": "assistant",
                "content": "I'm having trouble connecting to my language model right now. Please check your API keys and try again.",
            }

    @staticmethod
    def _serialize_message(message) -> dict:
        """Convert API message object to a clean dict."""
        result = {
            "role": message.role,
            "content": message.content,
        }

        if message.tool_calls:
            result["tool_calls"] = []
            for tc in message.tool_calls:
                result["tool_calls"].append({
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                })

        return result


def parse_tool_args(arguments_str: str) -> dict:
    """Safely parse function call arguments from JSON string."""
    try:
        return json.loads(arguments_str)
    except json.JSONDecodeError:
        logger.error(f"Failed to parse tool arguments: {arguments_str}")
        return {}
