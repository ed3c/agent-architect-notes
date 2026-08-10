# Agent Architect Capstone

Recommended positioning:

> An evaluation, security, and execution platform for production-grade AI agent skills.

This should grow from the existing SKILL.md / MCP / Skill Arena direction rather than becoming a generic RAG chatbot.

## Core Modules

### 1. Skill Registry

- SKILL.md validation
- Semantic versioning
- Capability metadata
- Required permissions
- Tool contracts
- Compatibility matrix

### 2. Execution Harness

- Isolated workspace
- Docker / MicroVM sandbox
- Timeouts
- Resource limits
- Network egress policy
- Secrets injection
- Deterministic replay

### 3. Agent Runtime

- State machine
- Checkpoints
- Resume
- Max iterations
- HITL
- Model routing
- Retry / fallback
- Budget control

### 4. Eval Platform

- Task Success Rate
- State Assertion Pass Rate
- Tool Selection Accuracy
- Tool Argument Precision
- Schema Compliance Rate
- Trajectory Efficiency
- Human Escalation Rate
- p50 / p95 latency
- Cost per task
- Security attack success rate

### 5. Observability

- OpenTelemetry
- Trace ID across Agent / Tool / Model calls
- Token and cost attribution
- Retrieval evidence
- Failure taxonomy
- Replayable trajectories

### 6. Security

- Prompt Injection test corpus
- Least-privilege tool tokens
- RBAC
- Approval gates
- Audit log
- Provenance
- Egress filtering
- Data boundary enforcement

## Portfolio Evidence

Minimum evidence package:

- Architecture diagram
- Three ADRs
- Threat model
- Eval report
- Real failure postmortem
- 8-12 minute English demo
- Reproducible benchmark
- CI agent regression tests

## Design Question Every Agent Architect Must Answer

Why should this be an agent rather than a deterministic workflow?

If the answer is weak, reduce autonomy and use a deterministic workflow plus human approval.
