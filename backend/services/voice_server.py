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
# Twilio Media Stream WebSocket
# ═══════════════════════════════════════════════════════════════

@app.websocket("/ws/twilio-stream")
async def twilio_media_stream(websocket: WebSocket):
    """
    Handle Twilio Media Stream for real-time voice calls.
    Receives mulaw/8000 audio from Twilio, processes through
    VoiceCallManager, sends response audio back.
    """
    await websocket.accept()
    print("Twilio media stream connected")

    from services.voice_call import VoiceCallManager
    manager = VoiceCallManager()
    stream_sid = ""

    try:
        # Send greeting on connect
        greeting_audio = await manager.on_connect()
        if greeting_audio:
            import base64
            await websocket.send_json({
                "event": "media",
                "streamSid": stream_sid,
                "media": {
                    "payload": base64.b64encode(greeting_audio).decode()
                }
            })

        while True:
            data = await websocket.receive_json()
            event = data.get("event", "")

            if event == "start":
                stream_sid = data.get("start", {}).get("streamSid", "")
                manager.call_sid = data.get("start", {}).get("callSid", "")
                print(f"Twilio stream started: {stream_sid}")

            elif event == "media":
                import base64
                payload = data.get("media", {}).get("payload", "")
                audio_bytes = base64.b64decode(payload)

                # Process audio through VoiceCallManager
                response_audio = await manager.on_audio_received(audio_bytes)
                if response_audio:
                    await websocket.send_json({
                        "event": "media",
                        "streamSid": stream_sid,
                        "media": {
                            "payload": base64.b64encode(response_audio).decode()
                        }
                    })

            elif event == "stop":
                print(f"Twilio stream stopped: {stream_sid}")
                job_id = await manager.on_hangup()
                if job_id:
                    await websocket.send_json({
                        "event": "synthia_pipeline_started",
                        "job_id": job_id,
                    })
                break

    except WebSocketDisconnect:
        print("Twilio stream disconnected")
        await manager.on_hangup()
    except Exception as e:
        print(f"Error in Twilio stream: {e}")
        await manager.on_hangup()
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
