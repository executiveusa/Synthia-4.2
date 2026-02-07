"""
Synthia 4.2 - Skills Registry

Central registry for all Synthia skills. Each skill defines its capabilities,
automation level, required tools, and approval requirements.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class AutomationLevel(str, Enum):
    FULL = "full"              # 95%+ automation
    HIGH = "high"              # 80-95% with approval points
    MEDIUM = "medium"          # 50-80% strategic decisions required
    HUMAN_IN_LOOP = "human"    # 30-50% continuous collaboration


class SkillCategory(str, Enum):
    DESIGN = "design"
    DEVELOPMENT = "development"
    DEPLOYMENT = "deployment"
    MARKETING = "marketing"
    FINANCE = "finance"
    CONTENT = "content"
    OPERATIONS = "operations"
    RELATIONSHIPS = "relationships"


@dataclass
class Skill:
    skill_id: str
    display_name: str
    category: SkillCategory
    automation_level: AutomationLevel
    description: str
    when_to_use: list[str] = field(default_factory=list)
    tools_required: list[str] = field(default_factory=list)
    approval_required: bool = False
    system_prompt_path: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "skill_id": self.skill_id,
            "display_name": self.display_name,
            "category": self.category.value,
            "automation_level": self.automation_level.value,
            "description": self.description,
            "when_to_use": self.when_to_use,
            "tools_required": self.tools_required,
            "approval_required": self.approval_required,
        }


# ─── SKILL DEFINITIONS ───────────────────────────────────────────────

SKILLS: dict[str, Skill] = {}


def register_skill(skill: Skill) -> None:
    SKILLS[skill.skill_id] = skill


def get_skill(skill_id: str) -> Optional[Skill]:
    return SKILLS.get(skill_id)


def list_skills(category: Optional[SkillCategory] = None) -> list[Skill]:
    if category:
        return [s for s in SKILLS.values() if s.category == category]
    return list(SKILLS.values())


# ─── REGISTER ALL SKILLS ─────────────────────────────────────────────

register_skill(Skill(
    skill_id="ui-ux-design-master",
    display_name="UI/UX Design Master",
    category=SkillCategory.DESIGN,
    automation_level=AutomationLevel.HIGH,
    description="End-to-end product/UI/UX partner. Component analysis, flow design, wireframes, UX specs, accessibility, performance, and UDIP compliance.",
    when_to_use=[
        "Product design requests",
        "Component analysis and audits",
        "UX strategy and user journey design",
        "Design system work and token generation",
        "Accessibility audits (WCAG)",
        "Performance optimization",
        "Awwwards trend research",
    ],
    tools_required=["ui-ux-pro-max", "figma-api", "awwwards-scraper"],
    approval_required=True,
    system_prompt_path="prompts/skills/ui_ux_design_master.md",
))

register_skill(Skill(
    skill_id="web-artifacts-builder-plus",
    display_name="Web Artifacts Builder+",
    category=SkillCategory.DEVELOPMENT,
    automation_level=AutomationLevel.FULL,
    description="Production React/Next.js component generation with shadcn/ui, Three.js, GSAP/Framer Motion, multi-page flows, and social media artifacts.",
    when_to_use=[
        "Build production components from designs",
        "Generate landing pages, dashboards, portfolios",
        "Create social media campaign artifacts",
        "Build interactive 3D web experiences",
    ],
    tools_required=["ollama", "code-gen"],
    approval_required=False,
    system_prompt_path="prompts/skills/web_artifacts_builder.md",
))

register_skill(Skill(
    skill_id="deployment-devops-orchestrator",
    display_name="Deployment & DevOps Orchestrator",
    category=SkillCategory.DEPLOYMENT,
    automation_level=AutomationLevel.HIGH,
    description="Coolify/Vercel deployment strategy, Docker configs, CI/CD pipelines, safe rollout strategies, and ops runbooks.",
    when_to_use=[
        "Deploy to staging or production",
        "Generate Docker configurations",
        "Set up CI/CD pipelines",
        "Incident response and rollback",
    ],
    tools_required=["docker", "coolify-api", "vercel-api"],
    approval_required=True,
    system_prompt_path="prompts/skills/deployment_devops.md",
))

register_skill(Skill(
    skill_id="marketing-growth-engine",
    display_name="Marketing & Growth Engine",
    category=SkillCategory.MARKETING,
    automation_level=AutomationLevel.HIGH,
    description="Full-funnel marketing campaigns: landing pages, email sequences, social posts. Mexico City market specialization.",
    when_to_use=[
        "Plan marketing campaigns",
        "Create landing page copy",
        "Generate email sequences",
        "Social media content strategy",
    ],
    tools_required=["analytics", "social-api", "email-api"],
    approval_required=True,
))

register_skill(Skill(
    skill_id="fundraising-ir-specialist",
    display_name="Fundraising & IR Specialist",
    category=SkillCategory.FINANCE,
    automation_level=AutomationLevel.MEDIUM,
    description="Pitch decks, investor narratives, data room outlines. Conservative scenario-based projections.",
    when_to_use=[
        "Prepare pitch decks",
        "Draft investor updates",
        "Create data room materials",
        "Investor email outreach",
    ],
    tools_required=["finance-models", "crm"],
    approval_required=True,
))

register_skill(Skill(
    skill_id="finance-ops-analyst",
    display_name="Finance & Ops Analyst",
    category=SkillCategory.FINANCE,
    automation_level=AutomationLevel.MEDIUM,
    description="Assumption-driven financial modeling, budget/cash flow/runway analysis, dashboards and reports.",
    when_to_use=[
        "Financial modeling and projections",
        "Budget and runway analysis",
        "Dashboard generation",
        "Expense reporting",
    ],
    tools_required=["finance-models"],
    approval_required=True,
))

register_skill(Skill(
    skill_id="avatar-comic-scriptwriter",
    display_name="Avatar & Comic Scriptwriter",
    category=SkillCategory.CONTENT,
    automation_level=AutomationLevel.FULL,
    description="Canon bible maintenance, episode scripts, dialog, story arcs, short-form social content.",
    when_to_use=[
        "Write comic scripts",
        "Create character dialog",
        "Plan story arcs",
        "Social media short-form content",
    ],
    tools_required=["content-gen"],
    approval_required=False,
))

register_skill(Skill(
    skill_id="algo-art-synthia",
    display_name="Algorithmic Art Generator",
    category=SkillCategory.CONTENT,
    automation_level=AutomationLevel.FULL,
    description="Algorithmic art via p5.js, Three.js, WebGL with seeded randomness. Social media assets, web animations, backgrounds.",
    when_to_use=[
        "Generate visual assets",
        "Create web animations",
        "Build social media graphics",
        "Design backgrounds and textures",
    ],
    tools_required=["canvas-gen"],
    approval_required=False,
))

register_skill(Skill(
    skill_id="brand-synthia",
    display_name="Synthia Brand Guidelines",
    category=SkillCategory.DESIGN,
    automation_level=AutomationLevel.FULL,
    description="Brand guidelines, design tokens, color system, typography, component patterns, tone-of-voice.",
    when_to_use=[
        "Check brand consistency",
        "Generate design tokens",
        "Update brand guidelines",
        "Verify component patterns",
    ],
    tools_required=["design-system"],
    approval_required=False,
))

register_skill(Skill(
    skill_id="gratitude-department",
    display_name="Gratitude Department",
    category=SkillCategory.RELATIONSHIPS,
    automation_level=AutomationLevel.HIGH,
    description="Dedicated relationship engine. Personalized thank-you notes, shoutouts, gift ideas, recurring gratitude cadences.",
    when_to_use=[
        "Send thank-you notes",
        "Plan appreciation events",
        "Track relationship milestones",
        "Community recognition",
    ],
    tools_required=["crm", "email-api"],
    approval_required=True,
))

register_skill(Skill(
    skill_id="internal-comms-synthia",
    display_name="Internal Communications",
    category=SkillCategory.OPERATIONS,
    automation_level=AutomationLevel.FULL,
    description="Status docs, incident reports, investor updates, partner communications. Automated weekly updates.",
    when_to_use=[
        "Write status updates",
        "Draft incident reports",
        "Create weekly summaries",
        "Document changes",
    ],
    tools_required=["docs-gen"],
    approval_required=False,
))

register_skill(Skill(
    skill_id="skill-creator-synthia",
    display_name="Skill Creator (Meta)",
    category=SkillCategory.OPERATIONS,
    automation_level=AutomationLevel.FULL,
    description="Meta-skill for creating new Cloud Skills. Follows schema defined in skills index.",
    when_to_use=[
        "Create new skills",
        "Update existing skill definitions",
        "Generate skill documentation",
    ],
    tools_required=["skill-schema"],
    approval_required=False,
))

register_skill(Skill(
    skill_id="theme-factory-synthia",
    display_name="Theme Factory",
    category=SkillCategory.DESIGN,
    automation_level=AutomationLevel.FULL,
    description="Reusable design themes for all artifact types. Extract design tokens from code/Figma.",
    when_to_use=[
        "Generate new themes",
        "Extract tokens from designs",
        "Apply consistent theming",
        "Create theme variants",
    ],
    tools_required=["design-system", "figma-api"],
    approval_required=False,
))

register_skill(Skill(
    skill_id="mcp-builder-synthia",
    display_name="MCP Server Builder",
    category=SkillCategory.DEVELOPMENT,
    automation_level=AutomationLevel.FULL,
    description="Build MCP servers for Synthia ecosystem. Coolify, Vercel, financial/crypto APIs, email/CRM/marketing tools.",
    when_to_use=[
        "Build new MCP tool servers",
        "Integrate external APIs",
        "Create deployment automations",
    ],
    tools_required=["mcp-sdk"],
    approval_required=False,
))

register_skill(Skill(
    skill_id="crypto-web3-strategist",
    display_name="Crypto & Web3 Strategist",
    category=SkillCategory.FINANCE,
    automation_level=AutomationLevel.MEDIUM,
    description="Conceptual tokenomics, user journeys integrating crypto safely, regulatory/security caveats. No direct transactions.",
    when_to_use=[
        "Design tokenomics",
        "Plan Web3 integrations",
        "Evaluate crypto strategies",
    ],
    tools_required=["research"],
    approval_required=True,
))

register_skill(Skill(
    skill_id="canvas-design-synthia",
    display_name="Canvas Design Generator",
    category=SkillCategory.CONTENT,
    automation_level=AutomationLevel.FULL,
    description="Static design generation for campaigns, comics, investor materials. PNG/PDF exports optimized for target channels. Size presets for social, print, presentations.",
    when_to_use=[
        "Create static social media graphics",
        "Generate campaign visuals and ads",
        "Produce investor presentation slides",
        "Create print-ready materials",
        "Design comic panels and illustrations",
    ],
    tools_required=["canvas-gen", "design-system"],
    approval_required=False,
))

register_skill(Skill(
    skill_id="slack-gif-synthia",
    display_name="Slack/Discord GIF Creator",
    category=SkillCategory.CONTENT,
    automation_level=AutomationLevel.FULL,
    description="Short animations for Slack/Discord team communication. File size and dimension constraints for chat platforms. Brand-aligned motion graphics.",
    when_to_use=[
        "Create team reaction GIFs",
        "Build branded Slack animations",
        "Generate Discord stickers and emotes",
        "Make short motion graphics for chat",
    ],
    tools_required=["canvas-gen", "animation-export"],
    approval_required=False,
))
