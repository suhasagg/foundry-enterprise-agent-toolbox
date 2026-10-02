# Threat Model
Protect agent identity, user/tenant data, tool authority, Toolbox credentials, memory, approvals, code execution, and audit.
Threats include prompt injection, confused deputy, malicious MCP/tool output, cross-tenant memory, approval substitution, SSRF, data exfiltration, sandbox escape, excessive delegation, poisoned RAG, and duplicate side effects.
Controls: Entra/workload identity, capability gateway, least privilege, approval, information-flow labels, DLP, endpoint governance, sandboxing, immutable tool versions, idempotency, evidence/provenance, and audit.
