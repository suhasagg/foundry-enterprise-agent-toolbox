from fastapi import FastAPI,Depends,Query
from prometheus_client import Counter,Histogram,generate_latest,CONTENT_TYPE_LATEST
from fastapi.responses import Response
from app.models import EnterpriseRequest
from app.security import principal
from app.orchestrator import supervisor
from app.memory import memory
RUNS=Counter("enterprise_agent_runs_total","Runs",["status"])
app=FastAPI(title="Foundry Hosted Enterprise Agent + Toolbox/MCP",version="1.0.0")
@app.get("/health/live")
async def live():return {"status":"ok"}
@app.post("/v1/run")
async def run(r:EnterpriseRequest,approved:bool=Query(False),p=Depends(principal)):
    out=await supervisor.run(p,r.request,approved=approved);RUNS.labels(out["status"]).inc();return out
@app.get("/v1/memory")
async def mem(p=Depends(principal)):return memory.snapshot(p.tenant)
@app.get("/metrics")
async def metrics():return Response(generate_latest(),media_type=CONTENT_TYPE_LATEST)
