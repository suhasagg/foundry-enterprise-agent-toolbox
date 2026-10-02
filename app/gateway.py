from app.toolbox import toolbox
class CapabilitySecurityGateway:
    READ_PREFIXES=("search.","knowledge.","file.","azure_search.","web.")
    async def execute(self,p,tool,args,risk="read",approved=False):
        if risk=="read" and "tools:read" not in p.scopes: return {"status":"denied","reason":"missing tools:read"}
        if risk in {"write","destructive"}:
            if "tools:write" not in p.scopes:return {"status":"denied","reason":"missing tools:write"}
            if not approved:return {"status":"approval_required","reason":"consequential action requires approval"}
        return {"status":"ok","result":await toolbox.call(tool,args)}
gateway=CapabilitySecurityGateway()
