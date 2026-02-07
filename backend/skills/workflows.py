"""
Synthia 4.2 - Multi-Skill Workflows (Flow Library)

Predefined sequences of skills that execute together for complex operations.
Each workflow defines trigger conditions, skill sequences, data requirements,
and human review points.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class WorkflowStep:
    skill_id: str
    description: str
    requires_approval: bool = False
    automation_ready: bool = True


@dataclass
class Workflow:
    workflow_id: str
    name: str
    trigger: str
    steps: list[WorkflowStep] = field(default_factory=list)
    data_required: list[str] = field(default_factory=list)
    tools: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "trigger": self.trigger,
            "steps": [
                {
                    "skill_id": s.skill_id,
                    "description": s.description,
                    "requires_approval": s.requires_approval,
                    "automation_ready": s.automation_ready,
                }
                for s in self.steps
            ],
            "data_required": self.data_required,
            "tools": self.tools,
        }


# ─── WORKFLOW DEFINITIONS ─────────────────────────────────────────────

WORKFLOWS: dict[str, Workflow] = {}


def register_workflow(w: Workflow) -> None:
    WORKFLOWS[w.workflow_id] = w


def get_workflow(workflow_id: str) -> Optional[Workflow]:
    return WORKFLOWS.get(workflow_id)


def list_workflows() -> list[Workflow]:
    return list(WORKFLOWS.values())


# ─── Flow 1: New Feature Launch ──────────────────────────────────────

register_workflow(Workflow(
    workflow_id="feature-launch",
    name="New Feature Launch",
    trigger="Feature completion milestone",
    steps=[
        WorkflowStep("ui-ux-design-master", "Generate UX specs and component designs"),
        WorkflowStep("web-artifacts-builder-plus", "Build production components"),
        WorkflowStep("deployment-devops-orchestrator", "Stage and deploy with monitoring", requires_approval=True),
        WorkflowStep("marketing-growth-engine", "Create launch campaign materials"),
        WorkflowStep("internal-comms-synthia", "Draft internal announcement and docs"),
    ],
    data_required=["Feature requirements", "Target audience", "Timeline"],
    tools=["Project repos", "Design system", "Coolify/Vercel", "Analytics"],
))

# ─── Flow 2: Fundraising Campaign ────────────────────────────────────

register_workflow(Workflow(
    workflow_id="fundraising-campaign",
    name="Fundraising Campaign",
    trigger="Scheduled fundraising push or investor meeting",
    steps=[
        WorkflowStep("finance-ops-analyst", "Update financial model and projections", requires_approval=True),
        WorkflowStep("fundraising-ir-specialist", "Refine pitch deck and investor materials", requires_approval=True),
        WorkflowStep("marketing-growth-engine", "Create supporting campaign content", requires_approval=True),
        WorkflowStep("gratitude-department", "Thank current supporters and warm introductions", requires_approval=True),
    ],
    data_required=["Current metrics", "Runway", "Investor targets"],
    tools=["Financial models", "CRM", "Email platforms"],
))

# ─── Flow 3: Content & Community Week ────────────────────────────────

register_workflow(Workflow(
    workflow_id="content-community-week",
    name="Content & Community Week",
    trigger="Weekly scheduled content push",
    steps=[
        WorkflowStep("avatar-comic-scriptwriter", "Generate episode scripts and social content"),
        WorkflowStep("algo-art-synthia", "Create visual assets and backgrounds"),
        WorkflowStep("theme-factory-synthia", "Apply consistent brand theming"),
        WorkflowStep("marketing-growth-engine", "Schedule and distribute content"),
        WorkflowStep("gratitude-department", "Feature community highlights and shoutouts"),
    ],
    data_required=["Content calendar", "Community engagement metrics"],
    tools=["Social platforms", "Design assets", "CRM"],
))

# ─── Flow 4: Design System Evolution ─────────────────────────────────

register_workflow(Workflow(
    workflow_id="design-system-evolution",
    name="Design System Evolution",
    trigger="Design trends update or brand refresh",
    steps=[
        WorkflowStep("ui-ux-design-master", "Analyze current Awwwards trends"),
        WorkflowStep("brand-synthia", "Update design tokens and guidelines", requires_approval=True),
        WorkflowStep("theme-factory-synthia", "Generate new theme variants"),
        WorkflowStep("web-artifacts-builder-plus", "Refactor components with new system"),
        WorkflowStep("internal-comms-synthia", "Document changes for team"),
    ],
    data_required=["Awwwards trend data", "Current design system"],
    tools=["Figma", "Codebase", "Design system configs"],
))

# ─── Flow 5: Agent Learning Cycle ────────────────────────────────────

register_workflow(Workflow(
    workflow_id="agent-learning-cycle",
    name="Agent Learning Cycle",
    trigger="Daily scheduled learning process",
    steps=[
        WorkflowStep("ui-ux-design-master", "Scrape and analyze Awwwards winners"),
        WorkflowStep("skill-creator-synthia", "Identify new patterns worth codifying"),
        WorkflowStep("mcp-builder-synthia", "Create new MCP tools for discovered needs"),
        WorkflowStep("internal-comms-synthia", "Generate daily learning report"),
    ],
    data_required=["Awwwards.com data", "Agent Lightning metrics"],
    tools=["Web scraping", "Pattern analysis", "Skill repository"],
))

# ─── Flow 6: Emergency Deployment Fix ────────────────────────────────

register_workflow(Workflow(
    workflow_id="emergency-fix",
    name="Emergency Deployment Fix",
    trigger="Production incident or critical bug",
    steps=[
        WorkflowStep("deployment-devops-orchestrator", "Analyze logs and identify root cause"),
        WorkflowStep("web-artifacts-builder-plus", "Generate fix (UI) or mcp-builder (backend)"),
        WorkflowStep("deployment-devops-orchestrator", "Deploy hotfix with rollback plan", requires_approval=True),
        WorkflowStep("internal-comms-synthia", "Draft incident report and post-mortem"),
    ],
    data_required=["Error logs", "Deployment history", "Affected users"],
    tools=["Coolify/Vercel", "Monitoring systems", "GitHub"],
))

# ─── Flow 7: Weekly Team Sync ────────────────────────────────────────

register_workflow(Workflow(
    workflow_id="weekly-team-sync",
    name="Weekly Team Sync",
    trigger="Every Monday morning",
    steps=[
        WorkflowStep("finance-ops-analyst", "Summarize weekly burn and runway"),
        WorkflowStep("marketing-growth-engine", "Report campaign performance"),
        WorkflowStep("deployment-devops-orchestrator", "Deployment summary and infra health"),
        WorkflowStep("gratitude-department", "Team wins and recognitions"),
        WorkflowStep("internal-comms-synthia", "Compile into weekly update email"),
    ],
    data_required=["Analytics", "Deployment logs", "CRM data"],
    tools=["All integrated systems"],
))

# ─── Flow 7b: Voice Collaboration Session ─────────────────────────────

register_workflow(Workflow(
    workflow_id="voice-collaboration",
    name="Voice Collaboration Session",
    trigger="Voice meeting or brainstorming session",
    steps=[
        WorkflowStep("gratitude-department", "Warm greeting and relationship context"),
        WorkflowStep("ui-ux-design-master", "Collaborative design exploration via voice"),
        WorkflowStep("web-artifacts-builder-plus", "Generate artifacts based on discussion"),
        WorkflowStep("internal-comms-synthia", "Create meeting notes and action items"),
    ],
    data_required=["Participant context", "Meeting agenda"],
    tools=["Voice synthesis/recognition APIs", "MCP Agent Mail"],
))

# ─── Flow 8: Social Media Campaign ───────────────────────────────────

register_workflow(Workflow(
    workflow_id="social-media-campaign",
    name="Social Media Campaign",
    trigger="Product launch or awareness campaign",
    steps=[
        WorkflowStep("marketing-growth-engine", "Define campaign strategy", requires_approval=True),
        WorkflowStep("avatar-comic-scriptwriter", "Create narrative content and scripts"),
        WorkflowStep("algo-art-synthia", "Generate visual assets"),
        WorkflowStep("web-artifacts-builder-plus", "Build landing pages and interactive elements"),
        WorkflowStep("gratitude-department", "Identify influencers and partners to engage"),
    ],
    data_required=["Campaign objectives", "Target audience", "Budget"],
    tools=["Social platforms", "Design tools", "Analytics"],
))

# ─── Flow 9: Quarterly Investor Update ───────────────────────────────

register_workflow(Workflow(
    workflow_id="quarterly-investor-update",
    name="Quarterly Investor Update",
    trigger="End of quarter",
    steps=[
        WorkflowStep("finance-ops-analyst", "Compile quarterly financials", requires_approval=True),
        WorkflowStep("marketing-growth-engine", "Summarize growth metrics", requires_approval=True),
        WorkflowStep("deployment-devops-orchestrator", "Technical milestones and infra updates", requires_approval=True),
        WorkflowStep("fundraising-ir-specialist", "Draft investor update and slide deck", requires_approval=True),
        WorkflowStep("gratitude-department", "Personalized notes to top investors", requires_approval=True),
    ],
    data_required=["Q metrics", "Product updates", "Financial data"],
    tools=["All systems", "Investor CRM"],
))
