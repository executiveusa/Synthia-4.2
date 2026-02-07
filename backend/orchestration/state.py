"""
Synthia 4.2 - Job State Management

Tracks pipeline execution state with Redis-backed persistence.
"""

import json
import uuid
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Optional, Any

from cache import get_cache


@dataclass
class JobState:
    job_id: str
    status: str  # pending | running | step_complete | done | failed
    brief: str
    niche: str
    page_type: str
    results_per_step: dict = field(default_factory=dict)
    current_agent: Optional[str] = None
    started_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "JobState":
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})

    @classmethod
    def create(cls, brief: str, niche: str, page_type: str) -> "JobState":
        return cls(
            job_id=str(uuid.uuid4())[:12],
            status="pending",
            brief=brief,
            niche=niche,
            page_type=page_type,
        )


class JobStore:
    """Redis-backed job state store."""

    PREFIX = "synthia:job:"
    TTL = 86400  # 24 hours

    def __init__(self):
        self._cache = get_cache()

    def save(self, job: JobState) -> None:
        key = f"{self.PREFIX}{job.job_id}"
        self._cache.set(key, job.to_dict(), ttl=self.TTL)

    def get(self, job_id: str) -> Optional[JobState]:
        key = f"{self.PREFIX}{job_id}"
        data = self._cache.get(key)
        if data:
            return JobState.from_dict(data)
        return None

    def list_jobs(self, limit: int = 50) -> list[JobState]:
        """List recent jobs (from in-memory cache fallback)."""
        # Redis SCAN would be used in production; for now return empty
        return []

    def update_status(self, job_id: str, status: str, **kwargs: Any) -> Optional[JobState]:
        job = self.get(job_id)
        if not job:
            return None
        job.status = status
        for k, v in kwargs.items():
            if hasattr(job, k):
                setattr(job, k, v)
        self.save(job)
        return job


__all__ = ["JobState", "JobStore"]
