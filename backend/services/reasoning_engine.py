"""
Synthia 4.2 - Multi-Provider LLM Reasoning Engine

Supports: GLM-4 (ZhipuAI), Anthropic Claude, OpenAI, Google Gemini, Ollama (local).
Automatically falls back through providers if one fails.

The engine handles:
- Multi-turn conversation with system prompt
- Language-aware responses (English, Mexican Spanish, Hindi)
- Streaming support
- Token counting / cost tracking
- Automatic provider fallback
"""

import os
import json
import logging
import httpx
from typing import Optional, AsyncIterator
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class LLMProvider(str, Enum):
    GLM = "glm"
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    GOOGLE = "google"
    OLLAMA = "ollama"


@dataclass
class LLMConfig:
    provider: LLMProvider
    model: str
    api_key: str
    base_url: str
    max_tokens: int = 512
    temperature: float = 0.7
    enabled: bool = True


class ReasoningEngine:
    """
    Multi-provider LLM engine for Synthia's autonomous reasoning.
    
    Priority order:
    1. GLM-4 Plus (ZhipuAI) - when balance available
    2. Anthropic Claude Sonnet 4 - primary fallback
    3. OpenAI GPT-4o - secondary fallback
    4. Google Gemini - tertiary fallback
    5. Ollama (local) - offline fallback
    """

    def __init__(self):
        self._providers: list[LLMConfig] = []
        self._active_provider: Optional[LLMConfig] = None
        self._total_tokens_used = 0
        self._load_providers()

    def _load_providers(self):
        """Load all configured LLM providers from environment."""
        
        # 1. GLM-4 Plus (ZhipuAI)
        glm_key = os.getenv("GLM_API_KEY", "")
        if glm_key:
            self._providers.append(LLMConfig(
                provider=LLMProvider.GLM,
                model="glm-4-plus",
                api_key=glm_key,
                base_url="https://open.bigmodel.cn/api/paas/v4/chat/completions",
                max_tokens=1024,
                temperature=0.7,
            ))
            logger.info("GLM-4 Plus provider loaded")

        # 2. Anthropic Claude (primary - most reliable)
        anthropic_key = os.getenv("ANTHROPIC_API_KEY_2") or os.getenv("ANTHROPIC_API_KEY", "")
        if anthropic_key:
            self._providers.append(LLMConfig(
                provider=LLMProvider.ANTHROPIC,
                model="claude-sonnet-4-20250514",
                api_key=anthropic_key,
                base_url="https://api.anthropic.com/v1/messages",
                max_tokens=1024,
                temperature=0.7,
            ))
            logger.info("Anthropic Claude provider loaded")

        # 3. OpenAI
        openai_key = os.getenv("OPENAI_API_KEY", "")
        if openai_key:
            self._providers.append(LLMConfig(
                provider=LLMProvider.OPENAI,
                model="gpt-4o-mini",
                api_key=openai_key,
                base_url="https://api.openai.com/v1/chat/completions",
                max_tokens=1024,
                temperature=0.7,
            ))
            logger.info("OpenAI provider loaded")

        # 4. Google Gemini
        google_key = os.getenv("GOOGLE_API_KEY", "")
        if google_key:
            self._providers.append(LLMConfig(
                provider=LLMProvider.GOOGLE,
                model="gemini-2.0-flash",
                api_key=google_key,
                base_url="https://generativelanguage.googleapis.com/v1beta",
                max_tokens=1024,
                temperature=0.7,
            ))
            logger.info("Google Gemini provider loaded")

        # 5. Ollama (local)
        ollama_host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self._providers.append(LLMConfig(
            provider=LLMProvider.OLLAMA,
            model=os.getenv("DEFAULT_CODE_MODEL", "qwen2.5-coder"),
            api_key="",
            base_url=f"{ollama_host}/api/chat",
            max_tokens=1024,
            temperature=0.7,
        ))
        logger.info("Ollama local provider loaded")

        if not self._providers:
            logger.error("No LLM providers configured!")

    async def chat(
        self,
        messages: list[dict],
        system_prompt: str = "",
        max_tokens: int = 512,
        temperature: float = 0.7,
        language_hint: str = "en",
    ) -> str:
        """
        Send a chat completion request. Tries providers in priority order.
        
        Args:
            messages: List of {"role": "user"|"assistant", "content": "..."}
            system_prompt: System instructions for the model
            max_tokens: Maximum response tokens
            temperature: Creativity (0.0 = focused, 1.0 = creative)
            language_hint: Expected response language (en, es, hi)
        
        Returns:
            Assistant response text
        """
        # Add language instruction to system prompt
        lang_instruction = {
            "es": " Respond in Mexican Spanish (español de México). Use natural CDMX dialect, not formal Castilian.",
            "hi": " Respond in Hindi (हिंदी). Use Devanagari script naturally.",
            "en": " Respond in English.",
        }.get(language_hint, "")

        full_system = (system_prompt + lang_instruction).strip()

        for provider_config in self._providers:
            if not provider_config.enabled:
                continue
            try:
                result = await self._call_provider(
                    provider_config, messages, full_system, max_tokens, temperature
                )
                if result:
                    self._active_provider = provider_config
                    return result
            except Exception as e:
                logger.warning(
                    "Provider %s failed: %s. Trying next...",
                    provider_config.provider.value, str(e)[:100]
                )
                continue

        return "I'm having trouble connecting to my reasoning engine. Please try again in a moment."

    async def _call_provider(
        self,
        config: LLMConfig,
        messages: list[dict],
        system_prompt: str,
        max_tokens: int,
        temperature: float,
    ) -> Optional[str]:
        """Call a specific LLM provider."""

        if config.provider == LLMProvider.ANTHROPIC:
            return await self._call_anthropic(config, messages, system_prompt, max_tokens, temperature)
        elif config.provider == LLMProvider.GLM:
            return await self._call_glm(config, messages, system_prompt, max_tokens, temperature)
        elif config.provider == LLMProvider.OPENAI:
            return await self._call_openai(config, messages, system_prompt, max_tokens, temperature)
        elif config.provider == LLMProvider.GOOGLE:
            return await self._call_google(config, messages, system_prompt, max_tokens, temperature)
        elif config.provider == LLMProvider.OLLAMA:
            return await self._call_ollama(config, messages, system_prompt, max_tokens, temperature)
        return None

    async def _call_anthropic(self, config, messages, system, max_tokens, temperature) -> str:
        """Call Anthropic Claude API."""
        headers = {
            "x-api-key": config.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        # Anthropic uses 'system' as a top-level param, not in messages
        payload = {
            "model": config.model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [m for m in messages if m["role"] != "system"],
        }
        if system:
            payload["system"] = system

        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(config.base_url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            self._total_tokens_used += data.get("usage", {}).get("output_tokens", 0)
            return data["content"][0]["text"]

    async def _call_glm(self, config, messages, system, max_tokens, temperature) -> str:
        """Call ZhipuAI GLM-4 API (OpenAI-compatible format)."""
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        }
        all_messages = []
        if system:
            all_messages.append({"role": "system", "content": system})
        all_messages.extend(messages)

        payload = {
            "model": config.model,
            "messages": all_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(config.base_url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            self._total_tokens_used += data.get("usage", {}).get("total_tokens", 0)
            return data["choices"][0]["message"]["content"]

    async def _call_openai(self, config, messages, system, max_tokens, temperature) -> str:
        """Call OpenAI API."""
        headers = {
            "Authorization": f"Bearer {config.api_key}",
            "Content-Type": "application/json",
        }
        all_messages = []
        if system:
            all_messages.append({"role": "system", "content": system})
        all_messages.extend(messages)

        payload = {
            "model": config.model,
            "messages": all_messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }

        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(config.base_url, headers=headers, json=payload)
            r.raise_for_status()
            data = r.json()
            return data["choices"][0]["message"]["content"]

    async def _call_google(self, config, messages, system, max_tokens, temperature) -> str:
        """Call Google Gemini API."""
        url = f"{config.base_url}/models/{config.model}:generateContent?key={config.api_key}"
        
        contents = []
        if system:
            contents.append({"role": "user", "parts": [{"text": f"[System instruction] {system}"}]})
            contents.append({"role": "model", "parts": [{"text": "Understood. I will follow these instructions."}]})
        
        for msg in messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})

        payload = {
            "contents": contents,
            "generationConfig": {
                "maxOutputTokens": max_tokens,
                "temperature": temperature,
            }
        }

        async with httpx.AsyncClient(timeout=30) as client:
            r = await client.post(url, json=payload)
            r.raise_for_status()
            data = r.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]

    async def _call_ollama(self, config, messages, system, max_tokens, temperature) -> str:
        """Call local Ollama instance."""
        all_messages = []
        if system:
            all_messages.append({"role": "system", "content": system})
        all_messages.extend(messages)

        payload = {
            "model": config.model,
            "messages": all_messages,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
            }
        }

        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(config.base_url, json=payload)
            r.raise_for_status()
            data = r.json()
            return data["message"]["content"]

    @property
    def active_provider_name(self) -> str:
        if self._active_provider:
            return f"{self._active_provider.provider.value}/{self._active_provider.model}"
        return "none"

    @property
    def total_tokens(self) -> int:
        return self._total_tokens_used


# Singleton
_engine: Optional[ReasoningEngine] = None


def get_reasoning_engine() -> ReasoningEngine:
    global _engine
    if _engine is None:
        _engine = ReasoningEngine()
    return _engine


__all__ = ["ReasoningEngine", "get_reasoning_engine", "LLMProvider"]
