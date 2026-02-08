"""
Synthia 4.2 - Audio Utilities

Handles audio format conversions for the Twilio ↔ Whisper ↔ ElevenLabs pipeline.

Twilio Media Streams deliver mulaw/8000 (G.711 μ-law, 8kHz, 8-bit mono).
Whisper expects PCM 16-bit 16kHz mono or mp3/wav/webm.
ElevenLabs returns mp3 or PCM.

Conversion flow:
  Inbound:  Twilio mulaw/8000 → PCM 16-bit/16kHz → Whisper
  Outbound: ElevenLabs mp3 → PCM 16-bit/8kHz → mulaw/8000 → Twilio
"""

import io
import struct
import asyncio
import logging
import audioop
import base64
import wave
from typing import Optional

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# μ-law Codec
# ═══════════════════════════════════════════════════════════════

# μ-law encoding/decoding lookup tables for G.711
MULAW_BIAS = 0x84
MULAW_MAX = 0x7FFF
MULAW_CLIP = 32635

# Pre-computed μ-law decode table (256 entries)
_MULAW_DECODE_TABLE: list[int] = []


def _build_mulaw_decode_table() -> list[int]:
    """Build μ-law to 16-bit linear PCM decode table."""
    table = []
    for i in range(256):
        val = ~i
        sign = val & 0x80
        exponent = (val >> 4) & 0x07
        mantissa = val & 0x0F
        sample = ((mantissa << 3) + MULAW_BIAS) << exponent
        sample -= MULAW_BIAS
        if sign:
            sample = -sample
        table.append(sample)
    return table


_MULAW_DECODE_TABLE = _build_mulaw_decode_table()


def mulaw_decode(mulaw_bytes: bytes) -> bytes:
    """
    Decode μ-law encoded bytes to 16-bit signed PCM.

    Input: mulaw bytes (8kHz, 8-bit, mono)
    Output: PCM bytes (8kHz, 16-bit, mono, little-endian)
    """
    try:
        # Use audioop for efficient conversion (C-level, much faster)
        return audioop.ulaw2lin(mulaw_bytes, 2)
    except Exception:
        # Fallback to pure Python if audioop unavailable
        samples = []
        for byte in mulaw_bytes:
            samples.append(_MULAW_DECODE_TABLE[byte])
        return struct.pack(f"<{len(samples)}h", *samples)


def mulaw_encode(pcm_bytes: bytes) -> bytes:
    """
    Encode 16-bit signed PCM to μ-law.

    Input: PCM bytes (8kHz, 16-bit, mono, little-endian)
    Output: mulaw bytes (8kHz, 8-bit, mono)
    """
    try:
        return audioop.lin2ulaw(pcm_bytes, 2)
    except Exception:
        # Fallback to pure Python
        samples = struct.unpack(f"<{len(pcm_bytes) // 2}h", pcm_bytes)
        encoded = []
        for sample in samples:
            sign = 0
            if sample < 0:
                sign = 0x80
                sample = -sample
            if sample > MULAW_CLIP:
                sample = MULAW_CLIP
            sample += MULAW_BIAS

            exponent = 7
            mask = 0x4000
            for exp in range(7, 0, -1):
                if sample & mask:
                    exponent = exp
                    break
                mask >>= 1
            else:
                exponent = 0

            mantissa = (sample >> (exponent + 3)) & 0x0F
            byte = ~(sign | (exponent << 4) | mantissa) & 0xFF
            encoded.append(byte)
        return bytes(encoded)


# ═══════════════════════════════════════════════════════════════
# Sample Rate Conversion
# ═══════════════════════════════════════════════════════════════

