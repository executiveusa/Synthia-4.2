"""
Synthia Skills API Endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

from skills.registry import (
    get_skill, list_skills, SkillCategory,
    AutomationLevel, SKILLS
)
from skills.workflows import (
    get_workflow, list_workflows, WORKFLOWS
)
from skills.quality import validate_code, get_quality_summary

router = APIRouter(prefix="/skills", tags=["skills"])

# Pydantic models
class SkillResponse(BaseModel):
    skill_id: str
    display_name: str
    category: str
    automation_level: str
    description: str
    when_to_use: List[str]
    tools_required: List[str]
    approval_required: bool

class WorkflowResponse(BaseModel):
    workflow_id: str
    name: str
    trigger: str
    steps: List[Dict[str, Any]]
    data_required: List[str]
    tools: List[str]

class CodeValidationRequest(BaseModel):
    code: str

class CodeValidationResponse(BaseModel):
    total_checks: int
    passed: int
    failed: int
    warnings: int
    score: float
    quality_gate: str
    results: List[Dict[str, Any]]

# Routes
@router.get("/list", response_model=List[SkillResponse])
async def list_all_skills(category: Optional[str] = None):
    """List all available skills."""
    if category:
        cat = SkillCategory(category)
        skills = list_skills(cat)
    else:
        skills = list_skills()
    
    return [skill.to_dict() for skill in skills]

@router.get("/{skill_id}", response_model=SkillResponse)
async def get_skill_details(skill_id: str):
    """Get details of a specific skill."""
    skill = get_skill(skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill.to_dict()

@router.get("/categories/list")
async def list_categories():
    """List all skill categories."""
    return [cat.value for cat in SkillCategory]

@router.get("/automation-levels/list")
async def list_automation_levels():
    """List all automation levels."""
    return [level.value for level in AutomationLevel]

# Workflow routes
@router.get("/workflows/list", response_model=List[WorkflowResponse])
async def list_all_workflows():
    """List all available workflows."""
    workflows = list_workflows()
    return [wf.to_dict() for wf in workflows]

@router.get("/workflows/{workflow_id}", response_model=WorkflowResponse)
async def get_workflow_details(workflow_id: str):
    """Get details of a specific workflow."""
    workflow = get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return workflow.to_dict()

@router.post("/workflows/{workflow_id}/execute")
async def execute_workflow(workflow_id: str):
    """Execute a workflow (placeholder - would trigger actual execution)."""
    workflow = get_workflow(workflow_id)
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
    
    # In real implementation, this would queue the workflow
    return {
        "status": "queued",
        "workflow_id": workflow_id,
        "message": f"Workflow '{workflow.name}' queued for execution"
    }

# Quality validation routes
@router.post("/quality/validate", response_model=CodeValidationResponse)
async def validate_code_quality(request: CodeValidationRequest):
    """Validate code against Synthia quality standards."""
    results = validate_code(request.code)
    summary = get_quality_summary(results)
    return summary

@router.get("/quality/checklist/{category}")
async def get_quality_checklist(category: str):
    """Get quality checklist for a specific category."""
    from skills.quality import CheckCategory, get_checklist_for_category
    
    try:
        cat = CheckCategory(category)
        checklist = get_checklist_for_category(cat)
        return checklist
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid category: {category}")
