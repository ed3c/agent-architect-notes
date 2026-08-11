# SD-AA-01：Design a Durable Agent Orchestrator

> Issue: [#2](https://github.com/ed3c/agent-architect-notes/issues/2)
> Target time: `50 minutes`
> Mode: System Design exercise；先作答，再查閱 source note 與 Lab

## 1. Business Objective

設計一個可執行長達數小時的 Agent orchestrator。它會讀取 conversation context、呼叫 Model 與 external tools，可能等待 human approval，且必須在 process / host crash 後安全 resume。

禁止用「serialize 整個 process」當完整答案。你必須界定 logical state、execution environment 與 external-system truth 的 authority。

## 2. Requirements

### Functional

- 建立、暫停、取消、resume 一個 Agent run。
- 保存 conversation/context、control state、execution manifest 與 effect evidence。
- 對 Model / Tool calls 設定 retry、timeout、budget、max iterations 與 approval gate。
- 支援 logical checkpoint；可選擇 execution-environment snapshot。
- 在 schema / code version 改變時，做 compatibility decision。
- 對 external effect 提供 idempotency、reconciliation 與 compensation path。

### Non-functional

- Single-region 起步；99.9% control-plane availability。
- 同一 run 不得有兩個合法 effect-dispatch owner。
- Recovery 不得 silent skip committed history，也不得 silent repeat high-risk effect。
- Audit evidence 不保存 secrets 或完整敏感 payload。
- Canonical history 可用時，corrupt/missing snapshot 不得阻止 recovery。

## 3. Workload and Budget

假設：

- 100,000 active runs；peak 2,000 state transitions / second。
- 每個 run median 80 events、P99 20,000 events。
- Model response P95 20 seconds；Tool response P95 5 seconds。
- Logical resume P95 3 seconds；若採 environment snapshot，restore P95 另列預算。
- 每個 run 有 token / cost budget；超限不得再 dispatch 新 Model / Tool effect。

請先指出哪些數字會改變 storage partition、checkpoint policy 或 queue design；不要直接套固定架構。

## 4. Required APIs and Event Contract

至少定義：

- `POST /runs`
- `POST /runs/{run_id}/resume`
- `POST /runs/{run_id}/cancel`
- `POST /runs/{run_id}/approvals/{approval_id}`
- `GET /runs/{run_id}`

Event contract 至少含 `run_id`、sequence、`event_id`、event/schema/producer version、causation/correlation ID、payload reference、integrity hash。說明 ordering、deduplication 與 branch/reset identity。

## 5. Required Architecture

你的 diagram 與說明必須把以下元件分開：

1. API / Auth / Tenant boundary
2. Run coordinator + lease/fencing
3. Append-only Event Store
4. Deterministic Reducer / Replay Worker
5. Checkpoint Store + Compatibility Gate
6. Model / Tool Effect Dispatcher
7. Idempotency / Reconciliation / Transactional Outbox boundary
8. Approval Queue
9. Observability / Eval evidence
10. Optional Firecracker execution environment

## 6. State Partition Table

逐列填寫 canonical authority、persisted representation、resume rule、retention / privacy policy：

| Partition | Canonical authority | Persisted representation | Resume rule | Retention / privacy |
| --- | --- | --- | --- | --- |
| Conversation / Context |  |  |  |  |
| Control State |  |  |  |  |
| Execution Environment |  |  |  |  |
| External Side Effects |  |  |  |  |

## 7. Mandatory Failure Walkthroughs

對每個 case 寫出「last durable fact → detection → recovery action → invariant → evidence」：

1. external provider 已接受 effect，worker 在 completion record 前 crash；
2. queue duplicate delivery 同一 event；
3. resume 時 reducer / event schema 已升級；
4. latest snapshot corrupt；另一情況是 snapshot missing；
5. snapshot checksum 合法，但來自另一個 run / event prefix；
6. iteration 或 cost budget 已達上限；
7. 同一 run 的兩個 workers 發生 lease race；
8. compensation 本身失敗。

## 8. Replay / Snapshot Comparison

必須用同一 workload 比較：

| Strategy | Canonical recovery source | Recovery work | Compatibility risk | External-effect safety | Failure fallback |
| --- | --- | --- | --- | --- | --- |
| Full replay |  |  |  |  |  |
| Snapshot-only |  |  |  |  |  |
| Validated snapshot + tail replay |  |  |  |  |  |
| Firecracker-assisted hybrid |  |  |  |  |  |

至少提供一個 deterministic work metric（例如 applied events）；若提供 latency，需說明 hardware、sample size 與 variance。

## 9. Security, Privacy, Isolation

說明 tenant isolation、Tool credential re-acquisition、prompt/context injection boundary、approval lease、redaction、data retention、snapshot secret handling，以及 clone 同一 VM snapshot 時的 uniqueness risk。

## 10. Observability and Evals

至少定義：

- replay nondeterminism rate；
- snapshot validation/fallback count；
- unresolved / ambiguous effects；
- duplicate deliveries；
- resume latency 與 replay work units；
- budget / iteration terminations；
- compensation success rate；
- per-run trace lineage 與 evidence locator。

## 11. Rollout and Rollback

- 如何用 historical fixtures 驗證新 reducer？
- 如何 canary 新 schema / upcaster？
- 哪些狀況 pin old worker，哪些狀況 fail closed？
- Rollback 為何仍須通過新 history 的 compatibility test？
- External effect 為何只能 compensation，不能刪除 history 當作沒發生？

## 12. Evidence Contract

作答後執行 [LAB-AA-01](../production-labs/lab-01-durable-agent-state/README.md)，並引用：

- [Primary Source note](../../docs/kb/durable-agent-state.md)
- [ADR-0001](../../docs/adr/adr-0001-durable-agent-recovery-hybrid.md)
- [Execution report](../../docs/eval-reports/2026-08-11-durable-agent-state-lab.md)

不得把 source claim、local test result、production guarantee 混成同一 evidence level。

## 13. Review Gate

### What-if Pivot

> Provider 已接受 payment-like effect，但 worker crash；此時 deploy 新 reducer/schema，latest snapshot checksum mismatch，舊 idempotency window 又快到期。你的 resume order 是什麼？哪一步需要 human decision？

### Pass Assertions

- 四個 state partitions 的 authority 無混淆。
- 明說 local log 不足以提供 arbitrary external exactly-once。
- checkpoint/snapshot 被當成可驗證的 accelerator，而非唯一真相。
- 有 version gate、lease/fencing、idempotency retention 與 reconciliation。
- termination 在新 effect 前檢查並留下 durable reason。
- rollback 使用 compensation / new history，不改寫 canonical past。

第一次 review 在作答後 24 小時內；7 天後只看 What-if 重答。若漏掉任一 Pass Assertion，48 小時內做 targeted repair。
