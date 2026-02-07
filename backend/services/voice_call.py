"""
Synthia 4.2 - Voice Call Manager

State machine for voice calls:
  ringing → connected → discussing → hangup → triggering_agents

On hangup, extracts a structured brief from the conversation
and dispatches the agent orchestration pipeline.
"""

import logging
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

logger = logging.getLogger(__name__)


class CallState(str, Enum):
    RINGING = "ringing"
    CONNECTED = "connected"
    DISCUSSING = "discussing"
    HANGUP = "hangup"
    TRIGGERING = "triggering_agents"
    COMPLETE = "complete"


@dataclass
class ConversationContext:
    """Tracks what was discussed during the call."""
    niche: str = ""
    page_type: str = "landing"
    preferences: list[str] = field(default_factory=list)
    patterns_discussed: list[str] = field(default_factory=list)
    client_notes: list[str] = field(default_factory=list)
    messages: list[dict] = field(default_factory=list)

    def to_brief(self) -> str:
        """Convert conversation into an agent pipeline brief."""
        parts = []
        if self.niche:
            parts.append(f"Niche: {self.niche}")
        if self.page_type:
            parts.append(f"Page type: {self.page_type}")
        if self.preferences:
            parts.append(f"Preferences: {', '.join(self.preferences)}")
        if self.patterns_discussed:
            parts.append(f"Patterns: {', '.join(self.patterns_discussed)}")
        if self.client_notes:
            parts.append(f"Notes: {'; '.join(self.client_notes)}")

        # Include last few conversation turns for context
        recent = self.messages[-6:]
        if recent:
            parts.append("Recent conversation:")
            for msg in recent:
                role = msg.get("role", "user")
                text = msg.get("content", "")[:200]
                parts.append(f"  {role}: {text}")

        return "\n".join(parts)


