# Agent Architecture Index

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
