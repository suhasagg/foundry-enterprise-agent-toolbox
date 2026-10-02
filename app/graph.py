"""LangGraph representation of the enterprise orchestration pipeline.

The API uses the deterministic Supervisor directly so the project runs without a model.
This graph factory demonstrates how the same orchestration is hosted as LangGraph.
"""
from typing import TypedDict,Any
from langgraph.graph import StateGraph,END
class State(TypedDict,total=False):
    request:str
    principal:Any
    plan:Any
    result:dict
def build_graph(supervisor):
    async def execute(state):
        p=state["principal"]
        state["result"]=await supervisor.run(p,state["request"])
        return state
    g=StateGraph(State)
    g.add_node("supervisor",execute)
    g.set_entry_point("supervisor")
    g.add_edge("supervisor",END)
    return g.compile()