def resample_8k_to_16k(pcm_8k: bytes) -> bytes:
    """
    Upsample 16-bit PCM from 8kHz to 16kHz (linear interpolation).
    Required for Whisper which expects 16kHz input.
    """
    try:
        # audioop.ratecv is efficient and handles this well
        converted, _ = audioop.ratecv(pcm_8k, 2, 1, 8000, 16000, None)
        return converted
    except Exception:
        # Simple linear interpolation fallback
        samples = struct.unpack(f"<{len(pcm_8k) // 2}h", pcm_8k)
        upsampled = []
        for i in range(len(samples) - 1):
            upsampled.append(samples[i])
            # Interpolated midpoint
            upsampled.append((samples[i] + samples[i + 1]) // 2)
        if samples:
            upsampled.append(samples[-1])
        return struct.pack(f"<{len(upsampled)}h", *upsampled)


def resample_16k_to_8k(pcm_16k: bytes) -> bytes:
    """
    Downsample 16-bit PCM from 16kHz to 8kHz.
    Required for converting ElevenLabs output to Twilio format.
    """
    try:
        converted, _ = audioop.ratecv(pcm_16k, 2, 1, 16000, 8000, None)
        return converted
    except Exception:
        # Simple decimation (take every other sample)
        samples = struct.unpack(f"<{len(pcm_16k) // 2}h", pcm_16k)
        decimated = samples[::2]
        return struct.pack(f"<{len(decimated)}h", *decimated)


def resample_to_8k(pcm_data: bytes, source_rate: int) -> bytes:
    """Resample PCM from any rate to 8kHz."""
    if source_rate == 8000:
        return pcm_data
    try:
        converted, _ = audioop.ratecv(pcm_data, 2, 1, source_rate, 8000, None)
        return converted
    except Exception as e:
        logger.error("Resample from %d to 8k failed: %s", source_rate, e)
        return pcm_data


# ═══════════════════════════════════════════════════════════════
# WAV Helpers
# ═══════════════════════════════════════════════════════════════

def pcm_to_wav(pcm_bytes: bytes, sample_rate: int = 16000, channels: int = 1) -> bytes:
    """Wrap raw PCM bytes in a WAV container for Whisper."""
    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sample_rate)
        wf.writeframes(pcm_bytes)
    return buf.getvalue()


def mulaw_to_wav_16k(mulaw_bytes: bytes) -> bytes:
    """
    Full pipeline: mulaw/8kHz → PCM/8kHz → PCM/16kHz → WAV/16kHz.
    Ready for Whisper transcription.
    """
    pcm_8k = mulaw_decode(mulaw_bytes)
    pcm_16k = resample_8k_to_16k(pcm_8k)
    return pcm_to_wav(pcm_16k, sample_rate=16000)


# ═══════════════════════════════════════════════════════════════
# MP3 → mulaw conversion (for ElevenLabs → Twilio)
# ═══════════════════════════════════════════════════════════════

def mp3_to_mulaw(mp3_bytes: bytes) -> bytes:
    """
    Convert MP3 audio (from ElevenLabs) to mulaw/8kHz for Twilio.
    Uses pydub if available, otherwise falls back to raw approach.
    """
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_mp3(io.BytesIO(mp3_bytes))
        # Convert to mono, 8kHz, 16-bit PCM
        audio = audio.set_channels(1).set_frame_rate(8000).set_sample_width(2)
        pcm_data = audio.raw_data
        return mulaw_encode(pcm_data)
    except ImportError:
        logger.warning("pydub not installed - returning raw mp3 (Twilio may not play correctly)")
        return mp3_bytes
    except Exception as e:
        logger.error("MP3 to mulaw conversion failed: %s", e)
        return mp3_bytes


def pcm_to_mulaw_8k(pcm_bytes: bytes, source_rate: int = 22050) -> bytes:
    """Convert raw PCM at any sample rate to mulaw/8kHz."""
    pcm_8k = resample_to_8k(pcm_bytes, source_rate)
    return mulaw_encode(pcm_8k)


# ═══════════════════════════════════════════════════════════════
# Audio Buffer (for accumulating Twilio 20ms chunks)
# ═══════════════════════════════════════════════════════════════

