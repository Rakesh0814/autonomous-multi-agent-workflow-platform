from __future__ import annotations
import uuid
from typing import TypedDict

from langgraph.graph import START, END, StateGraph

from .crew_runner import run_specialist
from .llm import generate_json, generate_text
from .memory import memory
from .models import AgentResult, WorkflowPlan, WorkflowResponse
from .n8n_client import notify_n8n

class WorkflowState(TypedDict, total=False):
    workflow_id: str
    goal: str
    plan: WorkflowPlan
    memory_context: list[str]
    current_index: int
    agent_results: list[AgentResult]
    crewai_used: bool
    final_report: str

PLANNER_SYSTEM = """
You orchestrate an autonomous multi-agent workflow.

Break the objective into 2-5 concrete tasks.
Assign every task to exactly one specialist:
- researcher: evidence, context, assumptions and information gathering
- analyst: reasoning, risks, trade-offs and synthesis
- operations: execution plan, owners, controls and implementation

Return ONLY JSON:
{
  "objective": "...",
  "tasks": [
    {"agent": "researcher|analyst|operations", "task": "..."}
  ]
}
"""

def planner_node(state: WorkflowState) -> WorkflowState:
    memory_context = memory.search(state["goal"], limit=3)

    data = generate_json(
        f"""
User objective:
{state["goal"]}

Relevant previous workflow memory:
{chr(10).join(memory_context) if memory_context else "[none]"}

Create a concise, non-duplicative task plan.
""",
        system=PLANNER_SYSTEM,
    )

    return {
        **state,
        "plan": WorkflowPlan.model_validate(data),
        "memory_context": memory_context,
        "current_index": 0,
        "agent_results": [],
        "crewai_used": False,
    }

def specialist_node(state: WorkflowState) -> WorkflowState:
    task = state["plan"].tasks[state["current_index"]]

    previous_results = "\n\n".join(
        f"{result.agent.upper()} RESULT:\n{result.output}"
        for result in state.get("agent_results", [])
    )

    context = (
        f"Previous workflow outputs:\n{previous_results or '[none]'}\n\n"
        f"Relevant memory:\n"
        f"{chr(10).join(state.get('memory_context', [])) or '[none]'}"
    )

    output, used_crewai = run_specialist(
        task.agent,
        task.task,
        context,
    )

    return {
        **state,
        "agent_results": [
            *state.get("agent_results", []),
            AgentResult(
                agent=task.agent,
                task=task.task,
                output=output,
            ),
        ],
        "crewai_used": state.get("crewai_used", False) or used_crewai,
        "current_index": state["current_index"] + 1,
    }

def route_after_specialist(state: WorkflowState) -> str:
    if state["current_index"] < len(state["plan"].tasks):
        return "more"
    return "review"

def reviewer_node(state: WorkflowState) -> WorkflowState:
    evidence = "\n\n".join(
        f"AGENT: {result.agent}\n"
        f"TASK: {result.task}\n"
        f"OUTPUT:\n{result.output}"
        for result in state["agent_results"]
    )

    report = generate_text(
        f"""
Original objective:
{state["goal"]}

Specialist outputs:
{evidence}

Create a final decision-ready report with:
1. Executive Summary
2. Key Findings
3. Risks / Dependencies
4. Recommended Actions
5. Next Steps

Resolve contradictions and do not invent facts.
""",
        system="You are the senior reviewer of a multi-agent workflow.",
    )

    memory.store(
        state["workflow_id"],
        f"Objective: {state['goal']}\nFinal report:\n{report}",
        metadata={"type": "completed_workflow"},
    )

    return {**state, "final_report": report}

def build_graph():
    graph = StateGraph(WorkflowState)
    graph.add_node("planner", planner_node)
    graph.add_node("specialist", specialist_node)
    graph.add_node("reviewer", reviewer_node)

    graph.add_edge(START, "planner")
    graph.add_edge("planner", "specialist")
    graph.add_conditional_edges(
        "specialist",
        route_after_specialist,
        {"more": "specialist", "review": "reviewer"},
    )
    graph.add_edge("reviewer", END)

    return graph.compile()

WORKFLOW_GRAPH = build_graph()

def run_workflow(goal: str) -> WorkflowResponse:
    workflow_id = str(uuid.uuid4())

    final_state = WORKFLOW_GRAPH.invoke(
        {
            "workflow_id": workflow_id,
            "goal": goal,
        }
    )

    n8n_notified = notify_n8n(
        {
            "workflow_id": workflow_id,
            "objective": final_state["plan"].objective,
            "status": "completed",
            "final_report": final_state["final_report"],
        }
    )

    return WorkflowResponse(
        workflow_id=workflow_id,
        status="completed",
        objective=final_state["plan"].objective,
        plan=final_state["plan"].tasks,
        agent_results=final_state["agent_results"],
        final_report=final_state["final_report"],
        memory_backend=memory.backend,
        crewai_used=final_state.get("crewai_used", False),
        n8n_notified=n8n_notified,
    )
