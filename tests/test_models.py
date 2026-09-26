from app.models import WorkflowPlan

def test_workflow_plan_validation():
    plan = WorkflowPlan.model_validate(
        {
            "objective": "Improve support operations",
            "tasks": [
                {
                    "agent": "researcher",
                    "task": "Gather context"
                },
                {
                    "agent": "analyst",
                    "task": "Analyze causes"
                }
            ],
        }
    )

    assert len(plan.tasks) == 2
    assert plan.tasks[0].agent == "researcher"
