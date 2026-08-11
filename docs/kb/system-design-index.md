# System Design Index

## 45-60 Minute Answer Skeleton

1. Clarify the business objective.
2. Define functional and non-functional requirements.
3. Estimate scale and latency budget.
4. Define APIs and data contracts.
5. Draw the high-level architecture.
6. Deep-dive into one or two critical components.
7. Address failures, security, privacy, and isolation.
8. Define observability, evaluations, and cost controls.
9. Explain rollout, rollback, and future evolution.
10. State the major trade-offs.

## Tier 1: Common Foundations

- Rate Limiter
- Webhook Ingestion Service
- Distributed Task Queue
- Notification Service
- Audit Logging System
- Multi-tenant API Platform
- Search / Autocomplete Service
- Event Streaming Pipeline

## Tier 2: AI Engineer

- Enterprise RAG
- LLM Gateway
- Semantic Cache
- Embedding Pipeline
- Inference Serving Platform
- Continuous Evaluation Pipeline

## Tier 3: Agent Architect

- [Durable Agent Orchestrator](../../exercises/system-design/sd-01-durable-agent-orchestrator.md)
- Enterprise Action Agent
- Multi-Agent Code Review System
- Agent Tool Gateway
- Agent Memory Service
- Agent Eval Platform
- Sandboxed Code Execution Platform
- Human Approval and Resume Workflow

## Tier 4: FDE Case Studies

- Fleet Dispatching
- Factory IoT Sensor Analytics
- Dirty CSV/JSON Integration
- Legacy ERP Modernization
- Customer Support Automation
- On-prem / Air-gapped Agent Deployment

## Agent-Specific Questions

- Why an agent instead of deterministic workflow?
- Why single-agent or multi-agent?
- How does state persist?
- What terminates execution?
- What operations require HITL?
- How are tools authenticated and authorized?
- How do you detect loops?
- How do you evaluate trajectory quality?
- How do you cap token and monetary cost?
- What happens when the model is unavailable?
