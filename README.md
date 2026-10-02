# Microsoft Foundry Hosted Enterprise Agent + Toolbox/MCP

A production-oriented, runnable reference implementation of an enterprise multi-agent system built around Microsoft Foundry Hosted Agents, Microsoft Agent Framework/LangGraph concepts, a supervisor-driven Task DAG, a security/capability gateway, Foundry Toolbox over MCP, specialist agents, critic/verifier, and seven-layer memory.

## 1. Why this architecture is timely

Microsoft Foundry Hosted Agents let teams keep orchestration logic in code while Foundry operates the hosted runtime, session lifecycle, identity, scaling, protocol endpoints and platform integration. Microsoft documents both Microsoft Agent Framework and LangGraph hosting paths.

Foundry Toolbox provides a named/versioned server-side tool collection exposed through a managed MCP-compatible endpoint. It is therefore a natural enterprise tool plane behind a custom hosted agent.

## 2. Target architecture

```text
Enterprise request
        |
        v
Microsoft Foundry Hosted Agent
        |
        +-----------------------------+
        |                             |
        v                             v
Microsoft Agent Framework         LangGraph
        |                             |
        +-------------+---------------+
                      |
                      v
                  Supervisor
                      |
                      v
                   Task DAG
       +--------------+--------------+
       |              |              |
       v              v              v
   Research       Knowledge       Analyst
       |              |              |
       +--------+-----+------+-------+
                |            |
                v            v
              Coder       Workflow
                \            /
                 \          /
                  v        v
                  Action Agent
                      |
                      v
            Capability/Security Gateway
                      |
                      v
                Foundry Toolbox
                      |
                     MCP
       +--------------+---------------+
       |              |               |
       v              v               v
   Web Search    Azure AI Search   Enterprise APIs
       |              |               |
       +--------------+---------------+
                      |
                      v
                Critic / Verifier
                      |
                      v
                Seven-Layer Memory
```

## 3. What is actually implemented

The repository contains runnable code for:
- FastAPI enterprise request endpoint;
- deterministic typed planner that compiles requests into a DAG;
- dependency-aware concurrent supervisor;
- Research Agent;
- Knowledge Analyst;
- Coder Agent;
- Workflow Agent;
- Action Agent;
- Critic/Verifier;
- Capability/Security Gateway;
- raw MCP-compatible Toolbox client;
- optional Entra `DefaultAzureCredential` authentication;
- approval gate for writes;
- seven-layer memory abstraction;
- LangGraph compiled-graph adapter;
- Foundry deployment configuration seam;
- Prometheus metrics;
- Docker Compose;
- tests;
- Kubernetes/operations/security design documentation.

The local mode intentionally returns deterministic tool fixtures when no real Toolbox endpoint is configured. That keeps the whole orchestration runnable without pretending to possess a user's Azure resources.

## 4. Microsoft-specific production integration

For a real Foundry deployment configure:

```text
FOUNDRY_PROJECT_ENDPOINT
FOUNDRY_MODEL_NAME
TOOLBOX_ENDPOINT or TOOLBOX_NAME
```

Use the Hosted Agent's dedicated Entra identity for model, Toolbox and downstream Azure authorization.

## 5. Hosted Agent responsibilities

Foundry owns the managed runtime around the container:
- endpoint;
- identity;
- scale;
- session lifecycle;
- platform observability/lifecycle.

Your code owns:
- planning;
- graph;
- agent prompts/logic;
- tool policy;
- memory semantics;
- business correctness;
- verification.

This separation is a major architectural advantage.

## 6. Responses vs Invocations protocol

Responses is appropriate for conversational/OpenAI-compatible clients.

Invocations is appropriate for custom request/response contracts, webhook-style jobs and non-conversational workloads.

Keep protocol hosting separate from domain orchestration.

## 7. Agent Framework + LangGraph

This project treats them as complementary concepts rather than artificially forcing duplicate orchestration.

Use Microsoft Agent Framework for:
- Microsoft-native agent abstractions;
- Foundry hosting integration;
- tools;
- workflows;
- enterprise ecosystem integration.

Use LangGraph where explicit graph state, conditional routing, checkpointing and graph composition are valuable.

The core domain logic remains independent so either hosting path can wrap it.

## 8. Supervisor

The Supervisor is the only component allowed to coordinate the global task graph.

Responsibilities:
1. compile request;
2. validate dependencies;
3. find ready nodes;
4. run independent nodes concurrently;
5. collect evidence;
6. stop at approval boundary;
7. send completed evidence to verifier;
8. persist memory/audit.

## 9. Why a typed Task DAG

Do not allow an LLM to execute arbitrary prose plans.

Compile into:

```text
Task {
  id
  kind
  instruction
  dependencies[]
  risk
}
```

Then validate it.

This creates a deterministic boundary between probabilistic planning and execution.

## 10. DAG scheduling

A node is ready when every dependency has a result.

```text
ready(node) =
  all dependency IDs are completed
```

Independent ready nodes can execute concurrently.

The current supervisor uses `asyncio.gather`.

Production should add:
- per-agent semaphores;
- tenant fairness;
- leases;
- durable state;
- retries;
- deadlines;
- cancellation.

## 11. Research Agent

Purpose:
- current external information;
- web/tool research;
- provenance.

Target Toolbox tools:
- web search;
- MCP search providers;
- browser automation when necessary.

Every result should carry source/provenance.

## 12. Knowledge Analyst

Purpose:
- enterprise RAG;
- internal policy/docs;
- product/engineering knowledge.

Target:
- Azure AI Search;
- file search;
- SharePoint/enterprise MCP;
- knowledge services.

Production retrieval should be ACL-aware.

## 13. Analyst role

For complex systems, a separate Analyst can:
- reconcile research and internal knowledge;
- identify contradictions;
- create hypotheses;
- request more evidence.

The compact runnable implementation folds this reasoning into specialist outputs and the verifier; a dedicated node can be added without changing the DAG model.

## 14. Coder Agent

Target:
- code interpreter;
- repository MCP;
- sandbox;
- test execution.

Code generated by an agent is not trusted merely because it compiles.

Run it inside a controlled sandbox with:
- CPU/memory/time quotas;
- filesystem restrictions;
- egress restrictions;
- short-lived credentials.

## 15. Workflow Agent

Purpose:
- transform intent into operational steps;
- create sub-DAGs;
- validate dependencies;
- model compensations.

A production Workflow Agent should emit typed workflow IR rather than executable Python.

## 16. Action Agent

The Action Agent performs consequential external changes.

It is deliberately placed behind the Capability/Security Gateway.

```text
model intent
   |
Action Agent
   |
Security Gateway
   |
approval/policy
   |
Toolbox
```

No direct privileged tool access.

## 17. Critic

The Critic challenges:
- unsupported claims;
- missing evidence;
- contradictions;
- incomplete tasks;
- unsafe assumptions.

It should not merely ask another model "is this correct?"

Use deterministic checks wherever possible.

## 18. Verifier

Verifier inputs:
- task results;
- evidence;
- tool provenance;
- policy status;
- execution status.

Output:

```text
verified
exceptions[]
evidence_count
```

Production verification can include:
- source corroboration;
- code tests;
- schema validation;
- business invariants;
- policy compliance.

## 19. Capability/Security Gateway

The Gateway separates reasoning from authority.

It handles:
- principal scopes;
- risk;
- approval;
- tool allowlists;
- data policy;
- audit;
- invocation.

This naturally integrates with the MCP Security/Permission Firewall architecture.

## 20. Foundry Toolbox

Toolbox should be treated as the managed enterprise tool plane.

Conceptually:

```text
Agent
  |
one Toolbox MCP endpoint
  |
versioned tool collection
  |
+-- MCP
+-- Web Search
+-- Azure AI Search
+-- Code Interpreter
+-- File Search
+-- OpenAPI
+-- A2A
+-- Browser Automation
+-- Work IQ / Fabric IQ where supported
```

Tool availability evolves; pin Toolbox versions rather than assuming a static catalog.

## 21. Why Toolbox instead of wiring every tool

Benefits:
- centralized configuration;
- reusable tool collection;
- versioning;
- authentication/governance;
- one MCP-compatible access plane;
- less per-agent integration code.

## 22. Toolbox versioning

Recommended:

```text
toolbox v17
  |
integration tests
  |
security tests
  |
canary hosted-agent version
  |
promote default
```

Pin critical workloads to known versions during rollout.

## 23. Raw MCP client

`app/toolbox.py` implements the portable path:

```text
POST TOOLBOX_ENDPOINT
JSON-RPC 2.0
method = tools/call
```

When configured, it uses `DefaultAzureCredential`.

For Microsoft Agent Framework hosted agents, prefer the Microsoft-provided Foundry Toolbox integration where appropriate because it handles lifecycle/context details.

## 24. Entra identity

Hosted Agents receive a dedicated agent identity.

Use that identity for:
- Foundry model access;
- Toolbox access;
- Azure AI Search;
- downstream Azure resources.

Do not embed long-lived credentials in prompts or source.

## 25. Least privilege

Give each agent identity only the resources needed.

Example:

```text
Research Agent -> web/search read
Knowledge Agent -> search index read
Coder -> sandbox only
Action Agent -> narrowly scoped write capabilities
```

## 26. User delegation

Some enterprise actions should preserve the user's authority rather than execute under broad agent identity.

Use delegated/OBO patterns where supported and appropriate.

## 27. Tool approval

Reads may execute automatically.

Writes can return:

```text
approval_required
```

