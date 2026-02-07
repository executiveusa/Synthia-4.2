"""
Synthia 4.2 - Celery Task Definitions

All async background tasks: pipeline execution, content generation,
notifications, health checks. Celery Beat schedule for cron jobs.

Docker runs: celery -A tasks.celery_app worker --loglevel=info
             celery -A tasks.celery_app beat --loglevel=info
"""

import os
import asyncio
import logging
from celery import Celery

logger = logging.getLogger(__name__)

# ─── Celery App ───────────────────────────────────────────────

celery_app = Celery(
    "synthia",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0"),
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)


# ─── Helper: run async in sync Celery task ────────────────────

def _run_async(coro):
    """Run an async coroutine from a sync Celery task."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(asyncio.run, coro).result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


# ─── Tasks ────────────────────────────────────────────────────

@celery_app.task(name="synthia.health_check")
def health_check():
    """Simple health check task."""
    return {"status": "ok", "service": "synthia-celery"}


@celery_app.task(name="synthia.run_pipeline", bind=True, max_retries=2)
def run_pipeline(self, job_id: str):
    """Execute the full agent orchestration pipeline for a job."""
    try:
        from orchestration.state import JobStore
        from orchestration.pipeline import SequentialPipeline

        store = JobStore()
        job = store.get(job_id)
        if not job:
            logger.error("Job %s not found", job_id)
            return {"status": "error", "message": f"Job {job_id} not found"}

        pipeline = SequentialPipeline()
        result = _run_async(pipeline.execute(job))

        return {
            "status": result.status,
            "job_id": result.job_id,
            "steps": len(result.results_per_step),
        }
    except Exception as exc:
        logger.exception("Pipeline task failed for job %s", job_id)
        raise self.retry(exc=exc, countdown=30)


@celery_app.task(name="synthia.generate_daily_content")
def generate_daily_content():
    """Generate daily Yappyverse content (comics + shorts)."""
    try:
        from yappyverse.characters import CharacterManager
        from yappyverse.story_engine import StoryEngine
        from yappyverse.world_model import WorldModel
        from yappyverse.content_pipeline import ComicPipeline, ShortsPipeline, ContentScheduler

        cm = CharacterManager()
        wm = WorldModel()
        se = StoryEngine(cm)
        cp = ComicPipeline(cm, se, wm)
        sp = ShortsPipeline(cm, se)
        scheduler = ContentScheduler(cp, sp)

        job_ids = scheduler.generate_daily_content()
        logger.info("Daily content generated: %d jobs", len(job_ids))
        return {"status": "ok", "jobs": job_ids}
    except Exception as e:
        logger.error("Daily content generation failed: %s", e)
        return {"status": "error", "message": str(e)}


@celery_app.task(name="synthia.send_digest_notification")
def send_digest_notification():
    """Send weekly digest notification."""
    try:
        from services.notifications import get_notification_service
        ns = get_notification_service()

        msg = (
            "📊 *Synthia Weekly Digest*\n\n"
            "Here's your weekly summary from The Pauli Effect.\n"
            "Check the dashboard for full details."
        )
        _run_async(ns._broadcast(msg))
        return {"status": "ok"}
    except Exception as e:
        logger.error("Digest notification failed: %s", e)
        return {"status": "error", "message": str(e)}


# ─── Celery Beat Schedule (cron jobs) ─────────────────────────

celery_app.conf.beat_schedule = {
    "daily-content": {
        "task": "synthia.generate_daily_content",
        "schedule": {
            "__type__": "crontab",
            "hour": 9,
            "minute": 0,
        },
    },
    "weekly-digest": {
        "task": "synthia.send_digest_notification",
        "schedule": {
            "__type__": "crontab",
            "hour": 8,
            "minute": 0,
            "day_of_week": 1,  # Monday
        },
    },
    "health-check": {
        "task": "synthia.health_check",
        "schedule": 300.0,  # every 5 minutes
    },
}

# Convert schedule dicts to actual crontab objects
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    "daily-content": {
        "task": "synthia.generate_daily_content",
        "schedule": crontab(hour=9, minute=0),
    },
    "weekly-digest": {
        "task": "synthia.send_digest_notification",
        "schedule": crontab(hour=8, minute=0, day_of_week=1),
    },
    "health-check": {
        "task": "synthia.health_check",
        "schedule": 300.0,
    },
}
