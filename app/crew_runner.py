from .config import settings
from .llm import generate_text

ROLES = {
    "researcher": (
        "Research & Knowledge Agent",
        "Gather relevant facts, assumptions, evidence and context."
    ),
    "analyst": (
        "Business & Risk Analysis Agent",
        "Analyze evidence, risks, trade-offs and dependencies."
    ),
    "operations": (
        "Operations & Execution Agent",
        "Turn analysis into actions, owners, controls and next steps."
    ),
}

def _fallback(name: str, task: str, context: str) -> str:
    role, goal = ROLES[name]
    return generate_text(
        f"Assigned task:\n{task}\n\nContext:\n{context or '[none]'}",
        system=f"You are the {role}. {goal} Be concise, decision-ready, and label assumptions."
    )

def run_specialist(name: str, task: str, context: str) -> tuple[str, bool]:
    if not settings.use_crewai:
        return _fallback(name, task, context), False

    try:
        from crewai import Agent, Crew, LLM, Process, Task

        role, goal = ROLES[name]
        llm = LLM(
            model=f"gemini/{settings.gemini_model}",
            api_key=settings.gemini_api_key,
            temperature=0.2,
        )

        agent = Agent(
            role=role,
            goal=goal,
            backstory=f"You are a specialist in {role.lower()}.",
            llm=llm,
            verbose=False,
            allow_delegation=False,
        )

        crew_task = Task(
            description=f"Complete this assignment:\n{task}\n\nWorkflow context:\n{context or '[none]'}",
            expected_output="A clear answer with findings, risks/dependencies and concrete recommendations.",
            agent=agent,
        )

        result = Crew(
            agents=[agent],
            tasks=[crew_task],
            process=Process.sequential,
            verbose=False,
        ).kickoff()

        return str(result), True

    except Exception as exc:
        print(f"[CrewAI] fallback: {exc}")
        return _fallback(name, task, context), False
