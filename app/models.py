from typing import Literal
from pydantic import BaseModel, Field

class WorkflowRequest(BaseModel):
    goal: str = Field(min_length=5, max_length=5000)

class PlannedTask(BaseModel):
    agent: Literal["researcher", "analyst", "operations"]
    task: str

class WorkflowPlan(BaseModel):
    objective: str
    tasks: list[PlannedTask]

class AgentResult(BaseModel):
    agent: str
    task: str
    output: str

class WorkflowResponse(BaseModel):
    workflow_id: str
    status: Literal["completed", "failed"]
    objective: str
    plan: list[PlannedTask]
    agent_results: list[AgentResult]
    final_report: str
    memory_backend: str
    crewai_used: bool
    n8n_notified: bool
