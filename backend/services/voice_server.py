"""
Synthia Voice Server - The Pauli Effect

Real-time voice collaboration for Synthia, the AI agent who manages
coding and frontend design for The Pauli Effect agency.

Languages supported:
- Spanish (es) - Mexico City market
- English (en) - International clients  
- Hindi (hi) - Indian market
- Serbian (sr) - European market
"""

import os
from pathlib import Path

# Load environment variables before anything else
from dotenv import load_dotenv
_backend_dir = Path(__file__).resolve().parent.parent
_project_dir = _backend_dir.parent
load_dotenv(_project_dir / ".env")
load_dotenv(_project_dir / "master.env", override=True)

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, UploadFile, File
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import io

from .voice import get_voice_service, LanguageCode

app = FastAPI(
    title="Synthia Voice Server - The Pauli Effect",
    description="Multilingual voice service for Synthia AI Agent",
    version="4.2.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class SynthesizeRequest(BaseModel):
    text: str
    language: str = "es"  # es, en, hi, sr

class TranscriptionResponse(BaseModel):
    text: str
    language: Optional[str] = None
    confidence: float = 1.0

# Routes
@app.get("/health")
async def health_check():
    return {
        "status": "ok",
        "service": "Synthia Voice Server",
        "organization": "The Pauli Effect",
        "agent": "Synthia",
        "languages": ["es", "en", "hi", "sr"]
    }

@app.post("/synthesize")
async def synthesize_voice(request: SynthesizeRequest):
    """Synthesize text to speech in specified language."""
    try:
        voice_service = get_voice_service()
        
        # Map language code
        lang_map = {
            "es": LanguageCode.SPANISH,
            "en": LanguageCode.ENGLISH,
            "hi": LanguageCode.HINDI,
            "sr": LanguageCode.SERBIAN,
        }
        language = lang_map.get(request.language, LanguageCode.SPANISH)
        
        audio_data = await voice_service.synthesize(request.text, language)
        
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=synthia_speech.mp3"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/transcribe", response_model=TranscriptionResponse)
async def transcribe_audio(file: UploadFile = File(...), language: Optional[str] = None):
    """Transcribe audio to text."""
    try:
        voice_service = get_voice_service()
        audio_data = await file.read()
        text = await voice_service.transcribe(audio_data, language)
        
        # Detect language from text
        detected_lang = voice_service.detect_language(text)
        
        return TranscriptionResponse(
            text=text,
            language=detected_lang.value,
            confidence=1.0
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.websocket("/ws/voice")
async def voice_websocket(websocket: WebSocket):
    """Real-time multilingual voice collaboration WebSocket."""
    await websocket.accept()
    voice_service = get_voice_service()
    
    try:
        while True:
            # Receive message
            message = await websocket.receive_json()
            
            if message.get("type") == "transcribe":
                # Handle transcription request
                audio_data = message.get("audio")
                language_hint = message.get("language")
                if audio_data:
                    import base64
                    audio_bytes = base64.b64decode(audio_data)
                    text = await voice_service.transcribe(audio_bytes, language_hint)
                    detected = voice_service.detect_language(text)
                    await websocket.send_json({
                        "type": "transcription",
                        "text": text,
                        "language": detected.value
                    })
            
            elif message.get("type") == "synthesize":
                # Handle synthesis request
                text = message.get("text", "")
                lang_code = message.get("language", "es")
                
                lang_map = {
                    "es": LanguageCode.SPANISH,
                    "en": LanguageCode.ENGLISH,
                    "hi": LanguageCode.HINDI,
                    "sr": LanguageCode.SERBIAN,
                }
                language = lang_map.get(lang_code, LanguageCode.SPANISH)
                
                # Stream audio chunks
                async for chunk in voice_service.stream_synthesize(text, language):
                    import base64
                    await websocket.send_json({
                        "type": "audio_chunk",
                        "data": base64.b64encode(chunk).decode()
                    })
                
                await websocket.send_json({"type": "audio_end"})
            
            elif message.get("type") == "chat":
                # Handle chat message with voice response
                text = message.get("text", "")
                lang_code = message.get("language", "es")
                
                # Synthia's response
                response_text = f"¡Hola!我是 Synthia from The Pauli Effect. I received: {text}"
                
                await websocket.send_json({
                    "type": "text_response",
                    "text": response_text,
                    "agent": "Synthia",
                    "organization": "The Pauli Effect"
                })
                
                # Stream voice response
                lang_map = {
                    "es": LanguageCode.SPANISH,
                    "en": LanguageCode.ENGLISH,
                    "hi": LanguageCode.HINDI,
                    "sr": LanguageCode.SERBIAN,
                }
                language = lang_map.get(lang_code, LanguageCode.SPANISH)
                
                async for chunk in voice_service.stream_synthesize(response_text, language):
                    import base64
                    await websocket.send_json({
                        "type": "audio_chunk",
                        "data": base64.b64encode(chunk).decode()
                    })
                
                await websocket.send_json({"type": "audio_end"})
                
    except WebSocketDisconnect:
        print("Client disconnected from Synthia voice service")
    except Exception as e:
        print(f"Error in Synthia voice websocket: {e}")
        await websocket.close()

# ═══════════════════════════════════════════════════════════════
# Twilio Media Stream WebSocket (Production Pipeline)
# ═══════════════════════════════════════════════════════════════

@app.websocket("/ws/twilio-stream")
async def twilio_media_stream(websocket: WebSocket):
    """
    Handle Twilio Bidirectional Media Stream for real-time voice calls.

    Protocol (from Twilio docs):
    - Twilio sends: start, media (mulaw/8kHz base64), stop, mark, dtmf
    - We send back: media (mulaw/8kHz base64), mark, clear

    Audio pipeline:
    - Inbound:  base64 → mulaw → AudioBuffer(VAD) → WAV/16kHz → Whisper
    - Outbound: ElevenLabs mp3 → mulaw → 640-byte chunks → base64 → Twilio
    """
    await websocket.accept()
    print("✅ Twilio media stream connected")

    from services.voice_call import VoiceCallManager
    from services.audio_utils import (
        create_media_message,
        create_mark_message,
        create_clear_message,
    )
    import base64

    manager = VoiceCallManager()
    stream_sid = ""

    try:
        while True:
            data = await websocket.receive_json()
            event = data.get("event", "")

            if event == "start":
                start_data = data.get("start", {})
                stream_sid = start_data.get("streamSid", "")
                call_sid = start_data.get("callSid", "")
                # Extract caller number from customParameters or start data
                custom = start_data.get("customParameters", {})
                caller_number = custom.get("callerNumber", "")
                if not caller_number:
                    # Try to get from the call metadata
                    caller_number = custom.get("from", "")

                manager.call_sid = call_sid
                manager.stream_sid = stream_sid
                manager.caller_number = caller_number
                print(f"📞 Twilio stream started: {stream_sid} (call: {call_sid}, caller: {caller_number})")

                # Send greeting audio
                greeting_chunks = await manager.on_connect()
                for chunk in greeting_chunks:
                    msg = create_media_message(stream_sid, chunk)
                    await websocket.send_json(msg)

                # Mark end of greeting so we know when playback finishes
                if greeting_chunks:
                    mark_msg = create_mark_message(stream_sid, "greeting_end")
                    await websocket.send_json(mark_msg)

            elif event == "media":
                payload = data.get("media", {}).get("payload", "")
                mulaw_chunk = base64.b64decode(payload)

                # Feed 20ms chunk into VoiceCallManager (AudioBuffer + VAD)
                response_chunks = await manager.on_mulaw_chunk(mulaw_chunk)

                if response_chunks:
                    # Clear any queued audio first (interruption handling)
                    clear_msg = create_clear_message(stream_sid)
                    await websocket.send_json(clear_msg)

                    # Send all response chunks
                    for chunk in response_chunks:
                        msg = create_media_message(stream_sid, chunk)
                        await websocket.send_json(msg)

                    # Send mark to track end of response playback
                    manager._mark_counter += 0  # counter already incremented in _process_utterance
                    mark_msg = create_mark_message(
                        stream_sid,
                        f"response_{manager._mark_counter}"
                    )
                    await websocket.send_json(mark_msg)

            elif event == "mark":
                mark_name = data.get("mark", {}).get("name", "")
                manager.on_mark_received(mark_name)

            elif event == "dtmf":
                digit = data.get("dtmf", {}).get("digit", "")
                print(f"🔢 DTMF received: {digit}")

            elif event == "stop":
                print(f"📴 Twilio stream stopped: {stream_sid}")
                job_id = await manager.on_hangup()
                if job_id:
                    print(f"🚀 Agent pipeline dispatched: {job_id}")
                break

    except WebSocketDisconnect:
        print("📴 Twilio stream disconnected")
        await manager.on_hangup()
    except Exception as e:
        print(f"❌ Error in Twilio stream: {e}")
        import traceback
        traceback.print_exc()
        await manager.on_hangup()
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
