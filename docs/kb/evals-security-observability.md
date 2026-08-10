# Evals, Security, Observability

## Evaluation Science

Do not reduce evaluation to LLM-as-a-Judge.

Required topics:

- Dataset construction
- Label quality
- Inter-rater agreement
- Deterministic assertions
- Pairwise evaluation
- Judge bias
- Leakage
- Statistical confidence
- Regression thresholds
- Offline vs online metrics

## Agent Metrics

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

## Security Controls

- Prompt Injection test corpus
- Least-privilege tool tokens
- RBAC
- Approval gates
- Audit log
- Provenance
- Egress filtering
- Data boundary enforcement
- Sandboxed execution
- Brokered and audited data access

## Observability Requirements

Every significant run should be replayable:

- Trace ID across Agent / Tool / Model calls
- Tool call inputs and outputs
- State transitions
- Prompt/retrieval evidence
- Latency and cost
- Failure taxonomy
- Human intervention events

## Postmortem Rule

A failure becomes learning evidence only after it records:

- Impact
- Timeline
- Root cause
- First divergence
- Broken invariant
- Repair action
- Regression test