The runnable gateway demonstrates this boundary.

Production approval should bind:
- principal;
- tenant;
- tool/version;
- arguments hash;
- resource;
- expiry;
- nonce.

## 28. Prompt injection

Tool output and retrieved content are untrusted.

Do not solve prompt injection only with a classifier.

Architectural controls:
- security gateway;
- read/write separation;
- information-flow labels;
- approval;
- credentials outside context;
- destination policy.

## 29. RAG architecture

```text
query
 |
query understanding
 |
ACL/security filter
 |
Azure AI Search
 |
hybrid/vector retrieval
 |
rerank
 |
evidence chunks
 |
Knowledge Analyst
```

Store document ID, version, ACL and source URI as provenance.

## 30. RAG poisoning

Defenses:
- trusted ingestion;
- provenance;
- content classification;
- document/version allowlists;
- anomaly detection;
- verifier corroboration.

Retrieved text never grants authority.

## 31. Seven-layer memory

This project models:

```text
1. Working memory
2. Conversation memory
3. Episodic memory
4. Semantic memory
5. Procedural memory
6. Entity memory
7. Audit/provenance memory
```

These layers have different lifecycles and security semantics.

## 32. Working memory

Short-lived state for the current run:
- goal;
- current plan;
- scratch values;
- pending actions.

Target store: Redis/checkpoint state.

## 33. Conversation memory

Recent interaction context.

Target:
- Foundry session;
- durable conversation store;
- LangGraph checkpointer.

Do not blindly inject entire history into every prompt.

## 34. Episodic memory

Records what happened:
- task;
- result;
- outcome;
- timestamp.

Useful for learning from prior runs.

## 35. Semantic memory

Stable facts/summaries extracted from episodes.

Production requires:
- provenance;
- confidence;
- validity interval;
- supersession.

## 36. Procedural memory

Reusable successful procedures:

```text
how to investigate deployment failure
how to prepare customer brief
```

Procedures are suggestions, not authorization.

## 37. Entity memory

Structured state around:
- people;
- projects;
- services;
- repositories;
- incidents;
- customers.

A graph store can be useful at scale.

## 38. Audit/provenance memory

Immutable-ish record of:
- tool calls;
- policy decisions;
- evidence;
- approvals;
- outputs.

Keep it separate from model-editable semantic memory.

## 39. Memory write policy

Not every model output deserves durable memory.

Pipeline:

```text
candidate
 |
classification
 |
deduplication
 |
confidence/provenance
 |
retention policy
 |
durable memory
```

## 40. Memory isolation

All layers must be tenant/user scoped.

Never use semantic similarity as an authorization mechanism.

## 41. Durable execution

A production agent must survive:
- process restart;
- container reschedule;
- transient provider failure;
- user disconnect;
- approval wait.

Persist:
- run;
- plan version;
- node state;
- attempts;
- outputs/references;
- approval state.

## 42. Recommended durable state

PostgreSQL:

```text
runs
plans
tasks
task_attempts
approvals
artifacts
events
```

LangGraph checkpointer can complement this for graph state.

## 43. Task state machine

```text
PENDING
 |
READY
 |
RUNNING
 | \
 |  WAITING_APPROVAL
 |       |
 |     READY
 |
+--> SUCCEEDED
+--> FAILED
+--> CANCELLED
+--> UNKNOWN
```

## 44. Worker leases

Distributed workers need:
- lease owner;
- lease expiry;
- heartbeat;
- fencing token.

This prevents duplicate active ownership.

## 45. Idempotency

Every write node should have an idempotency identity derived from:

```text
run + task + attempt semantics
```

Propagate provider idempotency keys when available.

## 46. Unknown write outcomes

If the network fails after a provider may have committed:

```text
UNKNOWN
```

Reconcile before retry.

## 47. Retries

Reads:
- bounded exponential retry.

Idempotent writes:
- retry with same idempotency key.

Non-idempotent writes:
- reconciliation first.

## 48. Compensation

Multi-step enterprise workflows may need sagas.

Example:

```text
create resource
 |
update configuration
 |
failure
 |
delete created resource
```

Compensation itself is a governed action.

## 49. Timeouts

Use a hierarchical deadline:

```text
request deadline
  > task deadline
    > tool deadline
```

Do not allow nested layers to multiply timeout duration.

## 50. Cancellation

Propagate cancellation:
client -> Hosted Agent -> graph -> task -> Toolbox/MCP where supported.

## 51. Parallelism

Bound:
- global;
- tenant;
- agent type;
- tool;
- provider.

This prevents one large DAG from starving the system.

## 52. Backpressure

When capacity is exhausted:
- queue bounded work;
- reject excessive work;
- expose retry-after;
- prioritize critical tenants/workflows.

## 53. Multi-agent communication

Prefer typed artifacts/events over free-form agent chat.

```text
ResearchResult
KnowledgeResult
CodeArtifact
ActionProposal
VerificationReport
```

This improves observability and testing.

## 54. Supervisor anti-pattern

Do not let every agent dynamically spawn arbitrary agents/tools indefinitely.

Bound:
- depth;
- steps;
- token budget;
- tool calls;
- wall time;
- cost.

## 55. Dynamic replanning

Replanning is useful after:
- failed task;
- missing evidence;
- verifier rejection.

Store the new plan as a new immutable version.

## 56. Hierarchical DAG

Large workflows:

```text
top-level plan
 |
subworkflow
 |
bounded specialist DAG
```

Avoid one giant graph with thousands of nodes.

## 57. Model abstraction

Use a model client interface.

Do not couple business orchestration to one deployment name.

Production configuration controls:
- model;
- temperature;
- max tokens;
- timeout;
- fallback.

## 58. Structured output

Planner/agents should emit Pydantic/JSON schema structures.

Validate before execution.

Never parse security-sensitive decisions from arbitrary prose.

## 59. Tool discovery

Large Toolboxes may need progressive disclosure/tool search.

Pipeline:

```text
intent
 |
policy-aware catalog filter
 |
lexical/vector retrieval
 |
rerank
 |
top-K tools
```

This integrates directly with the MCP Tool Discovery & Routing Engine.

## 60. Security firewall integration

```text
Tool selection
 |
MCP Security Firewall
 |
allow / approval / deny
 |
Toolbox
```

Toolbox centralizes tools; it does not remove the need for application/organization authorization.

## 61. Observability

Trace:

```text
hosted_agent.request
  |
supervisor.plan
  |
task.research
  |-- toolbox.web_search
  |
task.knowledge
  |-- azure_ai_search
  |
task.action
  |-- policy
  |-- toolbox.call
  |
critic.verify
```

## 62. OpenTelemetry

Propagate:
- trace ID;
- run ID;
- task ID;
- agent name;
- tool name/version;
- Toolbox version;
- policy outcome.

Never emit credentials or unrestricted prompts containing secrets.

## 63. Metrics

Recommended:
- runs/status;
- plan size;
- task latency;
- agent latency;
- tool latency;
- approval wait;
- verifier rejection;
- retrieval hit quality;
- token/cost;
- memory read/write;
- retry/unknown outcomes.

## 64. Logs

Use structured logs.

Every event should have:
- tenant;
- run;
- task;
- trace;
- event type.

Sensitive payload logging is policy-controlled.

## 65. SLOs

Illustrative:
- API availability 99.9%+;
- orchestration overhead p99 <250 ms excluding models/tools;
- zero unauthorized writes;
- durable run recovery >99.99%.

These are design examples, not measurements of this repository.

## 66. Cost governance

Track cost by:
- tenant;
- run;
- agent;
- model;
- tool.

Budget:
- tokens;
- tool calls;
- browser minutes;
- code compute.

## 67. Foundry observability

Use Foundry/Azure monitoring integrations where available and preserve application-level spans for graph/task semantics.

Platform telemetry does not replace business-level correctness metrics.

## 68. Evaluation

Offline dataset:

```text
request
expected task classes
expected tools
expected evidence
expected approval behavior
expected final invariants
```

Measure:
- planning accuracy;
- tool selection;
- retrieval relevance;
- verifier precision;
- task success;
- policy correctness.

## 69. Verifier evaluation

Create adversarial cases:
- unsupported answer;
- contradictory sources;
- failed tool hidden by agent;
- stale knowledge;
- code test failure;
- approval not completed.

Verifier should reject them.

## 70. Agent regression testing

Pin:
- model version where possible;
- prompts;
- tool schemas;
- Toolbox version;
- evaluation dataset.

Compare before promotion.

## 71. Security testing

Test:
- prompt injection;
- cross-tenant memory;
- malicious MCP output;
- tool poisoning;
- approval substitution;
- SSRF;
- credential leakage;
- excessive delegation;
- RAG poisoning;
- sandbox escape assumptions.

## 72. Load testing

Separate:
- host throughput;
- planner/model latency;
- DAG scheduler;
- Toolbox;
- Search;
- memory.

Model/provider latency often dominates; orchestration still must avoid unnecessary serial work.

## 73. Chaos testing

Inject:
- Toolbox timeout;
- Search outage;
- Redis loss;
- DB loss;
- model throttling;
- verifier failure;
- approval delay;
- worker restart.

Validate durable recovery.

## 74. Multi-tenancy

Hard boundaries:
- identity;
- run state;
- memory;
- search ACLs;
- artifacts;
- audit;
- credentials.

Do not rely on prompt instructions for isolation.

## 75. Data residency

Regionalize:
- memory;
- search;
- artifacts;
- logs;
- credentials;
- Toolbox endpoints where required.

## 76. Cell architecture

