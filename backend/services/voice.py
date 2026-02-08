"""
Synthia Voice Service - The Pauli Effect

Synthia is the AI agent for The Pauli Effect agency.
She communicates via ElevenLabs in multiple languages:
- Spanish (es) - Primary for Mexico City market
- English (en) - International clients
- Hindi (hi) - Indian market
- Serbian (sr) - European market
"""

import os
import asyncio
import httpx
from typing import Optional, Dict
from dataclasses import dataclass
from enum import Enum


class LanguageCode(str, Enum):
    SPANISH = "es"
    ENGLISH = "en"
    HINDI = "hi"
    SERBIAN = "sr"


class VoiceType(str, Enum):
    """Voice type presets for /voice/synthesize endpoint."""
    PAULI_DEFAULT = "pauli_default"  # Spanish voice - XB0fDUnXU5powFXDhCwa
    PROFESSIONAL_FEMALE = "professional_female"  # Rachel
    PROFESSIONAL_MALE = "professional_male"  # Josh
    WARM_CONVERSATIONAL = "warm_conversational"  # Bella
    ENERGETIC_MALE = "energetic_male"  # Antoni


# Map VoiceType to LanguageCode for backward-compatible lookup
VOICE_TYPE_LANGUAGE_MAP: Dict[VoiceType, LanguageCode] = {
    VoiceType.PAULI_DEFAULT: LanguageCode.SPANISH,
    VoiceType.PROFESSIONAL_FEMALE: LanguageCode.ENGLISH,
    VoiceType.PROFESSIONAL_MALE: LanguageCode.SERBIAN,
    VoiceType.WARM_CONVERSATIONAL: LanguageCode.HINDI,
    VoiceType.ENERGETIC_MALE: LanguageCode.ENGLISH,
}


@dataclass
class VoiceConfig:
    voice_id: str
    language: LanguageCode
    stability: float = 0.5
    similarity_boost: float = 0.75
    style: float = 0.0
    use_speaker_boost: bool = True


# ElevenLabs Voice IDs by Language
# Synthia uses different voices for different languages
VOICE_MAP: Dict[LanguageCode, VoiceConfig] = {
    LanguageCode.SPANISH: VoiceConfig(
        voice_id="XB0fDUnXU5powFXDhCwa",  # Spanish voice
        language=LanguageCode.SPANISH,
        stability=0.6,
        similarity_boost=0.8
    ),
    LanguageCode.ENGLISH: VoiceConfig(
        voice_id="XB0fDUnXU5powFXDhCwa",  # Rachel - Professional female
        language=LanguageCode.ENGLISH,
        stability=0.5,
        similarity_boost=0.75
    ),
    LanguageCode.HINDI: VoiceConfig(
        voice_id="21m00Tcm4TlvDq8ikWAM",  # Bella - Warm conversational
        language=LanguageCode.HINDI,
        stability=0.6,
        similarity_boost=0.8
    ),
    LanguageCode.SERBIAN: VoiceConfig(
        voice_id="TxGEqnHWrfWFTfGW9XjX",  # Josh - Professional male
        language=LanguageCode.SERBIAN,
        stability=0.5,
        similarity_boost=0.75
    ),
}


