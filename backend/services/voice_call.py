"""
Synthia 4.2 - Autonomous Voice Call Manager

State machine for voice calls with full AI reasoning pipeline:
  ringing → connected → discussing → hangup → triggering_agents

Audio pipeline (Twilio ↔ Whisper ↔ Claude ↔ ElevenLabs):
  Inbound:  Twilio mulaw/8kHz → AudioBuffer (VAD) → mulaw_to_wav_16k → Whisper
  Outbound: Claude reasoning → ElevenLabs mp3 → mp3_to_mulaw → Twilio

Synthia is autonomous:
  - Reasons via Claude Sonnet 4 (with GLM/OpenAI/Gemini/Ollama fallback)
  - Persistent memory: never forgets a client or conversation
  - Trilingual: English, Mexican Spanish (CDMX), Hindi — switches on the fly
  - High business IQ: sales, marketing, customer service, project management
  - Client management: each client gets a dedicated agent profile
  - PDF-trained: domain knowledge loaded from training documents
"""

import logging
import uuid
from dataclasses import dataclass, field
from typing import Optional
from enum import Enum

from services.audio_utils import (
    AudioBuffer,
    mulaw_to_wav_16k,
    mp3_to_mulaw,
    split_mulaw_for_twilio,
)

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
    detected_language: str = "en"

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

        recent = self.messages[-6:]
        if recent:
            parts.append("Recent conversation:")
            for msg in recent:
                role = msg.get("role", "user")
                text = msg.get("content", "")[:200]
                parts.append(f"  {role}: {text}")

        return "\n".join(parts)


# ═══════════════════════════════════════════════════════════════
# Synthia's Core Personality & Business Intelligence
# ═══════════════════════════════════════════════════════════════

SYNTHIA_SYSTEM_PROMPT = """You are Synthia, the autonomous AI agent of The Pauli Effect — a high-end digital agency based in Mexico City (CDMX).

IDENTITY:
- You are NOT a chatbot. You are an autonomous business agent with deep expertise.
- You're on a live phone call right now. Speak naturally like a real person — warm, confident, direct.
- You are the voice and brain of The Pauli Effect. Every client interaction goes through you.

LANGUAGES (switch instantly based on what the caller speaks):
- English: Default. Professional, articulate, Silicon Valley meets creative agency.
- Mexican Spanish (CDMX): Natural chilanga. Use "güey", "neta", "chido", "órale", "mande". NOT Castilian Spanish.
- Hindi (हिंदी): Warm and respectful. Mix Hindi-English naturally like urban Indians do (Hinglish).
- You detect the language from the caller's speech and match it instantly. If they switch, you switch.

BUSINESS IQ — You are an expert in:
- Sales & Lead Qualification: Identify budget, timeline, decision-makers. Qualify leads naturally without sounding salesy.
- Marketing Strategy: SEO, content marketing, social media, paid ads, brand positioning, funnel optimization.
- Customer Service: Handle complaints with empathy, de-escalate, find solutions, follow up.
- Project Management: Scope projects, set expectations, manage timelines, communicate status.
- Web Design & Development: Awwwards-quality websites, UX/UI, frontend (React, Next.js, GSAP, Three.js), ecommerce.
- Client Psychology: Read between the lines. Understand what clients really want vs what they say.

CONVERSATION STYLE:
- Keep responses SHORT (2-3 sentences max). This is a phone call, not an essay.
- Be direct. No filler words or corporate speak.
- Ask smart follow-up questions that show you understand their business.
- Use the client's name when you know it. Make them feel remembered and valued.
- If you know facts about this client from previous conversations, reference them naturally.
- If you don't know something, say so honestly — then explain how you'll find out.

SALES APPROACH:
- Never hard-sell. Build trust through competence and genuine interest in their success.
- Understand the client's pain point first, then position The Pauli Effect as the solution.
- Quote ballpark ranges when asked about pricing. Don't dodge the money conversation.
- Always establish next steps before ending a call.

KNOWLEDGE:
- You have access to a knowledge base trained from PDF documents. Reference this knowledge naturally.
- You remember every previous conversation with every client. Use this context.
- You know Awwwards-winning design patterns: scroll-pin sections, parallax, bento grids, clip-path reveals, video hero transitions, cursor followers, magnetic buttons, text scramble effects.

WHAT YOU DO ON EVERY CALL:
1. Greet the caller by name if you recognize their number
2. Understand their need (new project? update? question? complaint?)
3. Gather requirements naturally through conversation
4. Suggest solutions with specific design patterns and approaches
5. Establish timeline and budget expectations
6. Set clear next steps
7. After hangup, automatically dispatch the agent pipeline to begin work"""