```text
Global control plane
       |
+------+------+
|             |
EU cell      US cell
|             |
Hosted Agent Hosted Agent
Toolbox      Toolbox
Memory       Memory
Search       Search
```

## 77. Disaster recovery

Back up:
- durable run state;
- memory;
- Toolbox configuration/version metadata;
- policy;
- search source data/config;
- audit.

Practice restore.

## 78. Deployment strategy

```text
dev
 |
integration
 |
security/evaluation
 |
staging
 |
canary agent version
 |
production
```

Promote code and Toolbox versions independently but record the combination.

## 79. Supply chain

Use:
- pinned dependencies;
- SBOM;
- image scanning;
- signing;
- provenance;
- minimal base image.

## 80. Local run

```bash
unzip foundry-enterprise-agent-toolbox-production.zip
cd foundry-enterprise-agent-toolbox
cp .env.example .env
docker compose up --build
```

Verify:

```bash
curl http://localhost:8130/health/live
curl http://localhost:8130/metrics
```

## 81. Run an enterprise request locally

```bash
curl -s -X POST http://localhost:8130/v1/run \
  -H 'content-type: application/json' \
  -d '{
    "request":"Research the incident, inspect enterprise knowledge, and prepare a workflow"
  }' | python -m json.tool
```

With no Toolbox endpoint, the tool layer uses deterministic local fixtures.

## 82. Approval demonstration

```bash
curl -s -X POST 'http://localhost:8130/v1/run' \
  -H 'content-type: application/json' \
  -d '{"request":"Research the issue and send an update"}' | python -m json.tool
```

The Action Agent returns `approval_required`.

For local demonstration only:

```bash
curl -s -X POST 'http://localhost:8130/v1/run?approved=true' \
  -H 'content-type: application/json' \
  -d '{"request":"Research the issue and send an update"}' | python -m json.tool
```

Production must replace this query flag with the bound approval service described above.

## 83. Inspect memory

```bash
curl http://localhost:8130/v1/memory | python -m json.tool
```

You will see all seven memory layer keys.

## 84. Native run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
export ENV=dev
uvicorn app.main:app --reload --port 8130
```

## 85. Tests

```bash
pytest -q
ruff check .
```

## 86. Connect real Foundry Toolbox

Set:

```bash
export TOOLBOX_ENDPOINT='https://.../mcp?...'
```

Authenticate locally:

```bash
az login
```

`DefaultAzureCredential` can then use the Azure CLI identity in local development.

In a Hosted Agent deployment, prefer managed agent identity.

## 87. Foundry deployment prerequisites

You need:
- Azure subscription;
- Foundry project;
- model deployment;
- Toolbox with a default version;
- appropriate RBAC;
- Azure Developer CLI for the documented `azd` flow.

## 88. Install Foundry extras

Because current Microsoft Python hosting packages can be prerelease/beta, keep them isolated:

```bash
pip install -e '.[foundry]'
```

Check Microsoft documentation for the current supported package versions before production deployment.

## 89. LangGraph hosting

The project includes:

```text
langgraph.json
foundry/langgraph_entry.py
foundry/azure.yaml
```

The compiled graph can be exposed through Microsoft's LangGraph Foundry hosting integration.

## 90. Agent Framework hosting

For a Microsoft Agent Framework-native host, wrap the same Supervisor/domain services with the Agent Framework hosting server.

This keeps business orchestration reusable.

## 91. Deployment command concept

Microsoft's current Hosted Agent flow uses Azure Developer CLI/Foundry tooling.

A typical lifecycle is:

```text
az login / azd auth login
build/test locally
azd agent tooling
deploy hosted container
invoke Responses/Invocations endpoint
```

Use the exact current commands from Microsoft documentation because the Hosted Agent CLI surface can evolve.

## 92. Production PostgreSQL

Add tables:

```text
runs
plan_versions
tasks
task_attempts
events
approvals
artifacts
memory_episodes
semantic_memories
procedures
entities
```

## 93. Durable LangGraph checkpointer

Use a durable checkpointer for graph state.

The hosted platform can preserve session state, but application workflow state still needs explicit durability semantics for business-critical execution.

## 94. Azure AI Search ACLs

Filter retrieval using trusted user/tenant attributes.

Never retrieve all documents and ask the model to ignore unauthorized chunks.

## 95. Search freshness

Store:
- source version;
- ingestion timestamp;
- validity;
- last modified.

Verifier can reject stale evidence for time-sensitive requests.

## 96. Evidence contract

Every externally supported claim should reference:

```text
source
tool
retrieved_at
document/version
chunk/record ID
```

## 97. Critic vs verifier

Critic:
- adversarial reasoning;
- asks what may be wrong.

Verifier:
- checks explicit acceptance criteria.

Separate them for high-stakes workflows.

## 98. Human-in-the-loop

Human intervention points:
- consequential action approval;
- ambiguous business choice;
- verifier failure;
- policy exception.

Do not require human approval for every internal reasoning step.

## 99. Workflow pause/resume

On approval:

```text
RUNNING
 |
WAITING_APPROVAL
 |
approved event
 |
READY
 |
RUNNING
```

Persist state before notifying the human.

## 100. Event-driven continuation

Production can use:
- durable queue;
- event bus;
- webhook;
- Durable Task;
- workflow engine.

Do not keep an HTTP request open for hours.

## 101. Artifact storage

Large code/files/reports should go to object storage.

Graph state stores references, hashes and metadata rather than megabyte payloads.

## 102. Code interpreter

Treat generated code and output as untrusted.

Use Toolbox/Foundry-managed code execution or a dedicated sandbox and enforce file/network limits.

## 103. Browser automation

Use for sites without robust APIs.

Prefer API/MCP tools when deterministic interfaces exist.

Browser actions that submit forms or purchases are consequential writes.

## 104. A2A

A Toolbox can expose/use A2A capabilities where supported.

Remote agents should have:
- identity;
- capability metadata;
- bounded delegation;
- timeout;
- audit;
- policy.

## 105. Work IQ / enterprise context

Where available, enterprise intelligence tools can enrich agent context.

They remain data sources, not authorization sources.

## 106. OpenAPI tools

OpenAPI is valuable for enterprise REST services.

Generate tool schemas from curated specs, then apply gateway policy around methods/resources.

## 107. File search

Useful for scoped uploaded/project files.

Preserve ACL/provenance and classify retrieved content.

## 108. Tool Search

At large tool counts, do not expose every schema to the model.

Use Toolbox Tool Search/progressive disclosure where available and a policy-aware discovery layer.

## 109. Sessions

Hosted sessions improve conversational continuity.

Do not confuse session continuity with durable business workflow correctness.

## 110. Session security

Bind session state to trusted user/tenant context supplied by the hosting platform.

Local development must implement its own identity/state controls.

## 111. Session vs memory

Session:
- interaction/runtime continuity.

Memory:
- explicit application semantics and retention.

Keep them conceptually separate.

## 112. Session vs workflow

A user conversation may start multiple durable workflows.

Use unique run IDs rather than treating conversation ID as the workflow primary key.

## 113. Failure taxonomy

```text
PLANNING_FAILED
RETRIEVAL_FAILED
TOOL_DENIED
APPROVAL_REQUIRED
TOOL_TIMEOUT
TOOL_PROTOCOL_ERROR
CODE_FAILED
ACTION_UNKNOWN
VERIFICATION_FAILED
MEMORY_WRITE_FAILED
INTERNAL_ERROR
```

## 114. Graceful degradation

Web search unavailable:
- continue with internal evidence if request permits.

Knowledge unavailable:
- mark missing evidence.

Action gateway unavailable:
- do not bypass.

Verifier unavailable:
- high-assurance workflows should not claim verified success.

## 115. Runbook: Toolbox unavailable

1. stop dependent task execution;
2. preserve run state;
3. retry safe reads with bounds;
4. do not bypass security gateway;
5. alert on sustained outage.

## 116. Runbook: poisoned source

1. quarantine source/version;
2. invalidate caches;
3. find runs that consumed it;
4. re-run verifier;
5. update ingestion trust policy.

## 117. Runbook: compromised agent version

1. stop/canary rollback;
2. revoke identity if needed;
3. pin previous version;
4. inspect tool/audit traces;
5. invalidate unsafe pending approvals.

## 118. Runbook: runaway DAG

Enforce:
- max nodes;
- max depth;
- max steps;
- max parallelism;
- max wall time;
- max spend.

Cancel the run and preserve diagnostic state.

## 119. Principal-level tradeoff: one framework or two

Do not use Agent Framework and LangGraph merely for résumé keywords.

Use a clear ownership model:
- one primary graph runtime;
- adapters to the other ecosystem where useful.

This repository keeps the orchestration domain independent to demonstrate both without creating double scheduling.

## 120. Principal-level tradeoff: Hosted Agent vs self-host

Hosted Agent:
- managed scale/session/identity/lifecycle;
- tighter Foundry integration.

Self-host:
- maximum infrastructure control;
- custom networking/runtime.

Choose based on enterprise constraints, not novelty.

## 121. Principal-level tradeoff: Toolbox vs direct integrations

Toolbox:
- centralized, versioned, reusable tool plane.

Direct:
- useful for capabilities not supported in Toolbox or requiring custom execution.

A large enterprise may use both behind the same gateway.

## 122. Principal-level tradeoff: multi-agent vs single-agent

Multi-agent is justified when roles have materially different:
- tools;
- security;
- context;
- evaluation;
- lifecycle.

Do not split agents only to make the architecture look complex.

## 123. Principal-level tradeoff: seven memories

Seven layers are useful only if retention and retrieval semantics differ.

Otherwise they become seven names for one ungoverned vector database.

## 124. Principal-level tradeoff: critic cost

Run the Critic/Verifier selectively based on:
- risk;
- confidence;
- evidence quality;
- cost.

High-risk actions deserve stronger verification.

## 125. Narrative

> I host custom orchestration in Foundry so Microsoft manages runtime, sessions, identity, scaling and protocol endpoints, while my code owns business logic. A typed supervisor compiles requests into a bounded DAG and delegates to specialists for research, enterprise knowledge, coding, workflow construction and actions. Tools are centralized behind a versioned Foundry Toolbox MCP endpoint, but every consequential call still passes through an independent capability/security gateway. Results carry provenance into a critic/verifier, and state is separated into seven memory semantics. Durable task state, idempotency, approvals, ACL-aware RAG and end-to-end telemetry make the system suitable for long-running enterprise workflows rather than just a chat demo.

## 126. Why this is Principal-level

The difficult problems are not writing five prompts.

They are:
- authority;
- state;
- durability;
- versioning;
- retrieval correctness;
- data boundaries;
- side-effect semantics;
- evaluation;
- multi-region operations;
- cost;
- failure recovery.

The architecture treats those as first-class.

## 127. Production roadmap

Phase 1: runnable local DAG and Toolbox abstraction.

Phase 2: real Foundry Hosted Agent + Toolbox.

Phase 3: durable PostgreSQL/checkpointer.

Phase 4: security firewall/approval.

Phase 5: Azure AI Search ACL-aware RAG.

Phase 6: enterprise memory stores.

Phase 7: OTel/evaluation.

Phase 8: distributed workers/durable events.

Phase 9: regional cells/DR.

## 128. Production readiness checklist

- [ ] Foundry Hosted Agent deployed
- [ ] dedicated Entra identity
- [ ] Toolbox version pinned/promoted
- [ ] least-privilege RBAC
- [ ] capability firewall
- [ ] exact-action approval
- [ ] durable run/task state
- [ ] idempotency/reconciliation
- [ ] ACL-aware Azure AI Search
- [ ] provenance
- [ ] durable seven-layer memory
- [ ] sandboxed code
- [ ] bounded DAG
- [ ] cancellation/deadlines
- [ ] OTel traces
- [ ] security audit
- [ ] evaluation suite
- [ ] load/chaos tests
- [ ] DR
- [ ] cost budgets

## 129. Repository layout

```text
app/
  main.py
  config.py
  models.py
  security.py
  planner.py
  orchestrator.py
  agents.py
  gateway.py
  toolbox.py
  memory.py
  graph.py
