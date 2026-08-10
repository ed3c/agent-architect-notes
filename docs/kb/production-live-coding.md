# Production Live Coding

This track separates Agent Architect candidates from pure LeetCode candidates.

## Required Lab Structure

Every lab must include:

```text
src/
tests/
README.md
pyproject.toml
```

Required qualities:

- Type hints
- Structured errors
- Unit tests
- Edge-case tests
- Complexity and trade-off notes
- Runnable local command

## Lab List

| ID | Lab | Core Ability |
| --- | --- | --- |
| LAB-01 | Defensive JSON Ingestion API | Pydantic, schema drift, DLQ, error handling |
| LAB-02 | Token Bucket Rate Limiter | Time, concurrency, bandwidth control |
| LAB-03 | Retry + Full Jitter + Circuit Breaker | Failure handling, backoff, recovery |
| LAB-04 | Async Bounded Worker Pool | asyncio, semaphore, cancellation |
| LAB-05 | DAG Workflow Executor | Topological Sort, dependency scheduling |
| LAB-06 | LRU + TTL Cache | Hash map, linked structure, expiration |
| LAB-07 | Idempotent Webhook Receiver | Deduplication, transaction boundary |
| LAB-08 | SSE Streaming Endpoint | Backpressure, disconnect, partial result |
| LAB-09 | Durable Agent State Machine | Checkpoint, resume, HITL |
| LAB-10 | Tool Execution Gateway | RBAC, validation, sandbox, audit |
| LAB-11 | Agent Eval Harness | Assertions, graders, regression testing |
| LAB-12 | Distributed Trace Propagation | Trace ID, spans, latency, failure lineage |

## 60-Minute Live Coding Gate

A passing version should:

1. Clarify contract.
2. Build runnable baseline.
3. Add tests.
4. Handle the main failure mode.
5. Explain trade-offs.
6. Leave improvement TODOs without hiding incomplete work.
