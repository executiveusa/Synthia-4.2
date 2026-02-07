from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import ollama
import io
from PIL import Image
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import Synthia modules
from api import skills_router
from api.yappyverse import router as yappyverse_router
from skills.registry import get_skill, list_skills
from skills.workflows import get_workflow, list_workflows
from skills.quality import validate_code, get_quality_summary
from services import get_voice_service, VoiceType
from services.voice import LanguageCode, VOICE_TYPE_LANGUAGE_MAP
from api.orchestration import router as orchestration_router

app = FastAPI(
    title="Synthia 4.2 - The Pauli Effect",
    description="Synthia: AI Agent for The Pauli Effect. Manages coding and frontend design.",
    version="4.2.0"
)

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(skills_router)
app.include_router(yappyverse_router)
app.include_router(orchestration_router)

# Models
class VoiceSynthesizeRequest(BaseModel):
    text: str
    voice: str = "pauli_default"

class AgentQueryRequest(BaseModel):
    query: str
    skill_id: Optional[str] = None
    context: Optional[dict] = None

class GenerateResponse(BaseModel):
    code: str
    description: str

@app.get("/health")
async def health_check():
    return {"status": "ok", "service": "Synthia 4.2 Backend"}

@app.post("/generate", response_model=GenerateResponse)
async def generate_code(
    file: UploadFile = File(...),
    vision_model: str = "moondream",
    code_model: str = "qwen2.5-coder:1.5b"
):
    """
    Takes an uploaded image (screenshot) and generates React code using local LLMs.
    """
    
    # 1. Validate Image
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try:
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Convert image to bytes for Ollama
        img_byte_arr = io.BytesIO()
        image.save(img_byte_arr, format=image.format)
        img_bytes = img_byte_arr.getvalue()

        # 2. Vision Step: Describe the UI
        print(f"👀 Analyzing image with {vision_model}...")
        
        # Read vision system prompt from file
        try:
            with open("prompts/vision_system.md", "r", encoding="utf-8") as f:
                vision_system = f.read().strip()
        except FileNotFoundError:
            print("⚠️ Vision system prompt file not found. Using default.")
            vision_system = "You are an expert UI/UX Designer with a keen eye for technical detail. accurately describe layout, colors, and typography."

        vision_user_content = "Describe this UI in technical detail. List the layout components (header, sidebar, main content), specific colors (approximate hex), typography style, and any interactive elements (buttons, inputs). Be precise."
        
        vision_response = ollama.chat(
            model=vision_model,
            messages=[
                {'role': 'system', 'content': vision_system},
                {
                    'role': 'user',
                    'content': vision_user_content,
                    'images': [img_bytes]
                }
            ]
        )
        description = vision_response['message']['content']
        print(f"✅ Description generated: {description[:100]}...")

        # 3. Code Step: Generate React Code
        print(f"💻 Generating code with {code_model}...")
        
        # Read code generation system prompt from file
        try:
            with open("prompts/code_gen_system.md", "r", encoding="utf-8") as f:
                system_prompt = f.read().strip()
        except FileNotFoundError:
             print("⚠️ Code generation system prompt file not found. Using default.")
             system_prompt = "You are an expert Frontend Developer. Build the React component described by the user."

        user_prompt = f"""UI Description:
{description}"""

        code_response = ollama.chat(
            model=code_model,
            messages=[
                {'role': 'system', 'content': system_prompt},
                {'role': 'user', 'content': user_prompt}
            ]
        )
        code = code_response['message']['content']
        
        # Clean up markdown if present
        code = code.replace("```jsx", "").replace("```tsx", "").replace("```", "")
        
        print("✅ Code generated!")

        return GenerateResponse(code=code, description=description)

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# ═════════════════════════════════════════════════════════════════
# Synthia/Pauli Agent Endpoints
# ═════════════════════════════════════════════════════════════════

