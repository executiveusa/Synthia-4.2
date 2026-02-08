"""
Unit tests for Audio Utilities
Tests μ-law codec, resampling, and Twilio audio pipeline
"""

import os
import sys
import struct

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from services.audio_utils import (
    mulaw_encode, mulaw_decode, resample_8k_to_16k, resample_16k_to_8k,
    pcm_to_wav, mulaw_to_wav_16k, AudioBuffer, split_mulaw_for_twilio,
    create_media_message, create_mark_message, create_clear_message
)


def test_mulaw_codec():
    """Test μ-law encoding and decoding"""

    # Create test PCM data (16-bit samples)
    test_samples = [0, 1000, -1000, 32767, -32768]
    pcm_bytes = struct.pack(f"<{len(test_samples)}h", *test_samples)

    # Encode to μ-law
    mulaw_bytes = mulaw_encode(pcm_bytes)
    assert len(mulaw_bytes) == len(test_samples), "μ-law should be 1 byte per sample"
    print(f"✅ μ-law encoding: {len(pcm_bytes)} bytes PCM → {len(mulaw_bytes)} bytes μ-law")

    # Decode back to PCM (won't be identical due to quantization, but close)
    decoded_pcm = mulaw_decode(mulaw_bytes)
    assert len(decoded_pcm) == len(pcm_bytes), "Decoded PCM should match input length"
    print(f"✅ μ-law decoding: {len(mulaw_bytes)} bytes μ-law → {len(decoded_pcm)} bytes PCM")


def test_resample_8k_to_16k():
    """Test 8kHz → 16kHz upsampling"""

    # Create 8kHz PCM data (100ms = 800 samples)
    samples_8k = list(range(100))
    pcm_8k = struct.pack(f"<{len(samples_8k)}h", *samples_8k)

    # Upsample to 16kHz
    pcm_16k = resample_8k_to_16k(pcm_8k)
    samples_16k = struct.unpack(f"<{len(pcm_16k) // 2}h", pcm_16k)

    # Should have approximately double the samples
    assert len(samples_16k) >= len(samples_8k), "16kHz should have more samples"
    print(f"✅ Upsample 8k→16k: {len(samples_8k)} → {len(samples_16k)} samples")


def test_resample_16k_to_8k():
    """Test 16kHz → 8kHz downsampling"""

    # Create 16kHz PCM data (100ms = 1600 samples)
    samples_16k = list(range(200))
    pcm_16k = struct.pack(f"<{len(samples_16k)}h", *samples_16k)

    # Downsample to 8kHz
    pcm_8k = resample_16k_to_8k(pcm_16k)
    samples_8k = struct.unpack(f"<{len(pcm_8k) // 2}h", pcm_8k)

    # Should have approximately half the samples
    assert len(samples_8k) <= len(samples_16k), "8kHz should have fewer samples"
    print(f"✅ Downsample 16k→8k: {len(samples_16k)} → {len(samples_8k)} samples")


def test_pcm_to_wav():
    """Test PCM wrapping in WAV container"""

    # Create test PCM data
    test_samples = [0, 1000, 2000, 3000]
    pcm_bytes = struct.pack(f"<{len(test_samples)}h", *test_samples)

    # Wrap in WAV
    wav_bytes = pcm_to_wav(pcm_bytes, sample_rate=16000, channels=1)

    # WAV should start with "RIFF"
    assert wav_bytes[:4] == b"RIFF", "WAV should start with RIFF header"
    print(f"✅ PCM→WAV conversion: {len(pcm_bytes)} bytes PCM → {len(wav_bytes)} bytes WAV")


def test_full_pipeline():
    """Test full Twilio → Whisper pipeline: mulaw/8k → PCM/16k → WAV"""

    # Simulate Twilio audio (mulaw/8000)
    pcm_8k = struct.pack("<100h", *range(100))
    mulaw_bytes = mulaw_encode(pcm_8k)

    # Full pipeline
    wav_bytes = mulaw_to_wav_16k(mulaw_bytes)

    # Should be valid WAV
    assert wav_bytes[:4] == b"RIFF", "Output should be WAV"
    print(f"✅ Full pipeline: mulaw/8k ({len(mulaw_bytes)}) → WAV/16k ({len(wav_bytes)} bytes)")


def test_audio_buffer():
    """Test AudioBuffer for accumulating Twilio chunks"""

    buffer = AudioBuffer(min_bytes=160, max_bytes=1000)

    # Simulate Twilio 20ms chunks (160 bytes each at 8kHz)
    for i in range(5):
        chunk = b'\x00' * 160  # Silence
        result = buffer.add_chunk(chunk)
        if result:
            break

    print(f"✅ AudioBuffer: Processed chunks, duration={buffer.duration_seconds:.2f}s")


def test_twilio_message_format():
    """Test Twilio Media Stream message format"""

    stream_sid = "MZ1234567890abcdef"
    mulaw_payload = b'\x00\x80\x40\xc0'  # Mock μ-law data

    # Test media message
    msg = create_media_message(stream_sid, mulaw_payload)
    assert msg["event"] == "media"
    assert msg["streamSid"] == stream_sid
    assert "payload" in msg["media"]
    print(f"✅ Media message format OK")

    # Test mark message
    mark = create_mark_message(stream_sid, "test_mark")
    assert mark["event"] == "mark"
    assert mark["mark"]["name"] == "test_mark"
    print(f"✅ Mark message format OK")

    # Test clear message
    clear = create_clear_message(stream_sid)
    assert clear["event"] == "clear"
    print(f"✅ Clear message format OK")


def test_chunk_splitter():
    """Test splitting mulaw for Twilio playback"""

    # Create 2 seconds of mulaw at 8kHz (16000 bytes)
    mulaw_data = b'\x00' * 16000

    # Split into 80ms chunks (640 bytes)
    chunks = split_mulaw_for_twilio(mulaw_data, chunk_size=640)

    assert len(chunks) == 25, f"Should have 25 chunks (16000/640), got {len(chunks)}"
    assert all(len(c) == 640 for c in chunks), "All chunks should be 640 bytes"
    print(f"✅ Chunk splitter: {len(mulaw_data)} bytes → {len(chunks)} × 640-byte chunks")


if __name__ == "__main__":
    print("\n🧪 Testing Audio Utilities...\n")
    test_mulaw_codec()
    test_resample_8k_to_16k()
    test_resample_16k_to_8k()
    test_pcm_to_wav()
    test_full_pipeline()
    test_audio_buffer()
    test_twilio_message_format()
    test_chunk_splitter()
    print("\n✅ All audio tests passed!\n")
