# LAB-AA-01：Durable Agent State 與 Effect Boundary

> Issue: [#2](https://github.com/ed3c/agent-architect-notes/issues/2)
> Evidence stage: `executed-local`
> Runtime: Python `3.14.6`，只使用 standard library

## Objective

用最小 Event Reducer 與 Effect Boundary 重現 durable Agent 最容易被錯判的 recovery semantics：

1. duplicate event delivery 不得重複改變 logical state；
2. external effect 成功、completion record 尚未寫入就 crash 時，resume 必須重用 stable `idempotency_key`；
3. validated snapshot + tail replay 必須與 full replay 得到相同 state；
4. corrupt、missing、unknown-schema 或來自另一條 event stream 的 snapshot 必須退回 full replay；
5. iteration / budget limit 必須先留下 terminal event，才拒絕下一步。

這個 Lab 證明的是 bounded contract，不是 production framework，也不宣稱 arbitrary external API 具備 exactly-once guarantee。

## Public Seams

- `replay(events) -> ReplayResult`：pure logical reducer；以 `event_id` 去重。
- `create_snapshot(events) -> Snapshot`：建立含 state checksum 與 event-prefix checksum 的 logical checkpoint。
- `replay_with_snapshot(events, snapshot) -> ReplayResult`：驗證 snapshot 後只 replay tail；不可信時 full replay。
- `DurableRunner` + `EffectPort`：先記錄 intent，再呼叫 external boundary；resume 使用相同 logical `effect_id` 當 idempotency key。
- `RunController`：把 max iterations / budget 與 terminal reason 保存到 event history。

Production code 不依賴 test double。測試中的 `RecordingIdempotentEffectPort` 只模擬 external provider 的 idempotency boundary，沒有 mock reducer internals。

## State Partition

| Partition | 本 Lab 表示法 | Authority / Limit |
| --- | --- | --- |
| Conversation / Context | 未保存 payload，只保留 state model 的擴充位置 | 真實系統需保存 versioned message/context event 或 content-addressed reference |
| Control State | `run_id`、iteration、budget、terminal state | append-only event history 是 canonical recovery input |
| Execution Environment | `SNAPSHOT_SCHEMA_VERSION` | 本 Lab 未保存 runtime image、dependency、model/tool manifest |
| External Side Effects | `effect_planned` / `effect_completed`、stable `effect_id` | external provider 才是 outcome authority；local log 無法單獨提供 exactly-once |

## Run

從 repository root 執行：

```bash
python3 -m unittest discover \
  -s exercises/production-labs/lab-01-durable-agent-state \
  -p 'test_*.py' -v
```

Expected: `9 tests`、exit code `0`。

## Failure Cases and Assertions

| Case | Executable assertion |
| --- | --- |
| Duplicate event delivery | 相同 `event_id` 只增加一次 iteration / cost |
| Crash after effect, before completion record | retry call count = 2；external application count = 1；pending effect 最終清空 |
| Replay vs snapshot | 同一 5-event workload：full replay work units = 5；snapshot + tail = 2；state 相同 |
| Corrupt snapshot | state checksum mismatch 時 full replay，work units 回到完整 event count |
| Missing snapshot | `None` 明確走 full replay |
| Schema change during resume | unknown snapshot schema 不做 silent coercion，走 full replay |
| Foreign snapshot | event-prefix checksum 不符時拒絕套用，避免跨 run silent corruption |
| Max iteration | 第三次 iteration 被拒；terminal reason = `max_iterations` |
| Max budget | 可能超支的 iteration 不寫入；terminal reason = `max_budget` |

## Retry and Rollback Boundary

- Retry：logical retry 重用 `effect_id`；若 provider 沒有 idempotency / query contract，outcome 是 ambiguous，不能把本 Lab 的 result 外推成 exactly-once。
- Rollback：event history 不做 delete 或 rewind。正確做法是 append compensating intent / result；refund、撤銷或 cleanup 都是新的 external effect。
- Snapshot fallback：只有 canonical history 完整時才能 full replay；history 已被 compact 且沒有 validated base 時應 fail closed。

## Deliberate Limits

- `InMemoryEventStore` 不跨 process durable；crash/restart 是重建 `DurableRunner`、保留 store 與 external provider state 的 deterministic simulation。
- Snapshot payload 只接受 JSON-serializable state。
- 沒有 database transaction、Transactional Outbox、lease/fencing、parallel worker、network timeout、secret rotation 或 Firecracker runtime。
- 測量使用 deterministic replay work units，不把微秒級 wall-clock 當可靠 benchmark。

## Evidence and Review

- Primary Source note：[Durable Agent State](../../../docs/kb/durable-agent-state.md)
- Decision：[ADR-0001](../../../docs/adr/adr-0001-durable-agent-recovery-hybrid.md)
- Execution receipt：[2026-08-11 Lab report](../../../docs/eval-reports/2026-08-11-durable-agent-state-lab.md)
- What-if：provider 已接受 effect、worker crash、schema 升級且 snapshot checksum mismatch；請不看筆記說出 resume order。
- Next review：完成本 Lab 後 24 小時內做第一次 active recall；7 天後重做 What-if。
