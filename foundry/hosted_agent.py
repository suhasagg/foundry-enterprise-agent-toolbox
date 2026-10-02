"""Optional Microsoft Foundry Hosted Agent entry point.

Install: pip install -e '.[foundry]'
The exact beta package APIs can evolve; this module isolates the hosting adapter from domain logic.
"""
import os
from app.orchestrator import supervisor
# Production deployment should use Microsoft Agent Framework's Foundry hosting package
# or langchain_azure_ai.agents.hosting for a compiled LangGraph graph.
# The runnable local API remains framework-independent.
def deployment_settings():
    return {
      "project_endpoint":os.getenv("FOUNDRY_PROJECT_ENDPOINT",""),
      "model":os.getenv("FOUNDRY_MODEL_NAME",""),
      "toolbox_endpoint":os.getenv("TOOLBOX_ENDPOINT","")
    }
