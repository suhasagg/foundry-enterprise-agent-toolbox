from app.gateway import gateway
from app.models import AgentResult
class ResearchAgent:
    async def run(self,p,t,ctx):
        x=await gateway.execute(p,"web.search",{"query":t.instruction})
        return AgentResult(task_id=t.id,agent="ResearchAgent",status="ok" if x["status"]=="ok" else x["status"],output=x,evidence=[{"source":"toolbox:web.search"}])
class KnowledgeAgent:
    async def run(self,p,t,ctx):
        x=await gateway.execute(p,"azure_search.query",{"query":ctx["goal"]})
        return AgentResult(task_id=t.id,agent="KnowledgeAnalyst",status="ok" if x["status"]=="ok" else x["status"],output=x,evidence=[{"source":"toolbox:azure_search.query"}])
class CoderAgent:
    async def run(self,p,t,ctx):
        x=await gateway.execute(p,"code.interpreter",{"task":t.instruction,"context":ctx.get("results",{})})
        return AgentResult(task_id=t.id,agent="CoderAgent",status="ok" if x["status"]=="ok" else x["status"],output=x)
class WorkflowAgent:
    async def run(self,p,t,ctx):
        return AgentResult(task_id=t.id,agent="WorkflowAgent",status="ok",output={"dag":"validated","instruction":t.instruction})
class ActionAgent:
    async def run(self,p,t,ctx):
        x=await gateway.execute(p,"enterprise.action",{"request":t.instruction},risk=t.risk,approved=ctx.get("approved",False))
        return AgentResult(task_id=t.id,agent="ActionAgent",status=x["status"],output=x)
class VerifierAgent:
    async def run(self,p,t,ctx):
        failed=[k for k,v in ctx.get("results",{}).items() if v.get("status") not in {"ok"}]
        return AgentResult(task_id=t.id,agent="CriticVerifier",status="ok",output={"verified":not failed,"exceptions":failed,"evidence_count":len(ctx.get("evidence",[]))})
AGENTS={"research":ResearchAgent(),"knowledge":KnowledgeAgent(),"code":CoderAgent(),"workflow":WorkflowAgent(),"action":ActionAgent(),"verify":VerifierAgent()}