foundry/
  hosted_agent.py
  langgraph_entry.py
  azure.yaml
tests/
docs/
langgraph.json
Dockerfile
docker-compose.yml
```

## 130. Final principle

```text
Probabilistic intelligence
        |
        v
Typed orchestration
        |
        v
Bounded specialist agents
        |
        v
Deterministic security boundary
        |
        v
Versioned enterprise capabilities
        |
        v
Verifiable evidence
        |
        v
Durable governed memory
```

The agent should be flexible in reasoning but strict in authority, state transitions, evidence and side effects.

# Professional Complete Architecture & Operations Guide

This section extends the runnable implementation into a complete Principal/Staff-level engineering guide for Microsoft Foundry Hosted Agents, Microsoft Agent Framework, LangGraph, Foundry Toolbox/MCP, enterprise RAG, governed action execution, verification, memory, durability, security, observability, deployment and operations.

---

## 131. End-to-end production architecture

```text
                              ENTERPRISE CLIENT
                                     |
                                     v
                           Foundry Agent Endpoint
                                     |
                                     v
                      Microsoft Foundry Hosted Agent
                                     |
                   +-----------------+-----------------+
                   |                                   |
                   v                                   v
          Microsoft Agent Framework                 LangGraph
                   |                                   |
                   +-----------------+-----------------+
                                     |
                                     v
                               SUPERVISOR
                                     |
                              typed plan IR
                                     |
                                     v
                                 TASK DAG
            +------------------------+-----------------------+
            |                        |                       |
            v                        v                       v
      Research Agent          Knowledge Analyst        Analysis Agent
            |                        |                       |
            +------------+-----------+-----------+-----------+
                         |                       |
                         v                       v
                    Coder Agent            Workflow Agent
                         \                       /
                          \                     /
                           +---------+---------+
                                     |
                                     v
                                Action Agent
                                     |
                                     v
                         Capability/Security Gateway
                                     |
                   +-----------------+-----------------+
                   |                 |                 |
                   v                 v                 v
               Identity           Policy          Approval/DLP
                   |                 |                 |
                   +-----------------+-----------------+
                                     |
                                     v
                              Foundry Toolbox
                                     |
                                MCP endpoint
                                     |
          +--------------------------+---------------------------+
          |             |             |             |           |
          v             v             v             v           v
       Web Search   Azure AI Search  OpenAPI     Browser      A2A/MCP
          |             |             |             |           |
          +-------------+-------------+-------------+-----------+
                                     |
                                     v
                              Critic / Verifier
                                     |
                                     v
                              Evidence Ledger
                                     |
                                     v
                             SEVEN-LAYER MEMORY
```

The central engineering principle is separation of probabilistic reasoning from deterministic execution authority.

---

## 132. Control plane versus data plane

### Control plane

Owns:
- agent versions;
- Toolbox versions;
- policies;
- prompts;
- model configuration;
- agent capability manifests;
- deployment;
- evaluation;
- memory schemas;
- security configuration.

### Data plane

Owns:
- live requests;
- task execution;
- tool invocation;
- RAG retrieval;
- model calls;
- approval waits;
- artifacts;
- memory reads/writes;
- telemetry.

Keeping these separate makes rollout, rollback and security review substantially safer.

---

## 133. Request lifecycle

```text
1. Authenticate request.
2. Resolve tenant/user/session.
3. Create durable run.
4. Compile request into typed Task DAG.
5. Validate DAG.
6. Persist immutable plan version.
7. Schedule ready tasks.
8. Specialist agents gather evidence/work.
9. Consequential calls pass Security Gateway.
10. Gateway calls Foundry Toolbox/MCP.
11. Results are classified and recorded.
12. Critic challenges result.
13. Verifier evaluates acceptance criteria.
14. Memory candidates are consolidated.
15. Final answer/evidence returned.
16. Run/audit telemetry finalized.
```

---

## 134. `app/main.py`

The HTTP/API boundary.

Responsibilities:
- parse enterprise request;
- authenticate principal;
- invoke Supervisor;
- expose memory inspection in development;
- expose Prometheus metrics.

Production route handlers should remain thin.

---

## 135. `app/config.py`

Centralized environment configuration.

Important production rule:

```text
configuration identifies resources;
identity grants access to them.
```

Never put bearer tokens or client secrets into normal application configuration.

---

## 136. `app/models.py`

Contains the typed domain contract:
- `EnterpriseRequest`;
- `Task`;
- `Plan`;
- `AgentResult`;
- `FinalResponse`.

Typed models are a critical safety boundary because they prevent free-form model prose from becoming executable control state.

---

## 137. `app/planner.py`

The included planner is deterministic so the repository works without a model deployment.

Production upgrade:

```text
enterprise request
      |
structured-output LLM planner
      |
Pydantic Plan
      |
static validator
      |
policy analyzer
      |
immutable plan version
```

The LLM proposes; deterministic validation decides whether the proposal is executable.

---

## 138. Planner validation

Validate:
- unique task IDs;
- known task kinds;
- existing dependencies;
- no cycles;
- maximum nodes;
- maximum depth;
- maximum fan-out;
- permitted risk;
- permitted tools/capabilities;
- bounded dynamic expansion.

---

## 139. Plan hash

Canonicalize and hash:

```text
plan_version_hash =
 SHA256(canonical_json(plan))
```

Use it in:
- audit;
- approvals;
- resume;
- evaluation;
- incident analysis.

---

## 140. Plan immutability

Do not mutate a running plan invisibly.

Replanning produces:

```text
plan v1
   |
reason/event
   |
plan v2
```

Both remain auditable.

---

## 141. `app/orchestrator.py`

The Supervisor performs dependency-aware scheduling.

The runnable implementation:
- calculates ready nodes;
- executes independent nodes concurrently;
- collects results;
- persists memory records;
- stops at approval boundaries;
- invokes verifier.

Production moves task state into a durable repository/queue rather than process memory.

---

## 142. Ready-set algorithm

For task `T`:

```text
READY(T) =
 T.status == PENDING
 AND
 every dependency is terminal-success
```

Complexity can remain O(V+E) with maintained dependency counters.

---

## 143. Scheduler fairness

Production scheduling should consider:

```text
priority
tenant weight
risk
provider quota
agent class
deadline
cost budget
```

Avoid one tenant monopolizing workers.

---

## 144. Concurrency hierarchy

Bound:

```text
global
tenant
run
agent type
Toolbox
individual tool/provider
```

This prevents cascading overload.

---

## 145. `app/agents.py`

Specialists expose a common conceptual interface:

```text
run(principal, task, context) -> AgentResult
```

This allows:
- independent testing;
- policy specialization;
- model specialization;
- tool specialization;
- per-agent evaluation.

---

## 146. Research Agent production design

Responsibilities:
- current public information;
- multi-source retrieval;
- evidence collection;
- freshness.

Output contract should include:

```text
claim
source
retrieved_at
source_timestamp
confidence
```

---

## 147. Knowledge Analyst production design

Responsibilities:
- enterprise retrieval;
- ACL-aware search;
- internal policy/product knowledge;
- evidence provenance.

Preferred pipeline:

```text
query rewrite
 |
