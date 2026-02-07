"""
Synthia 4.2 - Agent Orchestration Engine

Sequential pipeline: Synthia → Designer → Coder → Reviewer → QA.
After a voice call, Synthia dispatches this pipeline to build autonomously.
"""

from .state import JobState, JobStore
from .agent_base import AgentBase
from .agents import DesignerAgent, CoderAgent, ReviewerAgent, QAAgent
from .pipeline import SequentialPipeline

__all__ = [
    "JobState",
    "JobStore",
    "AgentBase",
    "DesignerAgent",
    "CoderAgent",
    "ReviewerAgent",
    "QAAgent",
    "SequentialPipeline",
]