class VoiceCallManager:
    """
    Manages a single voice call session.
    Bridges Twilio audio ↔ Whisper STT ↔ Ollama chat ↔ ElevenLabs TTS.
    """

    def __init__(self, call_sid: str = ""):
        self.call_sid = call_sid
        self.state = CallState.RINGING
        self.context = ConversationContext()
        self._voice_service = None
        self._system_prompt = (
            "You are Synthia, an AI design assistant from The Pauli Effect agency in Mexico City. "
            "You're on a phone call with a client discussing their website project. "
            "Be warm, professional, and efficient. Ask about their business niche, "
            "what kind of page they need, preferred style, and any specific features. "
            "Suggest Awwwards-quality design patterns that fit their niche. "
            "Keep responses concise (2-3 sentences) since this is a voice call. "
            "Speak naturally, use casual professional tone."
        )
        self._chat_history: list[dict] = [
            {"role": "system", "content": self._system_prompt}
        ]

    def _get_voice_service(self):
        if self._voice_service is None:
            from services.voice import get_voice_service
            self._voice_service = get_voice_service()
        return self._voice_service

    async def on_connect(self) -> bytes:
        """Handle call connection. Returns greeting audio bytes."""
        self.state = CallState.CONNECTED
        greeting = (
            "Hi! This is Synthia from The Pauli Effect. "
            "I'm your design assistant. Let's talk about your project. "
            "What kind of website are you building?"
        )
        self.context.messages.append({"role": "assistant", "content": greeting})
        self._chat_history.append({"role": "assistant", "content": greeting})

        try:
            vs = self._get_voice_service()
            audio = await vs.synthesize(greeting)
            self.state = CallState.DISCUSSING
            return audio
        except Exception as e:
            logger.error("TTS failed on greeting: %s", e)
            self.state = CallState.DISCUSSING
            return b""

    async def on_audio_received(self, audio_bytes: bytes) -> bytes:
        """
        Process incoming audio from user.
        Transcribe → Generate response → Synthesize response audio.
        Returns response audio bytes.
        """
        vs = self._get_voice_service()

        # 1. Transcribe user audio
        try:
            user_text = await vs.transcribe(audio_bytes)
        except Exception as e:
            logger.error("STT failed: %s", e)
            return b""

        if not user_text.strip():
            return b""

        logger.info("User said: %s", user_text[:100])
        self.context.messages.append({"role": "user", "content": user_text})
        self._chat_history.append({"role": "user", "content": user_text})

        # 2. Extract intent/info from user's words
        self._extract_context(user_text)

        # 3. Generate response via LLM
        try:
            import ollama
            response = ollama.chat(
                model="qwen2.5-coder",
                messages=self._chat_history,
            )
            assistant_text = response["message"]["content"]
        except Exception as e:
            logger.error("LLM response failed: %s", e)
            assistant_text = "I understand. Can you tell me more about what you're looking for?"

        self.context.messages.append({"role": "assistant", "content": assistant_text})
        self._chat_history.append({"role": "assistant", "content": assistant_text})

        # 4. Synthesize response
        try:
            audio = await vs.synthesize(assistant_text)
            return audio
        except Exception as e:
            logger.error("TTS failed: %s", e)
            return b""

    async def on_hangup(self) -> Optional[str]:
        """
        Handle call hangup.
        Extracts brief from conversation and dispatches agent pipeline.
        Returns job_id if pipeline was started, None otherwise.
        """
        self.state = CallState.HANGUP
        logger.info("Call %s ended. Extracting brief and dispatching agents.", self.call_sid)

        brief = self.context.to_brief()

        if not brief.strip():
            logger.warning("Empty brief from call %s, skipping pipeline", self.call_sid)
            self.state = CallState.COMPLETE
            return None

        # Dispatch pipeline
        self.state = CallState.TRIGGERING
        try:
            from orchestration.state import JobState, JobStore
            job = JobState.create(
                brief=brief,
                niche=self.context.niche or "saas",
                page_type=self.context.page_type or "landing",
            )
            store = JobStore()
            store.save(job)

            # Dispatch to Celery
            try:
                from tasks import run_pipeline
                run_pipeline.delay(job.job_id)
            except Exception:
                logger.warning("Celery unavailable, pipeline queued but not started")

            self.state = CallState.COMPLETE
            logger.info("Pipeline %s dispatched from call %s", job.job_id, self.call_sid)
            return job.job_id

        except Exception as e:
            logger.error("Failed to dispatch pipeline from call: %s", e)
            self.state = CallState.COMPLETE
            return None

    def _extract_context(self, text: str) -> None:
        """Extract niche, page type, and preferences from user speech."""
        text_lower = text.lower()

        # Niche detection
        niche_keywords = {
            "saas": ["saas", "software", "app", "platform", "tool"],
            "ecommerce": ["shop", "store", "ecommerce", "e-commerce", "products", "sell"],
            "portfolio": ["portfolio", "personal", "freelance", "my work"],
            "agency": ["agency", "studio", "firm", "company"],
            "restaurant": ["restaurant", "food", "menu", "cafe", "bar"],
            "fashion": ["fashion", "clothing", "brand", "apparel"],
            "tech": ["tech", "startup", "ai", "machine learning"],
            "medical": ["medical", "health", "clinic", "doctor"],
            "legal": ["law", "legal", "attorney", "lawyer"],
        }
        for niche, keywords in niche_keywords.items():
            if any(kw in text_lower for kw in keywords):
                self.context.niche = niche
                break

        # Page type detection
        page_keywords = {
            "landing": ["landing", "home", "main page", "front page"],
            "product": ["product", "feature", "pricing"],
            "about": ["about", "team", "who we are"],
            "blog": ["blog", "content", "articles"],
            "contact": ["contact", "get in touch"],
        }
        for page_type, keywords in page_keywords.items():
            if any(kw in text_lower for kw in keywords):
                self.context.page_type = page_type
                break

        # Pattern preferences
        pattern_keywords = {
            "animations": "scroll-pin-section",
            "video hero": "video-hero-transition",
            "parallax": "parallax-depth-layers",
            "bento": "bento-tilt-grid",
            "clip path": "clip-path-hero-reveal",
            "3d": "parallax-depth-layers",
        }
        for keyword, pattern in pattern_keywords.items():
            if keyword in text_lower and pattern not in self.context.patterns_discussed:
                self.context.patterns_discussed.append(pattern)

        # General notes
        if len(text) > 20:
            self.context.client_notes.append(text[:200])


__all__ = ["VoiceCallManager", "CallState", "ConversationContext"]