identity/ACL filter
 |
Azure AI Search
 |
hybrid retrieval
 |
semantic rerank
 |
evidence pack
```

---

## 148. Analysis Agent

A dedicated Analysis Agent is valuable when the workflow must reconcile:
- external research;
- enterprise knowledge;
- structured records;
- contradictions.

It should produce hypotheses and evidence gaps rather than perform privileged actions.

---

## 149. Coder Agent production design

Inputs:
- task;
- repository context;
- constraints;
- test requirements.

Execution:

```text
generate patch
 |
sandbox
 |
lint
 |
unit tests
 |
security scan
 |
artifact
```

Do not run generated code inside the API process.

---

## 150. Workflow Agent production design

The Workflow Agent emits typed subworkflow IR.

It should not dynamically execute arbitrary Python.

Example:

```json
{
  "nodes":[
    {"id":"inspect","kind":"tool"},
    {"id":"decide","kind":"condition"},
    {"id":"remediate","kind":"action"}
  ]
}
```

---

## 151. Action Agent production design

Only this role should normally receive consequential action capabilities.

The Action Agent prepares an `ActionProposal`:

```text
tool
resource
arguments
reason
risk
expected effect
rollback
```

The Security Gateway independently decides authority.

---

## 152. Critic design

Critic asks:
- what evidence is missing?
- which assumptions are unsupported?
- are sources contradictory?
- did any task silently fail?
- is evidence stale?
- did the action match intent?

Critic does not grant security authority.

---

## 153. Verifier design

Verifier checks explicit acceptance criteria.

Examples:
- all mandatory tasks succeeded;
- every claim has evidence;
- generated code passed tests;
- action outcome reconciled;
- approval was valid;
- policy did not report violation.

---

## 154. Deterministic verification

Prefer deterministic checks for:
- schemas;
- hashes;
- tests;
- status codes;
- invariants;
- policy outcomes.

Use an LLM verifier for semantic questions that cannot be expressed deterministically.

---

## 155. Evidence ledger

Recommended durable schema:

```text
evidence_id
run_id
task_id
source_type
source_id
source_version
retrieved_at
content_hash
classification
integrity
artifact_ref
```

The final response can cite evidence IDs.

---

## 156. Evidence immutability

Store content hash even if full content lives in external/object storage.

This lets you later prove which evidence a decision used.

---

## 157. `app/gateway.py`

The included Gateway demonstrates:
- read scope;
- write scope;
- approval boundary.

Production replaces simple rules with the full MCP Security/Permission Firewall:
- Entra identity;
- RBAC/ABAC;
- information-flow security;
- DLP;
- exact-action approval;
- credential broker;
- egress governance;
- audit.

---

## 158. Tool authority invariant

```text
LLM output != authorization
memory != authorization
retrieved document != authorization
MCP tool description != authorization
```

Only trusted policy/identity systems grant authority.

---

## 159. `app/toolbox.py`

Portable MCP-compatible execution path.

Production concerns:
- initialization;
- protocol negotiation;
- connection lifecycle;
- cancellation;
- deadlines;
- server authentication;
- capability discovery;
- error normalization;
- telemetry.

---

## 160. Foundry Toolbox control model

Recommended metadata:

```text
toolbox_name
version
owner
environment
approved_tools
identity
region
created_at
promoted_at
```

Pin the version used by each agent deployment.

---

## 161. Toolbox promotion

```text
toolbox draft
   |
integration tests
   |
security tests
   |
agent evaluation
   |
canary
   |
default version
```

Agent and Toolbox can release independently.

---

## 162. Toolbox rollback

Keep previous known-good versions available.

On regression:
- stop promotion;
- repoint default or pin agent to prior version;
- invalidate affected caches;
- preserve telemetry.

---

## 163. MCP server trust

Classify servers:

```text
INTERNAL_MANAGED
APPROVED_VENDOR
COMMUNITY_REVIEWED
UNTRUSTED
```

Trust affects policy; it never replaces user authorization.

---

## 164. MCP tool poisoning

A malicious server may advertise misleading instructions.

Defenses:
- immutable reviewed tool metadata;
- separate security metadata;
- allowlists;
- output treated as untrusted;
- no tool description can override system policy.

---

## 165. MCP sampling

Server-initiated model requests need separate governance:
- server trust;
- model;
- token budget;
- data classification;
- request count.

Default-deny for unknown servers is a strong baseline.

---

## 166. MCP elicitation

Treat server-requested user input as untrusted.

Never request secrets solely because a server asks.

---

## 167. MCP tasks

Long-running MCP operations need:
- task identity;
- durable status;
- cancellation;
- reauthorization before consequential continuation;
- audit.

---

## 168. OpenAPI capability

For enterprise REST APIs:
- curate spec;
- restrict operations;
- normalize resource IDs;
- validate request schema;
- enforce endpoint policy;
- use short-lived credential.

---

## 169. Browser automation capability

Use when APIs are unavailable.

Policy distinguishes:
- navigation/read;
- file download;
- upload;
- form submission;
- purchase;
- irreversible confirmation.

Browser session should be isolated.

---

## 170. Code Interpreter capability

Useful for:
- data analysis;
- transformations;
- generated code testing.

Treat files/code as untrusted and limit:
- CPU;
- memory;
- disk;
- network;
- runtime.

---

## 171. A2A capability

Remote agents need:
- authenticated identity;
- agent card/capabilities;
- bounded delegation;
- deadlines;
- cancellation;
- trace propagation;
- policy.

A remote agent does not inherit unlimited parent authority.

---

## 172. Azure AI Search production schema

Typical fields:

```text
id
tenant_id
document_id
chunk_id
title
content
embedding
source_uri
source_version
acl_principals
classification
modified_at
```

---

## 173. ACL-aware retrieval

Authorization must be pushed into retrieval:

```text
query
AND tenant_id == principal.tenant
AND ACL intersects principal identities
```

Do not retrieve unauthorized chunks and rely on the model to ignore them.

---

## 174. Hybrid retrieval

Combine:
- lexical/BM25;
- vector;
- semantic reranking;
- metadata filters.

Different enterprise queries benefit from different signals.

---

## 175. Query rewriting

The Knowledge Analyst may create:
- semantic query;
- keywords;
- entity filters;
- time filters.

Keep trusted security filters separate from model-generated query content.

---

## 176. Retrieval freshness

Time-sensitive requests should incorporate:

```text
modified_at
valid_from
valid_until
retrieved_at
```

Verifier can reject stale evidence.

---

## 177. Retrieval conflict handling

If two documents disagree:
- preserve both;
- compare timestamps/authority;
- flag contradiction;
- avoid silently selecting one.

---

## 178. Seven-layer memory architecture

```text
                     Memory Router
                          |
   +----------+-----------+-----------+-----------+
   |          |           |           |           |
Working   Conversation Episodic   Semantic   Procedural
   |          |           |           |           |
 Redis     session/DB   Postgres   vector/DB    Postgres
                          |
                   +------+------+
                   |             |
                 Entity        Audit
                 graph      append-only
```

---

## 179. Working memory lifecycle

TTL: minutes/hours.

Contains only run-local state.

Delete/expire aggressively.

---

## 180. Conversation memory lifecycle

TTL/retention depends on product requirements.

Summarize older turns rather than indefinitely increasing context.

---

## 181. Episodic memory schema

```text
episode_id
tenant
principal
run
task
event
outcome
timestamp
evidence_refs
```

---

## 182. Semantic memory schema

```text
fact_id
subject
predicate
object/value
confidence
valid_from
valid_to
source_episode
supersedes
```

---

## 183. Procedural memory schema

```text
procedure_id
intent_pattern
steps
success_count
failure_count
last_validated
owner
version
```

Procedures must still pass current policy.

---

## 184. Entity memory

Possible graph:

```text
Service -> owned_by -> Team
Service -> depends_on -> Database
Incident -> affected -> Service
Repository -> deploys -> Service
```

Graph traversal can enrich planning.

---

## 185. Audit memory

Audit is not ordinary LLM memory.

Properties:
- append-only;
- restricted;
- retention governed;
- tamper-evident where required.

---

## 186. Memory consolidation

Pipeline:

```text
episodes
 |
candidate extraction
 |
dedup
 |
contradiction check
 |
confidence
 |
provenance
 |
semantic/procedural/entity memory
```

---

## 187. Memory contradiction

Never overwrite silently.

Example:

```text
fact v1 valid until t2
fact v2 valid from t2
```

Preserve temporal history.

---

## 188. Memory privacy

Support:
- retention;
- deletion;
- export;
- tenant isolation;
- classification;
- purpose limitation.

Do not copy sensitive data into every memory layer.

---

## 189. Durable run database

Recommended PostgreSQL tables:

```text
runs
plan_versions
tasks
task_attempts
events
approvals
artifacts
evidence
memory_candidates
```

---

## 190. Run record

```text
run_id
tenant
principal
session
status
active_plan_version
created_at
updated_at
deadline
cost_budget
```

---

## 191. Task record

```text
task_id
run_id
plan_version
kind
status
risk
dependencies
attempt
lease_owner
lease_expiry
fencing_token
```

---

## 192. Durable event log

Examples:

```text
RUN_CREATED
PLAN_COMPILED
TASK_READY
TASK_STARTED
TOOL_CALLED
APPROVAL_REQUESTED
APPROVAL_GRANTED
TASK_SUCCEEDED
PLAN_REVISED
RUN_VERIFIED
RUN_COMPLETED
```

---

## 193. Transactional outbox

When DB state and external event publication must agree:

```text
transaction:
  update task
  insert outbox event