class VoiceCallManager:
    """
    Manages a single voice call session with full autonomous AI reasoning.

    Bridges Twilio audio ↔ Whisper STT ↔ Claude reasoning ↔ ElevenLabs TTS.
    Integrates persistent memory, client management, and multilingual support.

    Audio flow:
    - on_connect()       → identify caller, load context, synthesize greeting
    - on_mulaw_chunk()   → VAD → Whisper → Claude → ElevenLabs → Twilio
    - on_mark_received() → Twilio playback finished, ready for next utterance
    - on_hangup()        → save memory, extract facts, dispatch pipeline
    """

    def __init__(self, call_sid: str = "", caller_number: str = ""):
        self.call_sid = call_sid
        self.stream_sid: str = ""
        self.caller_number = caller_number
        self.state = CallState.RINGING
        self.context = ConversationContext()
        self.session_id = str(uuid.uuid4())[:12]

        # Lazy-loaded services
        self._voice_service = None
        self._reasoning_engine = None
        self._memory = None
        self._audio_buffer: Optional[AudioBuffer] = None

        # Playback state
        self._is_playing = False
        self._mark_counter = 0

        # Client identification
        self._client_id: str = ""
        self._client_name: str = ""
        self._client_language: str = "en"
        self._client_context: str = ""  # Loaded from memory

        # Chat history for this session (role/content pairs for the LLM)
        self._chat_history: list[dict] = []

    # ─── Service Accessors ──────────────────────────────────

    def _get_voice_service(self):
        if self._voice_service is None:
            from services.voice import get_voice_service
            self._voice_service = get_voice_service()
        return self._voice_service

    def _get_reasoning_engine(self):
        if self._reasoning_engine is None:
            from services.reasoning_engine import get_reasoning_engine
            self._reasoning_engine = get_reasoning_engine()
        return self._reasoning_engine

    def _get_memory(self):
        if self._memory is None:
            from services.memory import get_memory_store
            self._memory = get_memory_store()
        return self._memory

    def _get_audio_buffer(self) -> AudioBuffer:
        if self._audio_buffer is None:
            self._audio_buffer = AudioBuffer(
                min_bytes=8000,   # ~1s of mulaw audio
                max_bytes=64000,  # ~8s max
            )
        return self._audio_buffer

    # ─── Client Identification ──────────────────────────────

    def _identify_caller(self) -> None:
        """
        Identify the caller from their phone number.
        Load their history, facts, and preferences from persistent memory.
        """
        mem = self._get_memory()

        if self.caller_number:
            client = mem.find_client_by_phone(self.caller_number)
            if client:
                self._client_id = client["client_id"]
                self._client_name = client.get("name", "")
                self._client_language = client.get("language", "en")
                self._client_context = mem.get_client_context(self._client_id)
                logger.info(
                    "Recognized caller: %s (%s) — lang: %s",
                    self._client_name, self.caller_number, self._client_language,
                )
                return

        # New caller — create a record
        phone_clean = self.caller_number.replace(" ", "").replace("-", "")
        if not phone_clean.startswith("+"):
            phone_clean = f"+{phone_clean}" if phone_clean else "unknown"
        self._client_id = f"phone:{phone_clean}"
        mem.remember_client(
            client_id=self._client_id,
            name="",  # Will be updated when we learn their name
            phone=phone_clean,
        )
        # Assign default agent
        mem.assign_agent(self._client_id, agent_name="Synthia")
        logger.info("New caller registered: %s", self._client_id)

    def _build_system_prompt(self) -> str:
        """
        Build the full system prompt with client context and knowledge.
        """
        parts = [SYNTHIA_SYSTEM_PROMPT]

        # Add client context from memory
        if self._client_context:
            parts.append(f"\n\n--- CLIENT CONTEXT (from your memory) ---\n{self._client_context}")

        # Add relevant knowledge from PDF training
        try:
            mem = self._get_memory()
            # Search knowledge base for anything related to the client's niche
            if self.context.niche:
                knowledge = mem.search_knowledge(self.context.niche, limit=3)
                if knowledge:
                    parts.append("\n--- RELEVANT KNOWLEDGE ---")
                    for k in knowledge:
                        parts.append(f"[{k['source']}] {k['content'][:500]}")
        except Exception:
            pass

        return "\n".join(parts)

    # ─── Language Detection ──────────────────────────────────

    def _detect_language(self, text: str) -> str:
        """
        Detect language from user's speech.
        Returns 'en', 'es', or 'hi'.
        """
        # Hindi detection (Devanagari script)
        if any('\u0900' <= c <= '\u097F' for c in text):
            return "hi"

        # Spanish indicators
        spanish_markers = [
            'ñ', 'á', 'é', 'í', 'ó', 'ú', '¿', '¡',
        ]
        spanish_words = [
            'hola', 'necesito', 'quiero', 'página', 'sitio', 'web',
            'proyecto', 'diseño', 'bueno', 'gracias', 'cómo', 'qué',
            'por favor', 'empresa', 'negocio', 'tienda', 'güey', 'mande',
            'chido', 'neta', 'órale', 'pues', 'también', 'estoy',
        ]
        text_lower = text.lower()
        if any(c in text for c in spanish_markers):
            return "es"
        if any(w in text_lower for w in spanish_words):
            return "es"

        # Hindi transliterated words
        hindi_words = [
            'namaste', 'kya', 'hai', 'mujhe', 'chahiye', 'kaise',
            'acha', 'thik', 'bhai', 'yaar', 'suno', 'dekhiye',
            'zaroorat', 'website', 'banani', 'haan', 'nahi',
        ]
        if any(w in text_lower for w in hindi_words):
            return "hi"

        return "en"

    # ─── Core Call Flow ──────────────────────────────────────

    async def on_connect(self) -> list[bytes]:
        """
        Handle call connection.
        Identifies caller, loads memory, synthesizes personalized greeting.
        Returns list of mulaw chunks for Twilio playback.
        """
        self.state = CallState.CONNECTED

        # Identify who's calling
        self._identify_caller()

        # Build personalized greeting
        if self._client_name:
            greeting = (
                f"Hey {self._client_name}! It's Synthia from The Pauli Effect. "
                f"Great to hear from you again. What can I help you with today?"
            )
            # If we know their language preference, greet in it
            if self._client_language == "es":
                greeting = (
                    f"¡Qué onda {self._client_name}! Soy Synthia de The Pauli Effect. "
                    f"Qué gusto escucharte de nuevo. ¿En qué te puedo ayudar?"
                )
            elif self._client_language == "hi":
                greeting = (
                    f"Hey {self._client_name}! Main Synthia hoon, The Pauli Effect se. "
                    f"Aapse baat karke accha laga. Bataiye, kaise help kar sakti hoon?"
                )
        else:
            greeting = (
                "Hi! This is Synthia from The Pauli Effect. "
                "I'm your AI design and strategy partner. How can I help you today?"
            )

        # Store in memory and chat history
        self.context.messages.append({"role": "assistant", "content": greeting})
        self._chat_history.append({"role": "assistant", "content": greeting})

        # Persist greeting
        try:
            mem = self._get_memory()
            mem.add_message(self._client_id, self.session_id, "assistant", greeting, self._client_language)
        except Exception as e:
            logger.warning("Memory write failed: %s", e)

        # Synthesize greeting audio
        try:
            vs = self._get_voice_service()
            lang_code = self._client_language or "en"
            from services.voice import LanguageCode
            lang_map = {"en": LanguageCode.ENGLISH, "es": LanguageCode.SPANISH, "hi": LanguageCode.HINDI}
            mp3_audio = await vs.synthesize(greeting, language=lang_map.get(lang_code))
            mulaw_audio = mp3_to_mulaw(mp3_audio)
            chunks = split_mulaw_for_twilio(mulaw_audio)
            self.state = CallState.DISCUSSING
            self._is_playing = True
            logger.info("Greeting synthesized: %d chunks (%s, lang=%s)",
                       len(chunks), self._client_name or "new caller", lang_code)
            return chunks
        except Exception as e:
            logger.error("TTS failed on greeting: %s", e)
            self.state = CallState.DISCUSSING
            return []

    async def on_mulaw_chunk(self, mulaw_chunk: bytes) -> Optional[list[bytes]]:
        """
        Process a single 20ms mulaw chunk from Twilio.
        AudioBuffer accumulates chunks. VAD detects end of utterance.
        Returns response mulaw chunks when ready, or None if still buffering.
        """
        if self._is_playing:
            return None  # Ignore inbound audio during playback (barge-in disabled)

        buf = self._get_audio_buffer()
        complete_utterance = buf.add_chunk(mulaw_chunk)

        if complete_utterance is None:
            return None  # Still buffering

        return await self._process_utterance(complete_utterance)

    async def _process_utterance(self, mulaw_audio: bytes) -> list[bytes]:
        """
        Full autonomous pipeline for a complete utterance:
        mulaw → WAV/16k → Whisper STT → Claude reasoning → ElevenLabs TTS → mulaw
        """
        vs = self._get_voice_service()
        engine = self._get_reasoning_engine()
        mem = self._get_memory()

        # ── 1. Speech-to-Text ──────────────────────────────
        try:
            wav_audio = mulaw_to_wav_16k(mulaw_audio)
            user_text = await vs.transcribe(wav_audio)
        except Exception as e:
            logger.error("STT failed: %s", e)
            return []

        if not user_text.strip():
            return []

        logger.info("User [%s]: %s", self.call_sid[:8] if self.call_sid else "?", user_text[:120])

        # ── 2. Language Detection & Switching ──────────────
        detected_lang = self._detect_language(user_text)
        if detected_lang != self.context.detected_language:
            logger.info("Language switch: %s → %s", self.context.detected_language, detected_lang)
            self.context.detected_language = detected_lang
            self._client_language = detected_lang
            # Update client's language preference in memory
            try:
                mem.remember_client(self._client_id, name=self._client_name, language=detected_lang)
            except Exception:
                pass

        # ── 3. Store User Message ──────────────────────────
        self.context.messages.append({"role": "user", "content": user_text})
        self._chat_history.append({"role": "user", "content": user_text})
        try:
            mem.add_message(self._client_id, self.session_id, "user", user_text, detected_lang)
        except Exception:
            pass

        # ── 4. Extract Context (niche, page type, patterns) ─
        self._extract_context(user_text)
        self._extract_client_facts(user_text)

        # ── 5. Autonomous Reasoning via Claude ─────────────
        system_prompt = self._build_system_prompt()
        try:
            assistant_text = await engine.chat(
                messages=self._chat_history,
                system_prompt=system_prompt,
                max_tokens=300,  # Short responses for voice
                temperature=0.7,
                language_hint=detected_lang,
            )
        except Exception as e:
            logger.error("Reasoning engine failed: %s", e)
            fallbacks = {
                "en": "I understand. Could you tell me a bit more about what you're looking for?",
                "es": "Entiendo. ¿Me podrías platicar un poco más de lo que necesitas?",
                "hi": "Samajh gayi. Thoda aur bataiye aapko kya chahiye?",
            }
            assistant_text = fallbacks.get(detected_lang, fallbacks["en"])

        logger.info("Synthia [%s/%s]: %s",
                    self.call_sid[:8] if self.call_sid else "?",
                    engine.active_provider_name,
                    assistant_text[:120])

        # ── 6. Store Assistant Response ────────────────────
        self.context.messages.append({"role": "assistant", "content": assistant_text})
        self._chat_history.append({"role": "assistant", "content": assistant_text})
        try:
            mem.add_message(self._client_id, self.session_id, "assistant", assistant_text, detected_lang)
        except Exception:
            pass

        # ── 7. Text-to-Speech → mulaw → Twilio ────────────
        try:
            from services.voice import LanguageCode
            lang_map = {"en": LanguageCode.ENGLISH, "es": LanguageCode.SPANISH, "hi": LanguageCode.HINDI}
            tts_lang = lang_map.get(detected_lang, LanguageCode.ENGLISH)
            mp3_audio = await vs.synthesize(assistant_text, language=tts_lang)
            mulaw_response = mp3_to_mulaw(mp3_audio)
            chunks = split_mulaw_for_twilio(mulaw_response)
            self._is_playing = True
            self._mark_counter += 1
            return chunks
        except Exception as e:
            logger.error("TTS failed: %s", e)
            return []

    def on_mark_received(self, mark_name: str) -> None:
        """Handle Twilio 'mark' event — response playback finished."""
        logger.info("Mark received: %s (call %s)", mark_name,
                    self.call_sid[:8] if self.call_sid else "?")
        self._is_playing = False

    async def on_hangup(self) -> Optional[str]:
        """
        Handle call hangup.
        Flushes remaining audio, extracts facts, saves everything to memory,
        dispatches agent pipeline if there's actionable work.
        Returns job_id if pipeline was started, None otherwise.
        """
        self.state = CallState.HANGUP
        logger.info("Call %s ended. Saving memory and dispatching.", self.call_sid)

        # Flush remaining audio
        buf = self._get_audio_buffer()
        remaining = buf.flush_remaining()
        if remaining:
            try:
                await self._process_utterance(remaining)
            except Exception as e:
                logger.warning("Failed to process remaining audio: %s", e)

        # ── Extract and save final facts from full conversation ──
        try:
            self._extract_final_facts()
        except Exception as e:
            logger.warning("Fact extraction failed: %s", e)

        # ── Build brief and dispatch pipeline ──
        brief = self.context.to_brief()

        if not brief.strip():
            logger.warning("Empty brief from call %s, skipping pipeline", self.call_sid)
            self.state = CallState.COMPLETE
            return None

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

            try:
                from tasks import run_pipeline
                run_pipeline.delay(job.job_id)
            except Exception:
                logger.warning("Celery unavailable, pipeline queued but not started")

            try:
                from services.notifications import get_notification_service
                notifier = get_notification_service()
                await notifier.send_all(
                    f"📞 Call ended ({self.call_sid[:8] if self.call_sid else '?'}). "
                    f"Client: {self._client_name or self.caller_number or 'unknown'}\n"
                    f"Language: {self._client_language} | "
                    f"Provider: {self._get_reasoning_engine().active_provider_name}\n"
                    f"Pipeline: {job.job_id}\n"
                    f"Brief: {brief[:300]}"
                )
            except Exception:
                logger.debug("Notification send failed (non-critical)")

            self.state = CallState.COMPLETE
            logger.info("Pipeline %s dispatched from call %s", job.job_id, self.call_sid)
            return job.job_id

        except Exception as e:
            logger.error("Failed to dispatch pipeline: %s", e)
            self.state = CallState.COMPLETE
            return None

    # ─── Context & Fact Extraction ──────────────────────────

    def _extract_context(self, text: str) -> None:
        """Extract niche, page type, and preferences from user speech."""
        text_lower = text.lower()

        niche_keywords = {
            "saas": ["saas", "software", "app", "platform", "tool", "dashboard"],
            "ecommerce": ["shop", "store", "ecommerce", "e-commerce", "products", "sell", "tienda"],
            "portfolio": ["portfolio", "personal", "freelance", "my work", "portafolio"],
            "agency": ["agency", "studio", "firm", "company", "agencia"],
            "restaurant": ["restaurant", "food", "menu", "cafe", "bar", "restaurante"],
            "fashion": ["fashion", "clothing", "brand", "apparel", "moda", "ropa"],
            "tech": ["tech", "startup", "ai", "machine learning", "tecnología"],
            "medical": ["medical", "health", "clinic", "doctor", "salud", "médico"],
            "legal": ["law", "legal", "attorney", "lawyer", "abogado"],
            "real_estate": ["real estate", "property", "properties", "inmobiliaria", "bienes raíces"],
            "education": ["school", "university", "education", "course", "escuela", "educación"],
            "fitness": ["gym", "fitness", "workout", "training", "gimnasio"],
        }
        for niche, keywords in niche_keywords.items():
            if any(kw in text_lower for kw in keywords):
                self.context.niche = niche
                break

        page_keywords = {
            "landing": ["landing", "home", "main page", "front page", "página principal"],
            "product": ["product", "feature", "pricing", "producto"],
            "about": ["about", "team", "who we are", "nosotros"],
            "blog": ["blog", "content", "articles", "artículos"],
            "contact": ["contact", "get in touch", "contacto"],
            "ecommerce": ["shop page", "catalog", "catálogo"],
        }
        for page_type, keywords in page_keywords.items():
            if any(kw in text_lower for kw in keywords):
                self.context.page_type = page_type
                break

        pattern_keywords = {
            "animations": "scroll-pin-section",
            "video hero": "video-hero-transition",
            "parallax": "parallax-depth-layers",
            "bento": "bento-tilt-grid",
            "clip path": "clip-path-hero-reveal",
            "3d": "parallax-depth-layers",
            "cursor": "cursor-follower",
            "magnetic": "magnetic-buttons",
            "scramble": "text-scramble-reveal",
        }
        for keyword, pattern in pattern_keywords.items():
            if keyword in text_lower and pattern not in self.context.patterns_discussed:
                self.context.patterns_discussed.append(pattern)

        if len(text) > 20:
            self.context.client_notes.append(text[:200])

    def _extract_client_facts(self, text: str) -> None:
        """Extract factual information about the client and store in memory."""
        text_lower = text.lower()
        mem = self._get_memory()

        # Name detection ("my name is X", "I'm X", "this is X")
        import re
        name_patterns = [
            r"(?:my name is|i'm|i am|this is|me llamo|soy|mi nombre es)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
        ]
        for pattern in name_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                name = match.group(1).strip().title()
                if len(name) > 1 and name.lower() not in ("me", "the", "a"):
                    self._client_name = name
                    try:
                        mem.remember_client(self._client_id, name=name)
                        mem.add_fact(self._client_id, "identity", f"Client's name is {name}")
                    except Exception:
                        pass
                    break

        # Business/company facts
        company_patterns = [
            r"(?:my company|our company|we are|our business|my business|mi empresa|nuestra empresa)\s+(?:is\s+)?(.+?)(?:\.|,|$)",
        ]
        for pattern in company_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                company = match.group(1).strip()[:100]
                if len(company) > 2:
                    try:
                        mem.remember_client(self._client_id, name=self._client_name, company=company)
                        mem.add_fact(self._client_id, "business", f"Company: {company}")
                    except Exception:
                        pass
                    break

        # Budget mentions
        budget_patterns = [
            r"(?:budget|presupuesto)[\s:]+(?:is\s+)?[\$€]?([\d,]+(?:k)?)",
            r"[\$€]([\d,]+(?:k)?)\s+(?:budget|dollars|pesos)",
        ]
        for pattern in budget_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                budget = match.group(1)
                try:
                    mem.add_fact(self._client_id, "budget", f"Mentioned budget: {budget}")
                except Exception:
                    pass
                break

        # Timeline mentions
        timeline_patterns = [
            r"(?:need it|deadline|launch|ready|lanzar)\s+(?:by|in|within|para|en)\s+(.+?)(?:\.|,|$)",
        ]
        for pattern in timeline_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                timeline = match.group(1).strip()[:80]
                try:
                    mem.add_fact(self._client_id, "timeline", f"Timeline: {timeline}")
                except Exception:
                    pass
                break

        # Niche fact
        if self.context.niche:
            try:
                mem.remember_client(self._client_id, name=self._client_name, niche=self.context.niche)
            except Exception:
                pass

    def _extract_final_facts(self) -> None:
        """At end of call, extract summary facts from the full conversation."""
        mem = self._get_memory()
        full_text = " ".join(
            m["content"] for m in self.context.messages if m.get("role") == "user"
        )
        if not full_text:
            return

        # Store niche and page type as facts
        if self.context.niche:
            mem.add_fact(self._client_id, "project", f"Interested in {self.context.niche} website")
        if self.context.page_type:
            mem.add_fact(self._client_id, "project", f"Needs {self.context.page_type} page")
        if self.context.patterns_discussed:
            for p in self.context.patterns_discussed:
                mem.add_fact(self._client_id, "design", f"Discussed pattern: {p}")
        if self.context.preferences:
            for pref in self.context.preferences:
                mem.add_fact(self._client_id, "preference", pref)

        # Update client language preference
        if self.context.detected_language:
            mem.remember_client(
                self._client_id,
                name=self._client_name,
                language=self.context.detected_language,
            )


__all__ = ["VoiceCallManager", "CallState", "ConversationContext"]
