import re,uuid
from app.models import Plan,Task
class Planner:
    """Deterministic safe baseline. Replace front-end with structured-output model while retaining typed IR validation."""
    def compile(self,goal):
        tasks=[]
        low=goal.lower()
        tasks.append(Task(id="research",kind="research",instruction=goal))
        tasks.append(Task(id="knowledge",kind="knowledge",instruction="Retrieve enterprise knowledge relevant to goal"))
        if any(x in low for x in ["code","implement","bug","repository","script"]):
            tasks.append(Task(id="coder",kind="code",instruction="Develop or inspect code",dependencies=["research","knowledge"]))
        if any(x in low for x in ["workflow","process","plan","orchestrate"]):
            tasks.append(Task(id="workflow",kind="workflow",instruction="Construct executable workflow",dependencies=["research","knowledge"]))
        if any(x in low for x in ["send","create","update","deploy","restart","execute"]):
            deps=[t.id for t in tasks]
            tasks.append(Task(id="action",kind="action",instruction=goal,dependencies=deps,risk="write"))
        deps=[t.id for t in tasks]
        tasks.append(Task(id="verify",kind="verify",instruction="Critique evidence and verify final result",dependencies=deps))
        return Plan(goal=goal,tasks=tasks)
planner=Planner()