commit
```

A publisher sends the event later.

---

## 194. Worker architecture

```text
Scheduler
   |
durable queue
   |
+-- Research workers
+-- Knowledge workers
+-- Code workers
+-- Action workers
+-- Verification workers
```

Workers should be stateless apart from leased work.

---

## 195. Worker lease

Acquire atomically:

```text
task
lease_owner
lease_expiry
fencing_token++
```

Every state mutation checks the fencing token.

---

## 196. Heartbeats

Long tasks renew lease.

If heartbeat expires, scheduler can reassign after checking operation semantics.

---

## 197. Durable timers

Use persisted timers for:
- retry;
- approval expiry;
- scheduled continuation;
- polling.

Do not depend on `asyncio.sleep` for hours-long production timers.

---

## 198. Approval pause

Before returning `WAITING_APPROVAL`:
1. persist state;
2. persist exact action hash;
3. commit;
4. notify approver.

This avoids lost approvals.

---

## 199. Approval resume

```text
approval event
 |
validate exact action
 |
mark approval consumed
 |
task READY
 |
worker executes
```

---

## 200. Idempotency

Key:

```text
tenant + run + task + semantic operation
```

Store request hash and terminal result.

---

## 201. Side-effect reconciliation

For ambiguous write outcome:
- query downstream state;
- compare expected effect;
- mark succeeded or safe-to-retry.

---

## 202. Saga compensation

Represent compensation explicitly:

```text
forward_task
compensation_task
compensation_policy
```

Compensation may itself require approval.

---

## 203. Cancellation model

States:

```text
CANCEL_REQUESTED
CANCELLING
CANCELLED
```

Propagate to model/tool/sandbox where supported.

---

## 204. Deadline propagation

Each child gets:

```text
remaining_deadline =
 parent_deadline - elapsed
```

This prevents stacked timeouts from exceeding user SLA.

---

## 205. Cost budget propagation

Run budget can allocate:

```text
planner
research
knowledge
coder
tools
verifier
```

A child cannot exceed remaining budget.

---

## 206. Model fallback

Fallback should consider:
- capability;
- data region;
- cost;
- latency;
- safety;
- evaluation quality.

Do not silently change to a model that violates data policy.

---

## 207. Model version recording

Audit:
- deployment;
- model family/version if available;
- prompt version;
- temperature/config.

Necessary for regression analysis.

---

## 208. Prompt versioning

Treat prompts like code:

```text
prompt ID
version
owner
evaluation score
promotion state
```

---

## 209. Agent manifest

Recommended:

```text
agent_id
version
role
models
allowed_tool_classes
memory_access
risk_ceiling
owner
evaluation_suite
```

---

## 210. Security Gateway input

```text
principal
agent identity
tool/version
arguments
resource
risk
data labels
delegation
approval
run/task
```

---

## 211. Security Gateway output

```text
ALLOW
DENY
APPROVAL_REQUIRED
```

plus obligations:
- sandbox;
- redact;
- output limit;
- audit level;
- credential profile.

---

## 212. Exact-action approval

Bind:

```text
principal
tenant
agent
tool/version
resource
canonical args hash
plan hash
expiry
nonce
```

This prevents substitution.

---

## 213. Credential brokerage

```text
Gateway
 |
approved action
 |
Credential Broker
 |
short-lived downstream credential
 |
Toolbox/tool
```

Credentials never enter model context.

---

## 214. Information-flow integrity

Label:
- trusted user instruction;
- internal governed data;
- arbitrary web;
- external email;
- MCP output.

Untrusted content should not directly control privileged sinks.

---

## 215. Confidentiality

Example lattice:

```text
PUBLIC < INTERNAL < CONFIDENTIAL < RESTRICTED
```

Destination policy determines permitted flow.

---

## 216. DLP

Apply before external disclosure:
- secret scan;
- PII classifier;
- enterprise data rules;
- destination policy.

Outcomes:
- allow;
- redact;
- approval;
- deny.

---

## 217. Tool output security

Tool output can contain prompt injection.

Treat output as data, not policy.

Validate:
- size;
- schema;
- classification;
- integrity.

---

## 218. Tool discovery integration

For thousands of capabilities:

```text
request
 |
domain filter
 |
policy prefilter
 |
BM25/vector retrieval
 |
rerank
 |
top-K
 |
model selection
 |
invocation firewall
```

---

## 219. Discovery security

Do not disclose tools the principal can never use if their existence is sensitive.

Discovery filtering is not a substitute for invocation authorization.

---

## 220. Agent delegation

Effective child authority:

```text
child_authority =
 intersection(
   user authority,
   parent delegation,
   child agent policy
 )
```

Never union authority.

---

## 221. A2A delegation

Delegation token can bind:
- parent agent;
- child agent;
- run;
- scopes;
- capability classes;
- expiry.

---

## 222. Multi-agent loops

Prevent:
- A delegates to B;
- B delegates back to A indefinitely.

Track:
- delegation depth;
- visited agents;
- max hops;
- budget.

---

## 223. Observability architecture

```text
Hosted Agent
   |
OTel SDK
   |
OTel Collector
   |
+-- Azure Monitor/Application Insights
+-- Prometheus
+-- logs/SIEM
+-- evaluation store
```

---

## 224. Trace attributes

Low-cardinality:
- agent;
- task kind;
- tool;
- status;
- risk.

IDs such as run/task belong in spans/logs but generally not Prometheus labels.

---

## 225. Metrics

Recommended:

```text
agent_runs_total
agent_run_duration
task_runs_total
task_duration
tool_calls_total
tool_latency
approval_wait
verifier_rejections
retrieval_latency
retrieval_documents
memory_reads/writes
model_tokens
estimated_cost
unknown_write_outcomes
```

---

## 226. Security metrics

```text
policy_denials
approval_requests
DLP_blocks
cross_tenant_attempts
tool_poisoning_alerts
sandbox_violations
credential_failures
```

---

## 227. Evaluation metrics

Planning:
- task precision/recall;
- dependency correctness.

Retrieval:
- Recall@K;
- MRR;
- nDCG.

Agent:
- task success;
- groundedness;
- instruction adherence.

Verifier:
- true rejection/false rejection.

---

## 228. Business metrics

Examples:
- incident resolution time;
- research turnaround;
- support resolution;
- developer cycle time;
- workflow completion.

Infrastructure metrics alone do not prove business value.

---

## 229. SLO decomposition

User-visible latency:

```text
gateway
+ planning
+ critical-path tasks
+ tools/models
+ verification
```

Parallel tasks contribute maximum critical-path latency rather than sum.

---

## 230. Critical path optimization

Prioritize:
- tasks on critical path;
- early evidence retrieval;
- parallel independent reads.

Avoid speculative consequential actions.

---

## 231. Caching

Safe candidates:
- public search;
- stable knowledge;
- tool metadata.

Avoid caching:
- authorization;
- rapidly changing operational state;
- sensitive personalized results without correct keying.

---

## 232. Semantic cache

Key by:
- tenant;
- authorization scope;
- corpus version;
- semantic query.

Otherwise semantic cache can leak cross-tenant information.

---

## 233. Deployment: local prerequisites

Recommended:
- Docker 24+;
- Docker Compose v2;
- Python 3.11+ for native run;
- curl.

Azure deployment additionally requires:
- Azure subscription;
- Foundry project;
- model deployment;
- Toolbox;
- RBAC;
- Azure CLI/Azure Developer CLI as required by current Microsoft tooling.

---

## 234. Local Docker run

```bash
unzip foundry-enterprise-agent-toolbox-professional-complete.zip
cd foundry-enterprise-agent-toolbox
cp .env.example .env
docker compose up --build
```

---

## 235. Verify local service

```bash
curl http://localhost:8130/health/live
curl http://localhost:8130/metrics
```

API docs:

```text
http://localhost:8130/docs
```

---

## 236. Docker background run

```bash
docker compose up --build -d
docker compose ps
docker compose logs -f agent
```

Stop:

```bash
docker compose down
```

Delete local DB/cache state:

```bash
docker compose down -v
```

---

## 237. Native run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
export ENV=dev
uvicorn app.main:app --host 0.0.0.0 --port 8130 --reload
```

---

## 238. Run tests

```bash
pytest -q
ruff check .
```

---

## 239. Run research/knowledge workflow

```bash
curl -s -X POST http://localhost:8130/v1/run \
  -H 'content-type: application/json' \
  -d '{
    "request":
      "Research the incident, inspect enterprise knowledge, and prepare a workflow"
  }' | python -m json.tool
```

---

## 240. Run code-oriented workflow

```bash
curl -s -X POST http://localhost:8130/v1/run \
  -H 'content-type: application/json' \
  -d '{
    "request":
      "Research the production issue and implement a diagnostic script"
  }' | python -m json.tool
```

This adds the Coder task.

---

## 241. Run action workflow

```bash
curl -s -X POST http://localhost:8130/v1/run \
  -H 'content-type: application/json' \
  -d '{
    "request":"Research the incident and send an update"
  }' | python -m json.tool
```

Expected local behavior:

```text
approval_required
```

---

## 242. Local approval demonstration

