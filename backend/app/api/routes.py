from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import AuthUser, get_current_user
from app.db import get_db
from app.entities import CourseEntity, LessonEntity, ModuleEntity, UserLessonProgressEntity, WorkflowEntity
from app.models import (
    CourseDetail,
    CourseOverview,
    CourseProgressResponse,
    LessonCompletionRequest,
    LessonDetail,
    LessonOverview,
    LessonProgressItem,
    LevelOverview,
    ModuleOverview,
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


@router.get("/courses", response_model=list[CourseOverview])
def list_courses(db: Session = Depends(get_db)) -> list[CourseOverview]:
    course_rows = db.execute(select(CourseEntity).order_by(CourseEntity.level.asc())).scalars().all()
    module_counts = dict(
        db.execute(
            select(ModuleEntity.course_id, func.count(ModuleEntity.id)).group_by(ModuleEntity.course_id)
        ).all()
    )
    lesson_counts = dict(
        db.execute(
            select(ModuleEntity.course_id, func.count(LessonEntity.id))
            .join(LessonEntity, LessonEntity.module_id == ModuleEntity.id)
            .group_by(ModuleEntity.course_id)
        ).all()
    )

    return [
        CourseOverview(
            id=course.id,
            slug=course.slug,
            title=course.title,
            description=course.description,
            level=course.level,
            module_count=int(module_counts.get(course.id, 0)),
            lesson_count=int(lesson_counts.get(course.id, 0)),
        )
        for course in course_rows
    ]


@router.get("/courses/{course_id}", response_model=CourseDetail)
def get_course(course_id: str, db: Session = Depends(get_db)) -> CourseDetail:
    course = db.get(CourseEntity, course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    module_rows = db.execute(
        select(ModuleEntity).where(ModuleEntity.course_id == course_id).order_by(ModuleEntity.position.asc())
    ).scalars().all()
    module_ids = [module.id for module in module_rows]
    lesson_rows = (
        db.execute(
            select(LessonEntity)
            .where(LessonEntity.module_id.in_(module_ids))
            .order_by(LessonEntity.module_id.asc(), LessonEntity.position.asc())
        ).scalars().all()
        if module_ids
        else []
    )

    lessons_by_module: dict[str, list[LessonOverview]] = {module_id: [] for module_id in module_ids}
    for lesson in lesson_rows:
        lessons_by_module.setdefault(lesson.module_id, []).append(
            LessonOverview(
                id=lesson.id,
                title=lesson.title,
                objective=lesson.objective,
                position=lesson.position,
            )
        )

    modules = [
        ModuleOverview(
            id=module.id,
            title=module.title,
            description=module.description,
            position=module.position,
            lessons=lessons_by_module.get(module.id, []),
        )
        for module in module_rows
    ]

    return CourseDetail(
        id=course.id,
        slug=course.slug,
        title=course.title,
        description=course.description,
        level=course.level,
        modules=modules,
    )


@router.get("/lessons/{lesson_id}", response_model=LessonDetail)
def get_lesson(lesson_id: str, db: Session = Depends(get_db)) -> LessonDetail:
    lesson = db.get(LessonEntity, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")
    return LessonDetail(
        id=lesson.id,
        module_id=lesson.module_id,
        title=lesson.title,
        objective=lesson.objective,
        content_markdown=lesson.content_markdown,
        position=lesson.position,
    )


@router.post("/lessons/{lesson_id}/complete", response_model=LessonProgressItem)
def mark_lesson_complete(
    lesson_id: str,
    payload: LessonCompletionRequest,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
) -> LessonProgressItem:
    lesson = db.get(LessonEntity, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")

    progress = db.execute(
        select(UserLessonProgressEntity).where(
            UserLessonProgressEntity.user_id == current_user.user_id,
            UserLessonProgressEntity.lesson_id == lesson_id,
        )
    ).scalar_one_or_none()

    if progress is None:
        progress = UserLessonProgressEntity(
            user_id=current_user.user_id,
            lesson_id=lesson_id,
            completed=payload.completed,
            score=payload.score,
        )
        db.add(progress)
    else:
        progress.completed = payload.completed
        progress.score = payload.score

    if payload.completed:
        progress.completed_at = datetime.now(timezone.utc)
    else:
        progress.completed_at = None

    db.commit()
    db.refresh(progress)
    return LessonProgressItem(
        lesson_id=progress.lesson_id,
        completed=progress.completed,
        score=progress.score,
        completed_at=progress.completed_at.isoformat() if progress.completed_at else None,
    )


@router.get("/courses/{course_id}/progress", response_model=CourseProgressResponse)
def get_course_progress(
    course_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
) -> CourseProgressResponse:
    course = db.get(CourseEntity, course_id)
    if course is None:
        raise HTTPException(status_code=404, detail="Course not found")

    lesson_ids = [
        row[0]
        for row in db.execute(
            select(LessonEntity.id)
            .join(ModuleEntity, ModuleEntity.id == LessonEntity.module_id)
            .where(ModuleEntity.course_id == course_id)
        ).all()
    ]
    total_lessons = len(lesson_ids)

    progress_rows = (
        db.execute(
            select(UserLessonProgressEntity).where(
                UserLessonProgressEntity.user_id == current_user.user_id,
                UserLessonProgressEntity.lesson_id.in_(lesson_ids),
            )
        ).scalars().all()
        if lesson_ids
        else []
    )
    completed_lessons = sum(1 for row in progress_rows if row.completed)
    percentage = (completed_lessons / total_lessons * 100) if total_lessons else 0.0

    items = [
        LessonProgressItem(
            lesson_id=row.lesson_id,
            completed=row.completed,
            score=row.score,
            completed_at=row.completed_at.isoformat() if row.completed_at else None,
        )
        for row in progress_rows
    ]

    return CourseProgressResponse(
        course_id=course_id,
        total_lessons=total_lessons,
        completed_lessons=completed_lessons,
        completion_percentage=round(percentage, 2),
        items=items,
    )


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
