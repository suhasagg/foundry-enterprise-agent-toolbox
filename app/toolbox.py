import httpx,uuid
from app.config import settings
try:
    from azure.identity.aio import DefaultAzureCredential
except Exception:
    DefaultAzureCredential=None
class ToolboxClient:
    """Raw MCP-compatible Foundry Toolbox client. Uses Entra token when configured; local mode returns deterministic fixtures."""
    def __init__(self): self.endpoint=settings.toolbox_endpoint
    async def _headers(self):
        h={"content-type":"application/json"}
        if self.endpoint and DefaultAzureCredential:
            cred=DefaultAzureCredential()
            try:
                token=await cred.get_token("https://ai.azure.com/.default")
                h["authorization"]="Bearer "+token.token
            finally:
                await cred.close()
        return h
    async def call(self,name,args):
        if not self.endpoint:
            return {"local_tool":name,"arguments":args,"content":[{"type":"text","text":f"Local development result for {name}"}]}
        payload={"jsonrpc":"2.0","id":str(uuid.uuid4()),"method":"tools/call","params":{"name":name,"arguments":args}}
        async with httpx.AsyncClient(timeout=settings.tool_timeout_seconds,follow_redirects=False) as c:
            r=await c.post(self.endpoint,headers=await self._headers(),json=payload)
            r.raise_for_status()
            return r.json()
toolbox=ToolboxClient()