```bash
curl -s -X POST 'http://localhost:8130/v1/run?approved=true' \
  -H 'content-type: application/json' \
  -d '{"request":"Research the incident and send an update"}' \
  | python -m json.tool
```

This query flag exists only for local demonstration.

Production uses signed bound approvals.

---

## 243. Inspect seven-layer memory

```bash
curl http://localhost:8130/v1/memory | python -m json.tool
```

---

## 244. Connect real Toolbox

Set `.env`:

```text
TOOLBOX_ENDPOINT=<your managed MCP endpoint>
```

For local development authenticate using your organization's approved Azure identity mechanism.

The client obtains an Entra token through `DefaultAzureCredential`.

---

## 245. Connect Azure AI Search

Configure:

```text
AZURE_AI_SEARCH_ENDPOINT
AZURE_AI_SEARCH_INDEX
```

Production Knowledge Agent should use the managed Toolbox Search tool or an explicit Azure Search adapter with identity-based authentication.

---

## 246. Foundry model configuration

Set:

```text
FOUNDRY_PROJECT_ENDPOINT
FOUNDRY_MODEL_NAME
```

Use structured output for planning/agent contracts.

---

## 247. Hosted deployment files

Included:

```text
foundry/azure.yaml
foundry/hosted_agent.py
foundry/langgraph_entry.py
langgraph.json
```

Microsoft's Hosted Agent tooling evolves; validate current package/CLI commands against current Foundry documentation before deployment.

---

## 248. Foundry extras

```bash
pip install -e '.[foundry]'
```

These dependencies are isolated because some hosting SDK surfaces can evolve faster than the domain architecture.

---

## 249. LangGraph local graph

```text
foundry/langgraph_entry.py
```

exports the compiled graph.

The domain Supervisor remains reusable outside LangGraph.

---

## 250. Agent Framework adapter

Recommended production structure:

```text
Agent Framework host
 |
request adapter
 |
Supervisor service
```

Do not duplicate scheduling in both frameworks.

---

## 251. Hosted Agent identity RBAC

Grant only necessary roles to the Hosted Agent identity:
- project/model inference;
- Toolbox;
- Search;
- specific enterprise resources.

Avoid broad subscription roles.

---

## 252. Private networking

Enterprise production may require:
- private endpoints;
- VNet integration;
- egress proxy;
- DNS policy;
- firewall;
- regional resources.

---

## 253. Kubernetes alternative

The included K8s manifest demonstrates self-hosting.

For Microsoft Foundry Hosted Agent, the managed hosting platform replaces much of this infrastructure.

Keep K8s useful for:
- local enterprise deployment;
- hybrid components;
- workers;
- sandbox pools.

---

## 254. Horizontal scaling

API/Supervisor front ends should be stateless.

Durable state lives in:
- PostgreSQL;
- queue;
- checkpointer;
- object store;
- memory services.

---

## 255. Scheduler scaling

Partition by:
- tenant hash;
- run ID;
- regional cell.

Use leases/fencing to prevent duplicate ownership.

---

## 256. Worker autoscaling

Scale from:
- queue depth;
- oldest task age;
- CPU;
- provider quotas.

Different worker classes may need different policies.

---

## 257. Sandbox worker pool

Coder/browser workloads often need a separate pool:

```text
Scheduler
 |
Sandbox Queue
 |
ephemeral container/microVM workers
```

Do not give API pods Docker socket access.

---

## 258. Object storage

Store:
- generated files;
- code artifacts;
- large tool results;
- reports.

Persist:
- URI;
- hash;
- classification;
- owner;
- retention.

---

## 259. Database migrations

Use Alembic.

Production migration strategy:

```text
expand
deploy compatible code
backfill
switch
contract later
```

---

## 260. CI pipeline

```text
checkout
 |
dependency validation
 |
ruff
 |
unit tests
 |
property tests
 |
agent evaluation
 |
security tests
 |
integration tests
 |
container build
 |
SBOM/SAST/image scan
 |
sign
 |
staging
 |
canary
 |
production
```

---

## 261. Tool integration test

Test against a non-production Toolbox version.

Verify:
- tool discovery;
- schema;
- authentication;
- expected output;
- timeout;
- policy;
- failure mapping.

---

## 262. Agent evaluation gate

Before deployment require thresholds for:
- planning;
- tool selection;
- retrieval;
- groundedness;
- verifier;
- policy compliance.

---

## 263. Canary

Route small controlled traffic to new:
- agent version;
- model;
- prompt;
- Toolbox version.

Compare metrics/evaluations.

---

## 264. Rollback

Record deployment tuple:

```text
agent code version
prompt version
model deployment
Toolbox version
policy version
memory schema version
```

Rollback must restore a compatible tuple.

---

## 265. Application: autonomous SRE

Flow:

```text
incident
 |
Research: external/service status
 |
Knowledge: runbooks/architecture
 |
Analysis: correlate telemetry
 |
Workflow: remediation plan
 |
Action: restart/rollback
 |
approval
 |
Verifier
```

---

## 266. Application: enterprise research analyst

Flow:
- web research;
- internal documents;
- Azure AI Search;
- contradiction analysis;
- cited report;
- semantic memory.

No write privileges required.

---

## 267. Application: software engineering agent

Flow:
- issue;
- repository context;
- knowledge;
- code patch;
- sandbox tests;
- PR proposal;
- optional PR creation approval;
- verifier.

---

## 268. Application: executive assistant

Tools:
- calendar;
- email;
- Teams;
- enterprise search.

Reads can be automatic; sending/scheduling can be approval-gated depending on policy.

---

## 269. Application: customer support

```text
ticket
 |
customer knowledge
 |
order/account tools
 |
recommended response/action
 |
refund/change approval
 |
verification
```

---

## 270. Application: security operations

```text
alert
 |
SIEM evidence
 |
knowledge/runbooks
 |
endpoint/user inspection
 |
containment proposal
 |
approval
 |
isolation/disable action
```

---

## 271. Application: data analyst

Use:
- Search;
- data APIs;
- code interpreter;
- file tools.

Verifier checks calculations and source freshness.

---

## 272. Application: compliance review

Use:
- policy corpus;
- evidence collection;
- document analysis;
- structured findings.

Audit memory is particularly important.

---

## 273. Application: procurement workflow

Research vendors, retrieve internal procurement policy, compare, generate recommendation, and gate purchase/contract actions behind human approval.

---

## 274. Application: cloud migration assistant

Specialists:
- inventory;
- architecture knowledge;
- code/config analysis;
- migration workflow;
- controlled infrastructure actions.

---

## 275. Application: incident postmortem

Read:
- alerts;
- logs;
- deployment events;
- Teams/incident transcript.

Produce:
- timeline;
- contributing factors;
- action items;
- evidence links.

---

## 276. Application: knowledge maintenance

Detect stale/conflicting enterprise knowledge and propose updates.

Publishing changes should be governed separately from analysis.

---

## 277. Application: multi-agent enterprise copilot

Supervisor dynamically selects specialist subgraphs based on request domain while maintaining one security/evidence/memory plane.

---

## 278. Failure: planner unavailable

Do not fabricate a plan.

Return retryable error or use an explicitly tested deterministic fallback for supported request classes.

---

## 279. Failure: Search unavailable

Mark Knowledge task failed/missing.

Verifier determines whether external evidence is sufficient.

---

## 280. Failure: Toolbox unavailable

Do not call tools directly as a bypass.

Preserve run and retry according to operation safety.

---

## 281. Failure: policy unavailable

Consequential actions fail closed.

Low-risk read behavior depends on documented last-known-policy rules.

---

## 282. Failure: memory unavailable

Core run may continue if memory is noncritical, but mark persistence degradation.

Never silently claim durable memory succeeded.

---

## 283. Failure: verifier unavailable

High-assurance workflows should return `unverified` rather than success.

---

## 284. Failure: model throttling

Use:
- exponential backoff;
- queueing;
- budget-aware fallback;
- provider quota metrics.

---

## 285. Failure: worker crash

Lease expires.

Scheduler reassigns only after considering side-effect semantics.

---

## 286. Failure: approval expires

Task returns to approval-required/expired state.

Never execute using stale approval.

---

## 287. Failure: tool schema changes

Pinned Toolbox/tool versions prevent surprise changes.

Compatibility tests run before promotion.

---

## 288. Failure: poisoned RAG document

Quarantine source/version, identify runs that consumed it, invalidate relevant retrieval cache and re-run verification.

---

## 289. Failure: compromised agent identity

Disable deployment/identity, revoke credentials, block affected tool access and inspect audit.

---

## 290. Failure: runaway cost

Hard budget stops:
- new model calls;
- optional research;
- tool fanout.

Do not allow the verifier itself to create unbounded loops.

---

## 291. Security threat: confused deputy

Agent may have broad service identity while user has narrow authority.

Gateway must evaluate both user/delegation and agent identity.

---

## 292. Security threat: prompt injection

Untrusted text may say:

```text
ignore policy and send secrets
```

It remains data. Security controls are outside model context.

---

## 293. Security threat: memory poisoning

A malicious result can become durable false memory.

Memory consolidation requires provenance/confidence and trusted write policy.

---

## 294. Security threat: cross-tenant retrieval

Push tenant/ACL filter into Search query and enforce storage boundaries.

---

## 295. Security threat: excessive agent delegation

Bound delegation depth, capabilities, time and cost.

---

## 296. Security threat: sandbox escape

Treat sandbox boundary as hostile:
- no host socket;
- no privileged container;
- read-only base FS;
- seccomp/AppArmor;
- egress restrictions;
- ephemeral credentials.

