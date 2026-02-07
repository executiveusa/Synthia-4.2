"""
Synthia 4.2 - Sequential Pipeline Runner

Chains agents: Designer → Coder → Reviewer → QA.
Persists state after each step via JobStore.
Sends notifications on completion/failure.
"""

import logging
from datetime import datetime

from .state import JobState, JobStore
from .agents import DesignerAgent, CoderAgent, ReviewerAgent, QAAgent

logger = logging.getLogger(__name__)


class SequentialPipeline:
    """Execute agents sequentially, passing accumulated context through each."""

    def __init__(self):
        self.agents = [
            DesignerAgent(),
            CoderAgent(),
            ReviewerAgent(),
            QAAgent(),
        ]
        self.store = JobStore()

    async def execute(self, job: JobState) -> JobState:
        """Run the full pipeline for a job."""
        job.status = "running"
        job.started_at = datetime.utcnow().isoformat()
        self.store.save(job)

        # Build initial context from the job brief
        context = {
            "brief": job.brief,
            "niche": job.niche,
            "page_type": job.page_type,
            "results_per_step": {},
        }

        for agent in self.agents:
            job.current_agent = agent.name
            job.status = "running"
            self.store.save(job)

            logger.info("Pipeline %s: running agent '%s'", job.job_id, agent.name)

            try:
                result = await agent.execute(context)

                # Store result in context for next agent
                context["results_per_step"][agent.name] = result
                job.results_per_step[agent.name] = result

                if result.get("status") == "error":
                    logger.error(
                        "Pipeline %s: agent '%s' failed: %s",
                        job.job_id, agent.name, result.get("error"),
                    )
                    # Continue pipeline even on non-fatal errors
                    # Only stop if it's the coder (no code = nothing to review)
                    if agent.name == "coder":
                        job.status = "failed"
                        job.error = f"Coder agent failed: {result.get('error')}"
                        job.completed_at = datetime.utcnow().isoformat()
                        self.store.save(job)
                        await self._notify_failure(job)
                        return job

                job.status = "step_complete"
                self.store.save(job)

                # Push status to dashboard if available
                await self._push_status(job)

            except Exception as e:
                logger.exception("Pipeline %s: unhandled error in '%s'", job.job_id, agent.name)
                job.status = "failed"
                job.error = f"Unhandled error in {agent.name}: {str(e)}"
                job.completed_at = datetime.utcnow().isoformat()
                self.store.save(job)
                await self._notify_failure(job)
                return job

        # All agents completed
        job.status = "done"
        job.current_agent = None
        job.completed_at = datetime.utcnow().isoformat()
        self.store.save(job)

        await self._notify_success(job)
        logger.info("Pipeline %s: completed successfully", job.job_id)
        return job

    async def _notify_success(self, job: JobState) -> None:
        """Send completion notification."""
        try:
            from services.notifications import get_notification_service
            ns = get_notification_service()
            await ns.notify_job_complete(job)
        except Exception as e:
            logger.warning("Failed to send success notification: %s", e)

    async def _notify_failure(self, job: JobState) -> None:
        """Send failure notification."""
        try:
            from services.notifications import get_notification_service
            ns = get_notification_service()
            await ns.notify_job_failed(job)
        except Exception as e:
            logger.warning("Failed to send failure notification: %s", e)

    async def _push_status(self, job: JobState) -> None:
        """Push status update to dashboard."""
        try:
            from services.dashboard_sync import get_dashboard_sync
            ds = get_dashboard_sync()
            await ds.push_job_status(job)
        except Exception as e:
            logger.debug("Dashboard sync unavailable: %s", e)


__all__ = ["SequentialPipeline"]