class VoiceService:
    """
    Synthia's Voice Service for The Pauli Effect.
    Handles multilingual voice synthesis and transcription.
    """
    
    def __init__(self):
        self.elevenlabs_api_key = os.getenv("ELEVEN_LABS_API") or os.getenv("ELEVENLABS_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1"
        self.default_language = LanguageCode(os.getenv("DEFAULT_LANGUAGE", "es"))
        self._local_whisper = None  # Lazy-loaded faster-whisper model
        
    def detect_language(self, text: str) -> LanguageCode:
        """
        Detect language from text.
        Simple heuristic - can be enhanced with proper language detection.
        """
        # Spanish indicators
        if any(char in text.lower() for char in ['ñ', 'á', 'é', 'í', 'ó', 'ú', '¿', '¡']):
            return LanguageCode.SPANISH
        
        # Hindi indicators (Devanagari range)
        if any('\u0900' <= char <= '\u097F' for char in text):
            return LanguageCode.HINDI
        
        # Serbian indicators (Cyrillic)
        if any('\u0400' <= char <= '\u04FF' for char in text):
            return LanguageCode.SERBIAN
        
        # Default to English
        return LanguageCode.ENGLISH
    
    async def synthesize(
        self,
        text: str,
        language: Optional[LanguageCode] = None,
        model: str = "eleven_turbo_v2_5"
    ) -> bytes:
        """
        Synthesize text to speech in specified language.
        Synthia speaks Spanish, English, Hindi, and Serbian.
        """
        if not self.elevenlabs_api_key:
            raise ValueError("ELEVEN_LABS_API not configured")
        
        # Auto-detect language if not specified
        lang = language or self.detect_language(text) or self.default_language
        config = VOICE_MAP.get(lang, VOICE_MAP[LanguageCode.ENGLISH])
        
        url = f"{self.base_url}/text-to-speech/{config.voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.elevenlabs_api_key,
        }
        
        payload = {
            "text": text,
            "model_id": model,
            "voice_settings": {
                "stability": config.stability,
                "similarity_boost": config.similarity_boost,
                "style": config.style,
                "use_speaker_boost": config.use_speaker_boost,
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload, headers=headers)
            response.raise_for_status()
            return response.content
    
    async def transcribe(self, audio_data: bytes, language: Optional[str] = None) -> str:
        """
        Transcribe audio to text.
        Tries OpenAI Whisper API first, falls back to local faster-whisper.
        """
        # Try OpenAI Whisper API first
        if self.openai_api_key:
            try:
                return await self._transcribe_openai(audio_data, language)
            except Exception as e:
                print(f"OpenAI STT failed ({e}), falling back to local Whisper...")

        # Fall back to local faster-whisper
        return await self._transcribe_local(audio_data, language)

    async def _transcribe_openai(self, audio_data: bytes, language: Optional[str] = None) -> str:
        """Transcribe via OpenAI Whisper API."""
        url = "https://api.openai.com/v1/audio/transcriptions"
        
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
        }
        
        files = {
            "file": ("audio.wav", audio_data, "audio/wav"),
            "model": (None, "whisper-1"),
        }
        
        if language:
            files["language"] = (None, language)
        
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(url, headers=headers, files=files)
            response.raise_for_status()
            data = response.json()
            return data.get("text", "")

    async def _transcribe_local(self, audio_data: bytes, language: Optional[str] = None) -> str:
        """Transcribe using local faster-whisper model (no API key needed)."""
        import tempfile
        import os as _os

        # Lazy-load the model
        if self._local_whisper is None:
            try:
                from faster_whisper import WhisperModel
                self._local_whisper = WhisperModel(
                    "base",  # small/fast model, upgrade to "small" or "medium" for better accuracy
                    device="cpu",
                    compute_type="int8",
                )
                print("Local Whisper model loaded (faster-whisper/base)")
            except ImportError:
                raise RuntimeError("No STT available: OpenAI key invalid and faster-whisper not installed")

        # Write audio to temp file (faster-whisper needs a file path)
        tmp_path = None
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name

            # Run transcription in thread pool to not block event loop
            loop = asyncio.get_event_loop()
            segments, info = await loop.run_in_executor(
                None,
                lambda: self._local_whisper.transcribe(
                    tmp_path,
                    language=language,
                    beam_size=3,
                    vad_filter=True,
                )
            )
            # Collect all segments
            text_parts = []
            for segment in segments:
                text_parts.append(segment.text)
            return " ".join(text_parts).strip()
        finally:
            if tmp_path and _os.path.exists(tmp_path):
                _os.unlink(tmp_path)
    
    async def stream_synthesize(
        self,
        text: str,
        language: Optional[LanguageCode] = None
    ):
        """Stream audio chunks for real-time voice output."""
        if not self.elevenlabs_api_key:
            raise ValueError("ELEVEN_LABS_API not configured")
        
        lang = language or self.detect_language(text) or self.default_language
        config = VOICE_MAP.get(lang, VOICE_MAP[LanguageCode.ENGLISH])
        
        url = f"{self.base_url}/text-to-speech/{config.voice_id}/stream"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": self.elevenlabs_api_key,
        }
        
        payload = {
            "text": text,
            "model_id": "eleven_turbo_v2_5",
            "stream": True,
            "voice_settings": {
                "stability": config.stability,
                "similarity_boost": config.similarity_boost,
            }
        }
        
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, json=payload, headers=headers) as response:
                response.raise_for_status()
                async for chunk in response.aiter_bytes():
                    yield chunk


# Singleton instance
_voice_service: Optional[VoiceService] = None


def get_voice_service() -> VoiceService:
    """Get or create voice service singleton."""
    global _voice_service
    if _voice_service is None:
        _voice_service = VoiceService()
    return _voice_service
