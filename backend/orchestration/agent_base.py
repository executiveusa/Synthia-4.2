"""
Synthia 4.2 - Agent Base Class

Each agent wraps an LLM call (Ollama local or cloud fallback)
with a specialized system prompt and structured output parsing.
"""

import os
import json
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

# Try Ollama first, fall back gracefully
try:
    import ollama as _ollama
    _ollama_available = True
except ImportError:
    _ollama_available = False


class AgentBase:
    """Base class for all orchestration agents."""

    name: str = "base_agent"
    role: str = "generic"
    system_prompt: str = "You are a helpful AI assistant."
    model: str = ""

    def __init__(self):
        self.model = os.getenv("DEFAULT_CODE_MODEL", "qwen2.5-coder")
        self.max_retries = 2

    async def execute(self, context: dict) -> dict:
        """
        Execute this agent's task given accumulated pipeline context.
        Returns result dict to be merged into context for next agent.
        """
        for attempt in range(self.max_retries + 1):
            try:
                result = await self._call_llm(context)
                return {
                    "agent": self.name,
                    "role": self.role,
                    "status": "success",
                    "output": result,
                }
            except Exception as e:
                logger.warning(
                    "Agent %s attempt %d failed: %s", self.name, attempt + 1, e
                )
                if attempt == self.max_retries:
                    return {
                        "agent": self.name,
                        "role": self.role,
                        "status": "error",
                        "error": str(e),
                    }

        return {"agent": self.name, "status": "error", "error": "max retries exceeded"}

    async def _call_llm(self, context: dict) -> str:
        """Call the LLM with system prompt + serialized context."""
        user_message = self._build_user_message(context)

        if _ollama_available:
            response = _ollama.chat(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message},
                ],
            )
            return response["message"]["content"]
        else:
            # Fallback: return a structured placeholder
            logger.warning("Ollama not available, returning placeholder for %s", self.name)
            return f"[{self.name}] Processed context with {len(context)} keys. Ollama unavailable for execution."

    def _build_user_message(self, context: dict) -> str:
        """Serialize context into a prompt-friendly string."""
        parts = []
        for key, value in context.items():
            if isinstance(value, dict):
                parts.append(f"## {key}\n{json.dumps(value, indent=2, default=str)}")
            elif isinstance(value, list):
                parts.append(f"## {key}\n{json.dumps(value, indent=2, default=str)}")
            else:
                parts.append(f"## {key}\n{value}")
        return "\n\n".join(parts)


__all__ = ["AgentBase"]