class AudioBuffer:
    """
    Accumulates mulaw audio chunks from Twilio until we have enough
    for meaningful transcription (~1-2 seconds of audio).

    Twilio sends 20ms chunks at 8kHz = 160 bytes per chunk.
    For good Whisper transcription, we want ~1-2 seconds = 8000-16000 bytes.
    """

    def __init__(self, min_bytes: int = 8000, max_bytes: int = 64000):
        self._buffer = bytearray()
        self._min_bytes = min_bytes  # ~1 second at 8kHz mulaw
        self._max_bytes = max_bytes  # ~8 seconds max
        self._silence_threshold = 500      # RMS threshold for silence detection
        self._silence_chunks = 0
        self._speech_detected = False

    def add_chunk(self, mulaw_chunk: bytes) -> Optional[bytes]:
        """
        Add a 20ms mulaw chunk. Returns accumulated audio when ready
        (enough data + silence detected), or None if still buffering.
        """
        self._buffer.extend(mulaw_chunk)

        # Check if this chunk is silence
        try:
            pcm = mulaw_decode(mulaw_chunk)
            rms = audioop.rms(pcm, 2)
        except Exception:
            rms = 0

        if rms < self._silence_threshold:
            self._silence_chunks += 1
        else:
            self._silence_chunks = 0
            self._speech_detected = True

        # Return buffer if:
        # 1. We have enough audio AND silence detected (end of utterance)
        # 2. Buffer is at max capacity
        buffer_len = len(self._buffer)

        if buffer_len >= self._max_bytes:
            return self._flush()

        if (buffer_len >= self._min_bytes
                and self._speech_detected
                and self._silence_chunks >= 15):  # ~300ms of silence
            return self._flush()

        return None

    def _flush(self) -> bytes:
        """Return accumulated audio and reset buffer."""
        audio = bytes(self._buffer)
        self._buffer.clear()
        self._silence_chunks = 0
        self._speech_detected = False
        return audio

    def flush_remaining(self) -> Optional[bytes]:
        """Flush any remaining audio (e.g., on hangup)."""
        if len(self._buffer) > 160:  # At least one chunk
            return self._flush()
        return None

    @property
    def duration_seconds(self) -> float:
        """Estimated duration of buffered audio in seconds."""
        return len(self._buffer) / 8000.0


# ═══════════════════════════════════════════════════════════════
# Twilio Media Stream Protocol Helpers
# ═══════════════════════════════════════════════════════════════

def create_media_message(stream_sid: str, mulaw_payload: bytes) -> dict:
    """
    Create a Twilio Media Stream outbound 'media' message.
    The payload must be base64-encoded mulaw audio.
    """
    return {
        "event": "media",
        "streamSid": stream_sid,
        "media": {
            "payload": base64.b64encode(mulaw_payload).decode("ascii")
        }
    }


def create_mark_message(stream_sid: str, name: str = "endOfResponse") -> dict:
    """
    Create a Twilio Media Stream 'mark' message.
    Used to signal the end of a response or track audio playback position.
    """
    return {
        "event": "mark",
        "streamSid": stream_sid,
        "mark": {
            "name": name
        }
    }


def create_clear_message(stream_sid: str) -> dict:
    """
    Create a Twilio Media Stream 'clear' message.
    Clears any queued audio on the stream (used for interruptions).
    """
    return {
        "event": "clear",
        "streamSid": stream_sid
    }


# ═══════════════════════════════════════════════════════════════
# Chunk splitter for Twilio playback
# ═══════════════════════════════════════════════════════════════

def split_mulaw_for_twilio(mulaw_bytes: bytes, chunk_size: int = 640) -> list[bytes]:
    """
    Split mulaw audio into chunks suitable for Twilio Media Stream playback.
    Default 640 bytes = 80ms at 8kHz (Twilio's recommended payload size).
    """
    chunks = []
    for i in range(0, len(mulaw_bytes), chunk_size):
        chunk = mulaw_bytes[i:i + chunk_size]
        if len(chunk) > 0:
            chunks.append(chunk)
    return chunks


__all__ = [
    "mulaw_decode",
    "mulaw_encode",
    "resample_8k_to_16k",
    "resample_16k_to_8k",
    "resample_to_8k",
    "pcm_to_wav",
    "mulaw_to_wav_16k",
    "mp3_to_mulaw",
    "pcm_to_mulaw_8k",
    "AudioBuffer",
    "create_media_message",
    "create_mark_message",
    "create_clear_message",
    "split_mulaw_for_twilio",
]
