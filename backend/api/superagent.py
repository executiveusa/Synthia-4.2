"""
🚀 SUPERAGENT ORCHESTRATION API 🚀

Unified API for all superagent capabilities
Agent Swarm, Self-Healing, HuggingFace, Revenue Tracking
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime

# Import all superagent components
from orchestration.agents import DesignerAgent, CoderAgent, ReviewerAgent, QAAgent
from orchestration.pipeline import AgentPipeline
from orchestration.state import JobState, JobStore
from monitoring.self_healing import get_self_healing_monitor, HealthStatus
from mcp.huggingface_server import get_hf_server
from dashboard.revenue_tracker import get_revenue_tracker, RevenueSource, ProjectStatus
from services.twilio_service import get_twilio_service
from services.voice_call import VoiceCallManager

router = APIRouter(prefix="/superagent", tags=["superagent"])


# ============ Pydantic Models ============

class PipelineRequest(BaseModel):
    brief: str
    niche: str = "saas"
    page_type: str = "landing"
    client_name: Optional[str] = None
    project_value: Optional[float] = None


class VoiceCallRequest(BaseModel):
    phone_number: str
    client_name: Optional[str] = None


class RevenueEntryRequest(BaseModel):
    source: str
    amount_usd: float
    description: str
    client_name: Optional[str] = None
    project_id: Optional[str] = None
    status: str = "paid"
    expenses: float = 0.0
    tags: List[str] = []


class HFGenerateRequest(BaseModel):
    prompt: str
    model_key: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None


# ============ Agent Swarm Endpoints ============

@router.post("/pipeline/run")
async def run_pipeline(request: PipelineRequest, background_tasks: BackgroundTasks):
    """Run the full agent swarm pipeline"""
    try:
        # Create job
        from orchestration.state import JobState
        job = JobState.create(
            brief=request.brief,
            niche=request.niche,
            page_type=request.page_type
        )
        
        store = JobStore()
        store.save(job)
        
        # Track revenue if project value provided
        if request.project_value:
            tracker = get_revenue_tracker()
            tracker.add_revenue(
                source=RevenueSource.CLIENT_PROJECT,
                amount_usd=request.project_value,
                description=f"Project: {request.brief[:50]}...",
                client_name=request.client_name,
                project_id=job.job_id,
                status=ProjectStatus.IN_PROGRESS
            )
        
        # Run pipeline in background
        background_tasks.add_task(_execute_pipeline, job.job_id)
        
        return {
            "success": True,
            "job_id": job.job_id,
            "status": "started",
            "message": "Agent swarm pipeline initiated",
            "agents": ["designer", "coder", "reviewer", "qa"]
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def _execute_pipeline(job_id: str):
    """Execute pipeline in background"""
    try:
        from tasks import run_pipeline
        run_pipeline.delay(job_id)
    except Exception as e:
        print(f"Pipeline execution error: {e}")


@router.get("/pipeline/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get pipeline job status"""
    store = JobStore()
    job = store.get(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job.job_id,
        "status": job.status,
        "current_step": job.current_step,
        "progress": job.progress,
        "results": job.results,
        "created_at": job.created_at,
        "updated_at": job.updated_at
    }


# ============ Self-Healing Endpoints ============

@router.get("/health/system")
async def get_system_health():
    """Get overall system health from self-healing monitor"""
    monitor = get_self_healing_monitor()
    return monitor.get_system_health()


@router.get("/health/agents/{agent_name}")
async def get_agent_health(agent_name: str):
    """Get specific agent health"""
    monitor = get_self_healing_monitor()
    metric = await monitor.check_agent_health(agent_name)
    
    return {
        "agent": agent_name,
        "status": metric.status.value,
        "health_score": metric.value,
        "threshold": metric.threshold,
        "details": metric.details,
        "timestamp": metric.timestamp
    }


@router.get("/health/incidents")
async def get_incidents(status: Optional[str] = None):
    """Get healing incidents"""
    monitor = get_self_healing_monitor()
    return {"incidents": monitor.get_incidents(status)}


# ============ HuggingFace MCP Endpoints ============

@router.get("/hf/status")
async def get_hf_status():
    """Get HuggingFace MCP server status"""
    server = get_hf_server()
    return server.get_status()


@router.get("/hf/models")
async def list_hf_models():
    """List available HuggingFace models"""
    server = get_hf_server()
    return {"models": server.list_models()}


@router.post("/hf/generate")
async def hf_generate(request: HFGenerateRequest):
    """Generate text using HuggingFace model"""
    server = get_hf_server()
    result = await server.generate(
        prompt=request.prompt,
        model_key=request.model_key,
        max_tokens=request.max_tokens,
        temperature=request.temperature
    )
    return result


