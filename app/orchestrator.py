import asyncio,uuid
from app.planner import planner
from app.agents import AGENTS
from app.memory import memory
class Supervisor:
    async def run(self,p,request,approved=False):
        run_id=str(uuid.uuid4()); plan=planner.compile(request)
        memory.put(p.tenant,"working",run_id,{"goal":request})
        results={}; evidence=[]
        pending={t.id:t for t in plan.tasks}
        while pending:
            ready=[t for t in pending.values() if all(d in results for d in t.dependencies)]
            if not ready: raise RuntimeError("DAG deadlock")
            async def one(t):
                ctx={"goal":request,"results":results,"evidence":evidence,"approved":approved}
                return t,await AGENTS[t.kind].run(p,t,ctx)
            batch=await asyncio.gather(*(one(t) for t in ready))
            for t,r in batch:
                results[t.id]=r.model_dump(); evidence.extend(r.evidence)
                memory.put(p.tenant,"episodic",f"{run_id}:{t.id}",r.model_dump())
                pending.pop(t.id)
                if r.status=="approval_required":
                    memory.put(p.tenant,"audit",f"{run_id}:approval",{"task":t.id})
                    return {"run_id":run_id,"status":"approval_required","plan":plan.model_dump(),"results":results,"evidence":evidence}
        verification=results.get("verify",{}).get("output",{})
        answer=f"Completed enterprise request with {len(results)} task nodes. Verification={verification.get('verified',False)}."
        memory.put(p.tenant,"conversation",run_id,{"request":request,"answer":answer})
        memory.put(p.tenant,"semantic",run_id,{"summary":answer})
        memory.put(p.tenant,"audit",run_id,{"status":"completed"})
        return {"run_id":run_id,"status":"succeeded","answer":answer,"plan":plan.model_dump(),"results":results,"evidence":evidence,"verification":verification}
supervisor=Supervisor()