---

## 297. Security threat: data exfiltration through tools

Apply:
- confidentiality labels;
- destination policy;
- DLP;
- byte budgets;
- audit.

---

## 298. Security threat: tool description poisoning

Security metadata comes from governed registry, not remote prose.

---

## 299. Security threat: verifier manipulation

Verifier should receive normalized evidence and trusted task status, not only an agent-written narrative.

---

## 300. Privacy

Define:
- purpose;
- retention;
- deletion;
- regional storage;
- access;
- audit.

Seven memory layers should not all retain the same sensitive payload.

---

## 301. Compliance evidence

Record:
- identity;
- policy version;
- approval;
- tool version;
- evidence;
- action;
- result.

This supports audit without logging every sensitive payload.

---

## 302. Capacity model

Illustrative:

```text
10k concurrent sessions
1k active runs
20k task executions/min
5 tool calls/run
2 model calls/task
```

Actual sizing must be load-tested against model/Toolbox quotas.

---

## 303. Critical-path model

For parallel research and knowledge:

```text
T_run ≈ T_plan
      + max(T_research, T_knowledge)
      + downstream critical path
      + T_verify
```

This explains why correct DAG parallelism matters.

---

## 304. Queue sizing

Use arrival/service measurements.

Monitor:
- queue depth;
- oldest age;
- worker utilization;
- downstream throttling.

---

## 305. Cost model

```text
run_cost =
 model_tokens
 + tool fees
 + Search
 + code/browser compute
 + storage
 + telemetry
```

Attribute by tenant/run/agent.

---

## 306. Principal tradeoff: managed hosting vs custom platform

Foundry Hosted Agent removes significant runtime/session/identity operational burden.

Keep custom infrastructure only where you need differentiated durability, security, workers or data-plane controls.

---

## 307. Principal tradeoff: Toolbox vs custom gateway

Toolbox provides managed tool collection/MCP access.

Custom Gateway adds:
- organization-specific policy;
- cross-framework governance;
- exact approval;
- DLP;
- cost controls;
- transport normalization.

They complement each other.

---

## 308. Principal tradeoff: LangGraph vs Agent Framework

Choose one primary orchestration owner.

Use adapters/integrations for ecosystem interoperability.

Double orchestration creates confusing state/retry ownership.

---

## 309. Principal tradeoff: supervisor intelligence

A very intelligent supervisor can adapt but becomes harder to test.

Prefer typed bounded planning plus specialist autonomy within explicit limits.

---

## 310. Principal tradeoff: verifier on every request

High assurance: always verify.

Low-risk simple requests: sample or confidence-trigger verification to control latency/cost.

---

## 311. Principal tradeoff: durable every intermediate token

Usually unnecessary.

Persist semantic task state and important artifacts/events, not every transient reasoning token.

---

## 312. Principal tradeoff: memory retrieval

Retrieve only relevant scoped memory.

Dumping all historical memory into prompts increases cost, confusion and privacy exposure.

---

## 313. Principal tradeoff: central memory vs agent-local memory

Central memory:
- consistency;
- governance.

Agent-local:
- specialization;
- isolation.

A Memory Router can provide governed shared semantics while preserving per-agent namespaces.

---

## 314. Principal tradeoff: real-time vs asynchronous workflows

Conversational request:
- synchronous until short deadline.

Long enterprise process:
- create run;
- return run ID;
- continue asynchronously;
- notify/stream progress.

---

## 315. Principal tradeoff: dynamic tools

Dynamic discovery scales capability count but increases security/evaluation complexity.

Use policy-aware progressive disclosure.

---

## 316. Principal tradeoff: automatic actions

Automation value increases with automatic actions, but so does risk.

Use risk tiers:
- auto read;
- bounded auto write;
- approval;
- deny.

---

## 317. why Foundry Hosted Agents?

Because the organization can retain custom code/orchestration while delegating runtime lifecycle, identity, sessions, scale and Foundry integration to the platform.

---

## 318. why Toolbox?

It creates a managed, reusable, versioned capability plane exposed through MCP rather than hard-wiring every agent to every enterprise integration.

---

## 319. why LangGraph?

For explicit stateful graphs, checkpointing, conditional routing and graph composition.

Use it when those semantics improve correctness—not merely because it is popular.

---

## 320. why Agent Framework?

It provides Microsoft-native agent/workflow/tool abstractions and integrates naturally with Foundry's agent ecosystem.

---

## 321. why seven memories?

Because working state, conversation, historical episodes, facts, procedures, entities and audit have materially different retrieval, retention and trust semantics.

---

## 322. hardest problem

The hardest problem is preserving correctness across:

```text
user intent
 -> plan
 -> delegated agent
 -> tool selection
 -> authorization
 -> side effect
 -> evidence
 -> memory
```

while retries, replanning, failures and concurrent work occur.

---

## 323. how do you prevent duplicate writes?

Use:
- idempotency key;
- durable task state;
- provider idempotency;
- unknown-outcome state;
- reconciliation;
- fencing.

---

## 324. how do you secure RAG?

ACL filtering occurs before retrieval, content has provenance/classification, retrieved text remains untrusted, and privileged actions still pass independent authorization.

---

## 325. how do you evaluate multi-agent systems?

Evaluate each layer:
- planner;
- specialist;
- tool selection;
- retrieval;
- security;
- verifier;
- end-to-end business outcome.

One aggregate "answer quality" score is insufficient.

---

## 326. how do you scale?

Regional stateless front ends + durable scheduler/queue + specialized worker pools + managed Toolbox/Search/model services + tenant-aware rate limits + cell architecture.

---

## 327. how do you handle model nondeterminism?

Constrain model outputs with typed schemas and deterministic validation, persist versions/evidence, evaluate regressions, and keep security/state transitions outside the model.

---

## 328. what is production readiness?

Not "the agent answered a demo."

Production readiness means:
- recoverable state;
- correct side effects;
- identity/policy;
- tenant isolation;
- evidence;
- evaluation;
- observability;
- rollback;
- incident response;
- capacity;
- DR.

---

## 329. Recommended enterprise repository evolution

```text
enterprise-agent/
├── api/
├── domain/
│   ├── plans/
│   ├── tasks/
│   └── evidence/
├── agents/
├── orchestration/
│   ├── langgraph/
│   └── agent_framework/
├── tools/
│   ├── toolbox/
│   ├── mcp/
│   └── gateway/
├── security/
├── approvals/
├── rag/
├── memory/
├── persistence/
├── scheduler/
├── workers/
├── sandbox/
├── telemetry/
├── evaluation/
├── migrations/
├── deploy/
├── tests/
└── docs/
```

---

## 330. Production implementation sequence

1. Deploy local reference.
2. Connect real Foundry model.
3. Connect real Toolbox.
4. Add structured-output planner.
5. Add Azure AI Search.
6. Add PostgreSQL/Alembic.
7. Add durable LangGraph/checkpoint state.
8. Add queue/workers.
9. Integrate Permission Firewall.
10. Add exact approvals.
11. Add enterprise memory backends.
12. Add OTel/evaluation.
13. Add sandbox.
14. Add regional deployment/DR.

---

## 331. Complete production checklist

### Foundry
- [ ] project created
- [ ] model deployed
- [ ] Hosted Agent identity
- [ ] Toolbox created
- [ ] Toolbox version pinned
- [ ] RBAC verified

### Orchestration
- [ ] typed planner
- [ ] DAG validator
- [ ] durable plan versions
- [ ] durable scheduler
- [ ] bounded parallelism
- [ ] cancellation
- [ ] replanning audit

### Tools
- [ ] governed catalog
- [ ] MCP negotiation
- [ ] tool versioning
- [ ] deadlines
- [ ] error taxonomy
- [ ] idempotency
- [ ] reconciliation

### Security
- [ ] Entra identity
- [ ] user/delegated authority
- [ ] permission firewall
- [ ] approval
- [ ] DLP
- [ ] information-flow labels
- [ ] credential broker
- [ ] egress controls
- [ ] sandbox

### RAG
- [ ] tenant/ACL filter
- [ ] hybrid retrieval
- [ ] provenance
- [ ] freshness
- [ ] poisoning response

### Memory
- [ ] seven explicit semantics
- [ ] retention
- [ ] provenance
- [ ] contradiction handling
- [ ] privacy/delete
- [ ] audit separation

### Reliability
- [ ] durable DB
- [ ] leases/fencing
- [ ] durable timers
- [ ] outbox
- [ ] retry policy
- [ ] unknown outcome
- [ ] compensation
- [ ] DR

### Observability
- [ ] OTel
- [ ] dashboards
- [ ] alerts
- [ ] cost
- [ ] evaluation
- [ ] audit/SIEM

### Delivery
- [ ] unit/property tests
- [ ] integration tests
- [ ] security tests
- [ ] agent evaluation
- [ ] load tests
- [ ] chaos tests
- [ ] SBOM/scanning/signing
- [ ] canary
- [ ] rollback

---

## 332. Final architecture principle

A production enterprise agent is not merely:

```text
LLM + tools
```

It is:

```text
managed identity
+ bounded probabilistic planning
+ typed durable orchestration
+ specialist agents
+ governed versioned capabilities
+ least-privilege authority
+ evidence/provenance
+ verification
+ explicit memory semantics
+ recoverable state
+ observability/evaluation
+ operational lifecycle
```

Foundry Hosted Agents and Toolbox are most valuable when used as managed platform primitives inside that larger correctness and governance architecture.