@app.get("/")
async def root():
    """Root endpoint with system info."""
    return {
        "name": "Synthia",
        "version": "4.2.0",
        "status": "operational",
        "agent_name": "Synthia",
        "organization": "The Pauli Effect",
        "role": "Coding and Frontend Design Lead",
        "languages": ["es", "en", "hi", "sr"],
        "capabilities": [
            "voice_collaboration",
            "voice_calls_twilio",
            "code_generation",
            "frontend_design",
            "awwwards_patterns",
            "skill_execution",
            "workflow_automation",
            "quality_validation",
            "agent_orchestration",
            "notification_whatsapp_telegram",
            "multilingual_communication"
        ],
        "endpoints": {
            "health": "/health",
            "skills": "/skills/list",
            "workflows": "/skills/workflows/list",
            "generate": "/generate",
            "voice_synthesize": "/voice/synthesize",
            "voice_call": "/voice/call",
            "agent_query": "/agent/query",
            "orchestration_start": "/orchestration/start",
            "patterns_recommend": "/patterns/recommend",
            "ws_jobs": "/ws/jobs"
        }
    }

@app.post("/agent/query")
async def agent_query(request: AgentQueryRequest):
    """
    Main Pauli agent query endpoint.
    Processes natural language requests and routes to appropriate skills.
    """
    try:
        # If skill_id specified, use that skill
        if request.skill_id:
            skill = get_skill(request.skill_id)
            if not skill:
                raise HTTPException(status_code=404, detail=f"Skill '{request.skill_id}' not found")
            
            return {
                "status": "success",
                "skill_used": skill.skill_id,
                "response": f"Executing {skill.display_name} skill for: {request.query}",
                "automation_level": skill.automation_level.value,
                "approval_required": skill.approval_required
            }
        
        # Otherwise, use intent recognition to route
        # In production, this would use Claude/OpenAI to determine intent
        query_lower = request.query.lower()
        
        # Simple keyword routing (replace with proper intent classification)
        if any(word in query_lower for word in ["design", "ui", "ux", "wireframe", "mockup"]):
            skill = get_skill("ui-ux-design-master")
        elif any(word in query_lower for word in ["code", "build", "create", "component", "page"]):
            skill = get_skill("web-artifacts-builder-plus")
        elif any(word in query_lower for word in ["deploy", "host", "server", "vercel", "coolify"]):
            skill = get_skill("deployment-devops-orchestrator")
        elif any(word in query_lower for word in ["market", "campaign", "social", "email", "ads"]):
            skill = get_skill("marketing-growth-engine")
        elif any(word in query_lower for word in ["voice", "speak", "audio", "sound"]):
            return {
                "status": "success",
                "skill_used": "voice_collaboration",
                "response": "I can help with voice synthesis. Use /voice/synthesize endpoint.",
                "automation_level": "full",
                "approval_required": False
            }
        else:
            # Default to general conversation
            return {
                "status": "success",
                "skill_used": None,
                "response": f"¡Hola!我是 Synthia from The Pauli Effect. I received your query: '{request.query}'. I can help with coding, frontend design, and creative projects in Spanish, English, Hindi, or Serbian.",
                "automation_level": "human",
                "approval_required": False,
                "suggested_skills": [s.skill_id for s in list_skills()[:5]]
            }
        
        return {
            "status": "success",
            "skill_used": skill.skill_id,
            "response": f"I'll use the {skill.display_name} skill to help with: {request.query}",
            "automation_level": skill.automation_level.value,
            "approval_required": skill.approval_required,
            "skill_description": skill.description,
            "when_to_use": skill.when_to_use[:3]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice/synthesize")
async def voice_synthesize(request: VoiceSynthesizeRequest):
    """Synthesize text to speech using Pauli's voice."""
    try:
        voice_service = get_voice_service()
        
        # Map voice string to VoiceType
        voice_map = {
            "pauli_default": VoiceType.PAULI_DEFAULT,
            "professional_female": VoiceType.PROFESSIONAL_FEMALE,
            "professional_male": VoiceType.PROFESSIONAL_MALE,
            "warm": VoiceType.WARM_CONVERSATIONAL,
            "energetic": VoiceType.ENERGETIC_MALE,
        }
        voice_type = voice_map.get(request.voice, VoiceType.PAULI_DEFAULT)
        
        # Resolve VoiceType to LanguageCode for the synthesize call
        lang = VOICE_TYPE_LANGUAGE_MAP.get(voice_type, LanguageCode.ENGLISH)
        audio_data = await voice_service.synthesize(request.text, lang)
        
        return StreamingResponse(
            io.BytesIO(audio_data),
            media_type="audio/mpeg",
            headers={"Content-Disposition": "attachment; filename=pauli_speech.mp3"}
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/training/dataset")
async def get_training_dataset():
    """Get Synthia training dataset info."""
    training_path = "training/synthia_training_dataset.jsonl"
    
    if not os.path.exists(training_path):
        return {
            "status": "not_found",
            "message": "Training dataset not found",
            "path": training_path
        }
    
    # Count lines in file
    with open(training_path, 'r', encoding='utf-8') as f:
        line_count = sum(1 for _ in f)
    
    return {
        "status": "available",
        "path": training_path,
        "examples": line_count,
        "format": "JSONL (OpenAI fine-tuning format)",
        "description": "Conversational training data for Synthia/Pauli agent fine-tuning"
    }

@app.get("/system/info")
async def system_info():
    """Get system configuration and status."""
    return {
        "agent": {
            "name": os.getenv("AGENT_NAME", "Pauli"),
            "version": "4.2.0",
            "voice_enabled": os.getenv("ENABLE_VOICE_COLLABORATION", "true").lower() == "true",
            "default_voice": os.getenv("DEFAULT_VOICE_TYPE", "pauli_default"),
        },
        "features": {
            "awwwards_scraping": os.getenv("ENABLE_AWWWARDS_SCRAPING", "true").lower() == "true",
            "agent_lightning": os.getenv("ENABLE_AGENT_LIGHTNING", "true").lower() == "true",
            "auto_deployment": os.getenv("ENABLE_AUTO_DEPLOYMENT", "false").lower() == "true",
            "mcp_tools": os.getenv("ENABLE_MCP_TOOLS", "true").lower() == "true",
        },
        "skills": {
            "total": len(list_skills()),
            "categories": list(set(s.category.value for s in list_skills()))
        },
        "workflows": {
            "total": len(list_workflows()),
            "available": [w.workflow_id for w in list_workflows()]
        }
    }

# ═════════════════════════════════════════════════════════════════
# Voice Call Endpoints (Twilio integration)
# ═════════════════════════════════════════════════════════════════

class VoiceCallRequest(BaseModel):
    phone_number: str

@app.post("/voice/call")
async def initiate_voice_call(request: VoiceCallRequest):
    """Initiate an outbound voice call to the client."""
    try:
        from services.twilio_service import get_twilio_service
        twilio = get_twilio_service()
        if not twilio.is_available:
            raise HTTPException(status_code=503, detail="Twilio not configured")
        call_sid = twilio.initiate_call(request.phone_number)
        return {"status": "call_initiated", "call_sid": call_sid}
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/voice/call/status")
async def voice_call_status(request: dict):
    """Twilio call status webhook callback."""
    return {"received": True, "status": request.get("CallStatus", "unknown")}


# ═════════════════════════════════════════════════════════════════
# WebSocket: Dashboard Job Status Stream
# ═════════════════════════════════════════════════════════════════

from fastapi import WebSocket, WebSocketDisconnect

_dashboard_clients: list[WebSocket] = []

@app.websocket("/ws/jobs")
async def websocket_job_status(websocket: WebSocket):
    """WebSocket endpoint for real-time job status updates."""
    await websocket.accept()
    _dashboard_clients.append(websocket)
    try:
        while True:
            # Keep connection alive, listen for client messages
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except WebSocketDisconnect:
        _dashboard_clients.remove(websocket)


# ═════════════════════════════════════════════════════════════════
# Awwwards Pattern Recommendation Endpoint
# ═════════════════════════════════════════════════════════════════

@app.get("/patterns/recommend")
async def recommend_patterns(niche: str = "saas", page_type: str = "landing", limit: int = 5):
    """Recommend Awwwards patterns for a given niche and page type."""
    from skills.awwwards_patterns import recommend_patterns as _recommend
    patterns = _recommend(niche, page_type, max_results=limit)
    return {
        "niche": niche,
        "page_type": page_type,
        "count": len(patterns),
        "patterns": [p.to_dict() for p in patterns],
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
