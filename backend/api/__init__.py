"""Synthia API routes."""

from .skills import router as skills_router
from .orchestration import router as orchestration_router

__all__ = ["skills_router", "orchestration_router"]
