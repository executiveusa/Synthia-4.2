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
        self.elevenlabs_api_key = os.getenv("ELEVEN_LABS_API")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = "https://api.elevenlabs.io/v1"
        self.default_language = LanguageCode(os.getenv("DEFAULT_LANGUAGE", "es"))
        
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
        Transcribe audio to text using OpenAI Whisper.
        Supports multilingual transcription.
        """
        if not self.openai_api_key:
            raise ValueError("OPENAI_API_KEY not configured")
        
        url = "https://api.openai.com/v1/audio/transcriptions"
        
        headers = {
            "Authorization": f"Bearer {self.openai_api_key}",
        }
        
        files = {
            "file": ("audio.mp3", audio_data, "audio/mpeg"),
            "model": (None, "whisper-1"),
        }
        
        # Add language hint if provided (es, en, hi, sr)
        if language:
            files["language"] = (None, language)
        
        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, files=files)
            response.raise_for_status()
            data = response.json()
            return data.get("text", "")
    
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
