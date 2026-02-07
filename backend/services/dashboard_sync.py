"""
Synthia 4.2 - Dashboard Sync Service

Pushes job status + metrics to the dashboard-agent-swarm
via webhook or WebSocket broadcast.
"""

import os
import logging
from typing import Optional, Any

import httpx

logger = logging.getLogger(__name__)


class DashboardSync:
    """Push pipeline state to external dashboard."""

    def __init__(self):
        self.webhook_url = os.getenv("DASHBOARD_WEBHOOK_URL", "")

    @property
    def is_available(self) -> bool:
        return bool(self.webhook_url)

    async def push_job_status(self, job) -> bool:
        """Push job state to dashboard webhook."""
        if not self.is_available:
            return False

        payload = {
            "event": "job_status",
            "job_id": job.job_id,
            "status": job.status,
            "current_agent": job.current_agent,
            "niche": job.niche,
            "page_type": job.page_type,
            "steps_completed": len(job.results_per_step),
            "started_at": job.started_at,
            "completed_at": job.completed_at,
            "error": job.error,
        }
        return await self._post(payload)

    async def push_metric(self, name: str, value: Any) -> bool:
        """Push a single metric to dashboard."""
        if not self.is_available:
            return False

        payload = {
            "event": "metric",
            "name": name,
            "value": value,
        }
        return await self._post(payload)

    async def _post(self, payload: dict) -> bool:
        """POST JSON to webhook URL."""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(self.webhook_url, json=payload)
                resp.raise_for_status()
                return True
        except Exception as e:
            logger.debug("Dashboard push failed: %s", e)
            return False


# Singleton
_dashboard_sync: Optional[DashboardSync] = None


def get_dashboard_sync() -> DashboardSync:
    global _dashboard_sync
    if _dashboard_sync is None:
        _dashboard_sync = DashboardSync()
    return _dashboard_sync


__all__ = ["DashboardSync", "get_dashboard_sync"]
