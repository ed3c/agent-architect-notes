# 2026-08-11 — Durable Agent State Lab Execution Receipt

> Exercise ID: `LAB-AA-01`
> Issue: [#2](https://github.com/ed3c/agent-architect-notes/issues/2)
> Evidence level: `LOCAL_OBSERVATION / executed-local`
> Runtime: Python `3.14.6`

## Trigger and Contract

驗證 minimal Event Reducer / Effect Boundary 是否能以 executable assertions 覆蓋：duplicate delivery、effect-completion crash window、snapshot/full replay comparison、snapshot fallback、schema gate、foreign snapshot、iteration/budget termination。

Public seams 與限制見 [LAB-AA-01](../../exercises/production-labs/lab-01-durable-agent-state/README.md)。

## TDD Receipt

| Increment | RED evidence | GREEN commit |
| --- | --- | --- |
| Deterministic replay / event dedup | `ModuleNotFoundError: durable_agent` | `2349603` |
| Crash after effect, before completion record | `ImportError: DurableRunner` | `2d1154f` |
| Snapshot + tail / corrupt / missing / schema fallback | missing API、wrong corrupt state、`NoneType` error、wrong work count | `ced2d28` |
| Iteration / budget terminal state | missing API；overspend 未 raise | `659add2` |
| Snapshot source-stream binding | foreign snapshot 產生錯誤 run/state | `16c786d` |

每個 increment 都先出現預期 failure，再加最小 implementation 並重跑完整 suite；沒有使用 `--no-verify` 或停用測試。

## Final Command

```bash
python3 -m unittest discover \
  -s exercises/production-labs/lab-01-durable-agent-state \
  -p 'test_*.py' -v
```

Result：exit code `0`；`Ran 9 tests`；`OK`。

## Assertion Results

| Assertion | Result | Observable evidence |
| --- | --- | --- |
| Duplicate event delivery | PASS | 3 delivered records 中 duplicate `event_id` 只套用一次；applied events = 2 |
| Crash after effect before completion | PASS（bounded） | resume 後 boundary calls = 2、external applications = 1、pending effects = 0 |
| Snapshot + tail equals full replay | PASS | 同一 5-event workload state 相同；work units 5 → 2 |
| Corrupt snapshot fallback | PASS | checksum mismatch 後 full replay；applied events = 3 |
| Missing snapshot fallback | PASS | `None` 後 full replay；applied events = 2 |
| Unknown snapshot schema | PASS（bounded） | schema `2` 對 reader `1` 會 full replay；未執行 reducer migration |
| Foreign snapshot | PASS | event-prefix checksum mismatch 後 full replay；避免跨 run silent state corruption |
| Max iterations | PASS | 第三次 iteration 被拒；terminal reason durable = `max_iterations` |
| Max budget | PASS | overspend iteration 未寫入；terminal reason durable = `max_budget` |

Compilation check：

```bash
python3 -m compileall -q \
  exercises/production-labs/lab-01-durable-agent-state
```

Result：exit code `0`。

## Evidence Interpretation

- `[LOCAL_OBSERVATION]` Replay work 使用 deterministic reducer application count，不是 wall-clock benchmark。
- `[LOCAL_OBSERVATION]` Crash/restart 是重建 runner、保留 in-memory event store 與 idempotent provider state 的 simulation。
- `[INFERENCE]` Stable idempotency key 可在 provider contract 有效的範圍內消除 duplicate accepted outcome；它不是任意 external API 的 exactly-once 證明。
- `[UNKNOWN]` Persistent database atomicity、Transactional Outbox、lease fencing、real provider retention、process/host restart、Firecracker restore、production latency/cost。

## First Divergence and Repair

Initial snapshot design 只驗證 state checksum。反例顯示：另一條 event stream 的 snapshot 可以 checksum 合法，卻把 `run-1` state 套到 `run-2`。修正後 snapshot 另含 event-prefix checksum；foreign snapshot 會 fail closed 回 full replay。

這是本 Lab 最重要的額外發現：artifact integrity 不等於 artifact provenance。

## Known Limits

- `InMemoryEventStore` 不跨 process durable。
- Test double 明確具備 idempotency；沒有模擬 provider key expiry 或不支援 query 的情況。
- Snapshot state 限 JSON-serializable payload。
- 沒有 parallel dispatch、lease race、partial database transaction 或 compensation failure test。
- Local assertions 不能外推為 production guarantee。

## Next Action and Review

- Production promotion 前：換 persistent store，加入 atomic append / Outbox、lease fencing、historical reducer fixtures、provider-specific reconciliation 與 load benchmark。
- `2026-08-12`：不看 note，重建四種 state authority 與 resume order。
- `2026-08-18`：回答 [SD-AA-01 What-if Pivot](../../exercises/system-design/sd-01-durable-agent-orchestrator.md#13-review-gate)；漏掉 version gate、idempotency retention、single-run lease 或 Firecracker external resources 任一項，48 小時內 targeted repair。
