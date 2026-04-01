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
