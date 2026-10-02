from typing import Any,Literal
from pydantic import BaseModel,Field
class EnterpriseRequest(BaseModel):
    request:str
    context:dict[str,Any]=Field(default_factory=dict)
    session_id:str|None=None
class Task(BaseModel):
    id:str
    kind:Literal["research","knowledge","analysis","code","workflow","action","verify"]
    instruction:str
    dependencies:list[str]=Field(default_factory=list)
    risk:Literal["read","write","destructive"]="read"
class Plan(BaseModel):
    goal:str
    tasks:list[Task]
class AgentResult(BaseModel):
    task_id:str
    agent:str
    status:Literal["ok","failed","approval_required"]
    output:Any=None
    evidence:list[dict[str,Any]]=Field(default_factory=list)
    error:str|None=None
class FinalResponse(BaseModel):
    run_id:str
    status:str
    answer:str
    evidence:list[dict[str,Any]]=Field(default_factory=list)
    verification:dict[str,Any]=Field(default_factory=dict)
