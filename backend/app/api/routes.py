from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import AuthUser, get_current_user
from app.db import get_db
from app.entities import (
    CourseEntity,
    LessonEntity,
    ModuleEntity,
    QuizAttemptEntity,
    QuizQuestionEntity,
    TutorMessageEntity,
    TutorSessionEntity,
    UserLessonProgressEntity,
    WorkflowEntity,
)
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
    QuizAttemptSummary,
    QuizAnswerSubmission,
    QuizOption,
    QuizQuestionPublic,
    QuizResultItem,
    QuizSubmitRequest,
    QuizSubmitResponse,
    StarterProject,
    TutorGenerateRequest,
    TutorMessage,
    TutorMessageRequest,
    TutorMessageResponse,
    TutorSessionCreateRequest,
    TutorSessionDetail,
    TutorSessionOverview,
    WorkflowAnalysis,
    WorkflowDiagram,
    WorkflowSaveRequest,
)
from app.tutor_engine import generate_tutor_response

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


@router.get("/lessons/{lesson_id}/quiz", response_model=list[QuizQuestionPublic])
def get_lesson_quiz(lesson_id: str, db: Session = Depends(get_db)) -> list[QuizQuestionPublic]:
    lesson = db.get(LessonEntity, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")

    question_rows = db.execute(
        select(QuizQuestionEntity)
        .where(QuizQuestionEntity.lesson_id == lesson_id)
        .order_by(QuizQuestionEntity.position.asc())
    ).scalars().all()

    return [
        QuizQuestionPublic(
            id=question.id,
            prompt=question.prompt,
            options=[QuizOption(**option) for option in question.options],
            position=question.position,
        )
        for question in question_rows
    ]


@router.post("/lessons/{lesson_id}/quiz/submit", response_model=QuizSubmitResponse)
def submit_quiz_attempt(
    lesson_id: str,
    payload: QuizSubmitRequest,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
) -> QuizSubmitResponse:
    lesson = db.get(LessonEntity, lesson_id)
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")

    question_rows = db.execute(
        select(QuizQuestionEntity)
        .where(QuizQuestionEntity.lesson_id == lesson_id)
        .order_by(QuizQuestionEntity.position.asc())
    ).scalars().all()
    if not question_rows:
        raise HTTPException(status_code=404, detail="No quiz questions found for lesson")

    answer_map = {answer.question_id: answer.selected_option_key for answer in payload.answers}
    results: list[QuizResultItem] = []
    correct_count = 0

    for question in question_rows:
        selected = answer_map.get(question.id)
        is_correct = selected == question.correct_option_key
        if is_correct:
            correct_count += 1
        results.append(
            QuizResultItem(
                question_id=question.id,
                selected_option_key=selected,
                correct_option_key=question.correct_option_key,
                is_correct=is_correct,
                explanation=question.explanation,
            )
        )

    total_questions = len(question_rows)
    percentage = (correct_count / total_questions * 100) if total_questions else 0.0
    attempt_id = str(uuid4())

    db.add(
        QuizAttemptEntity(
            id=attempt_id,
            user_id=current_user.user_id,
            lesson_id=lesson_id,
            score=correct_count,
            total_questions=total_questions,
            answers=[QuizAnswerSubmission(question_id=item.question_id, selected_option_key=item.selected_option_key or "").model_dump() for item in results],
        )
    )
    db.commit()

    return QuizSubmitResponse(
        attempt_id=attempt_id,
        score=correct_count,
        total_questions=total_questions,
        percentage=round(percentage, 2),
        results=results,
    )


@router.get("/lessons/{lesson_id}/quiz/attempts", response_model=list[QuizAttemptSummary])
def get_quiz_attempts(
    lesson_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
) -> list[QuizAttemptSummary]:
    attempt_rows = db.execute(
        select(QuizAttemptEntity)
        .where(
            QuizAttemptEntity.lesson_id == lesson_id,
            QuizAttemptEntity.user_id == current_user.user_id,
        )
        .order_by(QuizAttemptEntity.submitted_at.desc())
    ).scalars().all()

    return [
        QuizAttemptSummary(
            attempt_id=attempt.id,
            score=attempt.score,
            total_questions=attempt.total_questions,
            percentage=round((attempt.score / attempt.total_questions * 100) if attempt.total_questions else 0.0, 2),
            submitted_at=attempt.submitted_at.isoformat(),
        )
        for attempt in attempt_rows
    ]


@router.post("/tutor/sessions", response_model=TutorSessionOverview)
def create_tutor_session(
    payload: TutorSessionCreateRequest,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
) -> TutorSessionOverview:
    if payload.lesson_id:
        lesson = db.get(LessonEntity, payload.lesson_id)
        if lesson is None:
            raise HTTPException(status_code=404, detail="Lesson not found")

    session_id = str(uuid4())
    session = TutorSessionEntity(
        id=session_id,
        user_id=current_user.user_id,
        lesson_id=payload.lesson_id,
        title=payload.title or "AI Tutor Session",
        mode=payload.mode,
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return TutorSessionOverview(
        id=session.id,
        lesson_id=session.lesson_id,
        title=session.title,
        mode=session.mode,
        created_at=session.created_at.isoformat(),
        updated_at=session.updated_at.isoformat(),
    )


@router.get("/tutor/sessions", response_model=list[TutorSessionOverview])
def list_tutor_sessions(
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
) -> list[TutorSessionOverview]:
    sessions = db.execute(
        select(TutorSessionEntity)
        .where(TutorSessionEntity.user_id == current_user.user_id)
        .order_by(TutorSessionEntity.updated_at.desc())
    ).scalars().all()
    return [
        TutorSessionOverview(
            id=session.id,
            lesson_id=session.lesson_id,
            title=session.title,
            mode=session.mode,
            created_at=session.created_at.isoformat(),
            updated_at=session.updated_at.isoformat(),
        )
        for session in sessions
    ]


@router.get("/tutor/sessions/{session_id}", response_model=TutorSessionDetail)
def get_tutor_session(
    session_id: str,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
) -> TutorSessionDetail:
    session = db.execute(
        select(TutorSessionEntity).where(
            TutorSessionEntity.id == session_id,
            TutorSessionEntity.user_id == current_user.user_id,
        )
    ).scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=404, detail="Tutor session not found")

    messages = db.execute(
        select(TutorMessageEntity)
        .where(TutorMessageEntity.session_id == session_id)
        .order_by(TutorMessageEntity.created_at.asc())
    ).scalars().all()
    return TutorSessionDetail(
        session=TutorSessionOverview(
            id=session.id,
            lesson_id=session.lesson_id,
            title=session.title,
            mode=session.mode,
            created_at=session.created_at.isoformat(),
            updated_at=session.updated_at.isoformat(),
        ),
        messages=[
            TutorMessage(
                id=message.id,
                role=message.role,
                content=message.content,
                hint_level=message.hint_level,
                created_at=message.created_at.isoformat(),
            )
            for message in messages
        ],
    )


@router.post("/tutor/sessions/{session_id}/messages", response_model=TutorMessageResponse)
def send_tutor_message(
    session_id: str,
    payload: TutorMessageRequest,
    db: Session = Depends(get_db),
    current_user: AuthUser = Depends(get_current_user),
) -> TutorMessageResponse:
    session = db.execute(
        select(TutorSessionEntity).where(
            TutorSessionEntity.id == session_id,
            TutorSessionEntity.user_id == current_user.user_id,
        )
    ).scalar_one_or_none()
    if session is None:
        raise HTTPException(status_code=404, detail="Tutor session not found")

    lesson_context = None
    if session.lesson_id:
        lesson = db.get(LessonEntity, session.lesson_id)
        lesson_context = lesson.objective if lesson else None

    generated = generate_tutor_response(
        TutorGenerateRequest(
            user_message=payload.content,
            lesson_context=lesson_context,
            mode=payload.mode,
            hint_level=payload.hint_level,
        )
    )

    user_message_entity = TutorMessageEntity(
        id=str(uuid4()),
        session_id=session.id,
        role="user",
        content=payload.content,
        hint_level=payload.hint_level if payload.mode == "hint" else None,
    )
    assistant_message_entity = TutorMessageEntity(
        id=str(uuid4()),
        session_id=session.id,
        role="assistant",
        content=generated,
        hint_level=payload.hint_level if payload.mode == "hint" else None,
    )
    session.mode = payload.mode
    db.add(user_message_entity)
    db.add(assistant_message_entity)
    db.commit()
    db.refresh(session)
    db.refresh(user_message_entity)
    db.refresh(assistant_message_entity)

    return TutorMessageResponse(
        user_message=TutorMessage(
            id=user_message_entity.id,
            role=user_message_entity.role,
            content=user_message_entity.content,
            hint_level=user_message_entity.hint_level,
            created_at=user_message_entity.created_at.isoformat(),
        ),
        assistant_message=TutorMessage(
            id=assistant_message_entity.id,
            role=assistant_message_entity.role,
            content=assistant_message_entity.content,
            hint_level=assistant_message_entity.hint_level,
            created_at=assistant_message_entity.created_at.isoformat(),
        ),
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
