# Agent Architecture Index

## Qualified Learning Units

- [Durable Agent State：Replay、Checkpoint、Snapshot 與 Effect Boundary](durable-agent-state.md)
- [SD-AA-01：Design a Durable Agent Orchestrator](../../exercises/system-design/sd-01-durable-agent-orchestrator.md)
- [LAB-AA-01：Durable Agent State 與 Effect Boundary](../../exercises/production-labs/lab-01-durable-agent-state/README.md)
- [ADR-0001：Validated Snapshot + Tail Replay](../adr/adr-0001-durable-agent-recovery-hybrid.md)
- [Zero-trust Agent Sandbox：Isolation、Egress 與 Cleanup](zero-trust-agent-sandbox.md)
- [SD-AA-02：Zero-trust Agent Code Execution](../../exercises/system-design/sd-02-zero-trust-agent-code-sandbox.md)
- [LAB-AA-02：Zero-trust Agent Code Sandbox](../../exercises/production-labs/lab-02-zero-trust-sandbox/README.md)

## Core Concepts

- Agent Control Loop
- State
- Memory
- Termination
- Tool Contract
- Tool Gateway
- Human-in-the-loop
- Checkpoint / Resume
- Model routing
- Retry / fallback
- Budget control
- Trajectory replay

## Identity and Permissioning

Agent work requires identity design, not only tool calling:

- OAuth 2.0
- OIDC
- PKCE
- Token exchange
- Consent
- Delegated authorization
- Service accounts
- Secret rotation
- Per-user tool identity
- Fine-grained scopes

## Reliability Risks

- Infinite loop
- Tool argument drift
- Hidden state corruption
- Retry storm
- Budget overrun
- Model outage
- Unsafe action
- Missing audit trace
- Retrieval without permission boundary

## Agent Design Gate

Before implementing autonomy, answer:

1. What exact task success metric improves?
2. Which step needs model judgment?
3. Which steps must stay deterministic?
4. What is the termination condition?
5. What is the rollback path?
6. What requires human approval?
7. Which evidence proves reliability?