@router.post("/hf/models/{model_key}/load")
async def load_hf_model(model_key: str):
    """Load a HuggingFace model"""
    server = get_hf_server()
    success = await server.load_model(model_key)
    return {
        "success": success,
        "model": model_key,
        "message": f"Model {model_key} {'loaded' if success else 'failed to load'}"
    }


# ============ Voice Call Endpoints ============

@router.post("/voice/call")
async def initiate_voice_call(request: VoiceCallRequest):
    """Initiate outbound voice call via Twilio"""
    try:
        twilio = get_twilio_service()
        
        if not twilio.is_available:
            raise HTTPException(status_code=503, detail="Twilio not configured")
        
        call_sid = twilio.initiate_call(request.phone_number)
        
        return {
            "success": True,
            "call_sid": call_sid,
            "phone_number": request.phone_number,
            "status": "initiated",
            "message": "Call initiated. Synthia will discuss the project and create a pipeline job."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/voice/status")
async def get_voice_status():
    """Get voice service status"""
    twilio = get_twilio_service()
    
    return {
        "twilio_available": twilio.is_available,
        "phone_number": twilio.phone_number if twilio.is_available else None,
        "whatsapp_number": twilio.whatsapp_number if twilio.is_available else None
    }


# ============ Revenue Tracking Endpoints ============

@router.post("/revenue/add")
async def add_revenue_entry(request: RevenueEntryRequest):
    """Add a revenue entry"""
    tracker = get_revenue_tracker()
    
    entry = tracker.add_revenue(
        source=RevenueSource(request.source),
        amount_usd=request.amount_usd,
        description=request.description,
        client_name=request.client_name,
        status=ProjectStatus(request.status),
        expenses=request.expenses,
        tags=request.tags
    )
    
    return {
        "success": True,
        "entry_id": entry.entry_id,
        "amount": entry.amount_usd,
        "source": entry.source.value,
        "timestamp": entry.timestamp
    }


@router.get("/revenue/dashboard")
async def get_revenue_dashboard():
    """Get revenue dashboard summary"""
    tracker = get_revenue_tracker()
    return tracker.get_dashboard_summary()


@router.get("/revenue/yappyverse")
async def get_yappyverse_revenue():
    """Get Yappyverse-specific revenue metrics"""
    tracker = get_revenue_tracker()
    return tracker.get_yappyverse_metrics()


@router.get("/revenue/clients")
async def get_client_report(client_id: Optional[str] = None):
    """Get client revenue report"""
    tracker = get_revenue_tracker()
    return tracker.get_client_report(client_id)


# ============ Superagent Status ============

@router.get("/status")
async def get_superagent_status():
    """Get complete superagent status"""
    
    # Check all components
    monitor = get_self_healing_monitor()
    hf_server = get_hf_server()
    tracker = get_revenue_tracker()
    twilio = get_twilio_service()
    
    return {
        "timestamp": datetime.now().isoformat(),
        "version": "4.2.0-superagent",
        "components": {
            "agent_swarm": {
                "status": "operational",
                "agents": ["designer", "coder", "reviewer", "qa"],
                "active_jobs": 0  # Would query from JobStore
            },
            "self_healing": {
                "status": monitor.get_system_health()["overall_status"],
                "health_score": monitor._calculate_healing_success_rate(),
                "open_incidents": len([i for i in monitor.incidents.values() if i.status == "open"])
            },
            "huggingface": {
                "status": "available" if hf_server.get_status()["transformers_available"] else "unavailable",
                "loaded_models": hf_server.get_status()["loaded_models"],
                "cuda_available": hf_server.get_status()["cuda_available"]
            },
            "voice_calls": {
                "status": "available" if twilio.is_available else "unavailable",
                "provider": "Twilio"
            },
            "revenue_tracking": {
                "status": "operational",
                "monthly_revenue": tracker.get_dashboard_summary()["monthly"]["revenue"],
                "total_clients": len(tracker.clients)
            }
        },
        "capabilities": [
            "agent_swarm_orchestration",
            "self_healing_monitoring",
            "local_llm_inference",
            "voice_call_automation",
            "revenue_analytics",
            "yappyverse_content_generation"
        ]
    }


@router.get("/")
async def superagent_root():
    """Superagent API root"""
    return {
        "name": "Synthia Superagent",
        "version": "4.2.0",
        "description": "Aggressive Full Superagent with Agent Swarm, Self-Healing, HuggingFace, Voice, and Revenue Tracking",
        "endpoints": [
            "/superagent/status",
            "/superagent/pipeline/run",
            "/superagent/health/system",
            "/superagent/hf/status",
            "/superagent/voice/call",
            "/superagent/revenue/dashboard"
        ],
        "controller": "Pauli 'The Polyglot' Morelli",
        "universe": "The Yappyverse"
    }