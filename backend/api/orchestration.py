"""
Synthia 4.2 - Orchestration API

Endpoints to start agent pipelines, check status, and retrieve results.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from orchestration.state import JobState, JobStore

router = APIRouter(prefix="/orchestration", tags=["orchestration"])

_store = JobStore()


class PipelineStartRequest(BaseModel):
    brief: str
    niche: str = "saas"
    page_type: str = "landing"


class PipelineStartResponse(BaseModel):
    job_id: str
    status: str
    message: str


@router.post("/start", response_model=PipelineStartResponse)
async def start_pipeline(request: PipelineStartRequest):
    """Start a new agent orchestration pipeline."""
    job = JobState.create(
        brief=request.brief,
        niche=request.niche,
        page_type=request.page_type,
    )
    _store.save(job)

    # Dispatch to Celery for async execution
    try:
        from tasks import run_pipeline
        run_pipeline.delay(job.job_id)
    except Exception:
        # Fallback: run inline if Celery unavailable
        pass

    return PipelineStartResponse(
        job_id=job.job_id,
        status=job.status,
        message=f"Pipeline started for '{request.niche}' {request.page_type}",
    )


@router.get("/{job_id}")
async def get_pipeline_status(job_id: str):
    """Get current pipeline status."""
    job = _store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return job.to_dict()


@router.get("/{job_id}/result")
async def get_pipeline_result(job_id: str):
    """Get final pipeline results."""
    job = _store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if job.status not in ("done", "failed"):
        return {
            "job_id": job.job_id,
            "status": job.status,
            "message": f"Pipeline still running (current: {job.current_agent})",
        }
    return {
        "job_id": job.job_id,
        "status": job.status,
        "results": job.results_per_step,
        "error": job.error,
        "started_at": job.started_at,
        "completed_at": job.completed_at,
    }
