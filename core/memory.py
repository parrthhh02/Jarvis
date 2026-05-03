"""
Lilu — Memory System
Handles short-term (conversation) and long-term (profile/goals) memory.
"""

import json
import logging
from datetime import datetime
from pathlib import Path

import config

logger = logging.getLogger("lilu.memory")


class MemoryManager:
    """Manages conversation history, user profile, and goals."""

    def __init__(self):
        self.conversation_history: list[dict] = []
        self.session_id: str = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.user_profile: dict = self._load_profile()
        self.goals: list[dict] = self._load_goals()

    # ── User Profile ──────────────────────────────────

    def _load_profile(self) -> dict:
        """Load user profile from disk."""
        if config.USER_PROFILE_PATH.exists():
            try:
                data = json.loads(config.USER_PROFILE_PATH.read_text(encoding="utf-8"))
                logger.info("User profile loaded.")
                return data
            except (json.JSONDecodeError, IOError) as e:
                logger.warning(f"Failed to load profile: {e}")
        return self._default_profile()

    @staticmethod
    def _default_profile() -> dict:
        return {
            "name": "",
            "preferences": [],
            "goals": [],
            "tech_stack": [],
            "notes": [],
            "created_at": datetime.now().isoformat(),
        }

    def save_profile(self):
        """Persist user profile to disk."""
        try:
            config.USER_PROFILE_PATH.write_text(
                json.dumps(self.user_profile, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            logger.info("User profile saved.")
        except IOError as e:
            logger.error(f"Failed to save profile: {e}")

    def update_profile(self, key: str, value) -> str:
        """Update a specific profile field."""
        if key in self.user_profile:
            if isinstance(self.user_profile[key], list):
                if isinstance(value, list):
                    self.user_profile[key].extend(value)
                else:
                    self.user_profile[key].append(value)
            else:
                self.user_profile[key] = value
            self.save_profile()
            return f"Profile updated: {key}"
        return f"Unknown profile field: {key}"

    # ── Goals ─────────────────────────────────────────

    def _load_goals(self) -> list[dict]:
        """Load goals from disk."""
        if config.GOALS_PATH.exists():
            try:
                return json.loads(config.GOALS_PATH.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, IOError):
                pass
        return []

    def save_goals(self):
        """Persist goals to disk."""
        try:
            config.GOALS_PATH.write_text(
                json.dumps(self.goals, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
        except IOError as e:
            logger.error(f"Failed to save goals: {e}")

    def add_goal(self, title: str, steps: list[str] | None = None) -> str:
        """Add a new goal with optional sub-steps."""
        goal = {
            "id": len(self.goals) + 1,
            "title": title,
            "steps": steps or [],
            "status": "active",
            "created_at": datetime.now().isoformat(),
        }
        self.goals.append(goal)
        self.save_goals()
        return f"Goal added: {title}"

    def complete_goal(self, goal_id: int) -> str:
        """Mark a goal as completed."""
        for goal in self.goals:
            if goal["id"] == goal_id:
                goal["status"] = "completed"
                goal["completed_at"] = datetime.now().isoformat()
                self.save_goals()
                return f"Goal completed: {goal['title']}"
        return f"Goal #{goal_id} not found."

    def get_active_goals(self) -> list[dict]:
        """Return all active goals."""
        return [g for g in self.goals if g["status"] == "active"]

    # ── Conversation History ──────────────────────────

    def add_message(self, role: str, content: str, **kwargs):
        """Add a message to conversation history."""
        msg = {"role": role, "content": content, **kwargs}
        self.conversation_history.append(msg)

    def add_raw_message(self, message: dict):
        """Add a pre-formatted message dict to history."""
        self.conversation_history.append(message)

    def get_messages(self, include_system: bool = True, system_prompt: str = "") -> list[dict]:
        """Get conversation history formatted for LLM API calls."""
        messages = []
        if include_system and system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.extend(self.conversation_history)
        return messages

    def get_context_summary(self) -> str:
        """Generate a brief summary of current context for the LLM."""
        parts = []
        if self.user_profile.get("name"):
            parts.append(f"User: {self.user_profile['name']}")
        active = self.get_active_goals()
        if active:
            goals_str = ", ".join(g["title"] for g in active[:3])
            parts.append(f"Active goals: {goals_str}")
        parts.append(f"Messages in session: {len(self.conversation_history)}")
        return " | ".join(parts)

    def save_conversation(self):
        """Save current conversation to disk."""
        if not self.conversation_history:
            return

        filepath = config.CONVERSATIONS_DIR / f"{self.session_id}.json"
        data = {
            "session_id": self.session_id,
            "started_at": self.session_id,
            "message_count": len(self.conversation_history),
            "messages": self.conversation_history,
        }
        try:
            filepath.write_text(
                json.dumps(data, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8",
            )
            logger.info(f"Conversation saved: {filepath.name}")
        except IOError as e:
            logger.error(f"Failed to save conversation: {e}")

    def trim_history(self, max_messages: int = 50):
        """Keep only the most recent messages to manage context window."""
        if len(self.conversation_history) > max_messages:
            self.conversation_history = self.conversation_history[-max_messages:]
            logger.info(f"Trimmed conversation to {max_messages} messages.")
