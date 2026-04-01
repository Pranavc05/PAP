from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth import AuthUser, get_current_user
from app.db import get_db
from app.entities import WorkflowEntity
from app.models import (
    LevelOverview,
    StarterProject,
    WorkflowAnalysis,
    WorkflowDiagram,
    WorkflowSaveRequest,
)

router = APIRouter(prefix="/api/v1", tags=["mvp"])


@router.get("/levels", response_model=list[LevelOverview])
def list_levels() -> list[LevelOverview]:
    return [
        LevelOverview(
            level=1,
            title="Foundations of Process Automation",
            goal="Understand what to automate and why.",
        ),
        LevelOverview(
            level=2,
            title="Process Mapping and Business Thinking",
            goal="Map processes and identify bottlenecks.",
        ),
        LevelOverview(
            level=3,
            title="Tools Used in Industry",
            goal="Choose practical tools based on use case constraints.",
        ),
    ]


@router.get("/projects/starter", response_model=list[StarterProject])
def list_starter_projects() -> list[StarterProject]:
    return [
        StarterProject(
            title="Auto-sort onboarding emails",
            difficulty="Beginner",
            business_goal="Reduce manual sorting time by 60%.",
            first_step="Map current email categories and routing rules.",
        ),
        StarterProject(
            title="Employee onboarding workflow",
            difficulty="Intermediate",
            business_goal="Cut onboarding cycle time from 5 days to 2 days.",
            first_step="Document all systems and handoff points in the current process.",
        ),
    ]


@router.post("/workflows", response_model=WorkflowDiagram)
def save_workflow(
    payload: WorkflowSaveRequest,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
) -> WorkflowDiagram:
    workflow_id = str(uuid4())
    workflow_row = WorkflowEntity(
        id=workflow_id,
        owner_id=current_user.user_id,
        name=payload.name,
        nodes=[node.model_dump() for node in payload.nodes],
        edges=[edge.model_dump() for edge in payload.edges],
    )
    db.add(workflow_row)
    db.commit()
    db.refresh(workflow_row)
    return WorkflowDiagram(
        id=workflow_row.id,
        name=workflow_row.name,
        nodes=payload.nodes,
        edges=payload.edges,
    )


@router.get("/workflows/{workflow_id}", response_model=WorkflowDiagram)
def get_workflow(
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
) -> WorkflowDiagram:
    workflow = db.execute(
        select(WorkflowEntity).where(
            WorkflowEntity.id == workflow_id,
            WorkflowEntity.owner_id == current_user.user_id,
        )
    ).scalar_one_or_none()
    if workflow is None:
        raise HTTPException(status_code=404, detail="Workflow not found")
    return WorkflowDiagram(
        id=workflow.id,
        name=workflow.name,
        nodes=workflow.nodes,
        edges=workflow.edges,
    )


@router.post("/workflows/analyze", response_model=WorkflowAnalysis)
def analyze_workflow(payload: WorkflowSaveRequest) -> WorkflowAnalysis:
    findings: list[str] = []
    recommendations: list[str] = []
    node_types = [node.type.lower() for node in payload.nodes]

    approval_count = node_types.count("approval")
    decision_count = node_types.count("decision")
    ai_count = node_types.count("ai")
    api_count = node_types.count("api")

    bottleneck_score = min(100, approval_count * 20 + decision_count * 10)
    risk_score = min(100, max(0, 20 + ai_count * 15 - api_count * 5))

    if approval_count >= 2:
        findings.append("Multiple approval gates may slow cycle time.")
        recommendations.append("Consolidate approvals or introduce conditional auto-approvals.")
    if decision_count == 0:
        findings.append("No explicit decision nodes found for exception handling.")
        recommendations.append("Add at least one decision node for edge-case routing.")
    if ai_count > 0 and approval_count == 0:
        findings.append("AI steps exist without human verification points.")
        recommendations.append("Add human-in-the-loop checks for low-confidence outcomes.")
    if not findings:
        findings.append("Workflow has a balanced structure for an MVP draft.")
        recommendations.append("Track lead time and error rate to validate performance in practice.")

    return WorkflowAnalysis(
        bottleneck_score=bottleneck_score,
        risk_score=risk_score,
        findings=findings,
        recommendations=recommendations,
    )
