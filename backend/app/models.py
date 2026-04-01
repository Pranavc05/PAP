from pydantic import BaseModel


class LevelOverview(BaseModel):
    level: int
    title: str
    goal: str


class StarterProject(BaseModel):
    title: str
    difficulty: str
    business_goal: str
    first_step: str


class WorkflowNodePosition(BaseModel):
    x: float
    y: float


class WorkflowNodeData(BaseModel):
    label: str


class WorkflowNode(BaseModel):
    id: str
    type: str
    position: WorkflowNodePosition
    data: WorkflowNodeData


class WorkflowEdge(BaseModel):
    id: str
    source: str
    target: str


class WorkflowDiagram(BaseModel):
    id: str
    name: str
    nodes: list[WorkflowNode]
    edges: list[WorkflowEdge]


class WorkflowSaveRequest(BaseModel):
    name: str
    nodes: list[WorkflowNode]
    edges: list[WorkflowEdge]


class WorkflowAnalysis(BaseModel):
    bottleneck_score: int
    risk_score: int
    findings: list[str]
    recommendations: list[str]


class LessonOverview(BaseModel):
    id: str
    title: str
    objective: str
    position: int


class ModuleOverview(BaseModel):
    id: str
    title: str
    description: str
    position: int
    lessons: list[LessonOverview]


class CourseOverview(BaseModel):
    id: str
    slug: str
    title: str
    description: str
    level: int
    module_count: int
    lesson_count: int


class CourseDetail(BaseModel):
    id: str
    slug: str
    title: str
    description: str
    level: int
    modules: list[ModuleOverview]


class LessonDetail(BaseModel):
    id: str
    module_id: str
    title: str
    objective: str
    content_markdown: str
    position: int


class LessonCompletionRequest(BaseModel):
    completed: bool = True
    score: int | None = None


class LessonProgressItem(BaseModel):
    lesson_id: str
    completed: bool
    score: int | None
    completed_at: str | None


class CourseProgressResponse(BaseModel):
    course_id: str
    total_lessons: int
    completed_lessons: int
    completion_percentage: float
    items: list[LessonProgressItem]
