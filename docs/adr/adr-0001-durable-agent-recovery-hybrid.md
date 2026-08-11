# ADR-0001：Durable Agent 採 Validated Snapshot + Tail Replay

Date: `2026-08-11`
Status: `Accepted — learning-unit scope`
Issue: [#2](https://github.com/ed3c/agent-architect-notes/issues/2)

## Context

Durable Agent 必須在 crash/restart 後重建 logical state，同時避免重複不可逆的 external effect。候選方案有 full event replay、snapshot-only，以及 snapshot + tail replay；execution environment 還可另加 Firecracker snapshot。

這些方案不能只比 recovery speed：還要比較 canonical authority、determinism、version compatibility、corrupt fallback、external effect ambiguity 與 rollback semantics。

## Decision

本 learning unit 採用：

1. append-only logical event history 作 canonical recovery source；
2. deterministic reducer 由 ordered history 重建 control state；
3. logical snapshot 只作 accelerator，必須驗證 state checksum、event-prefix checksum 與 schema version；
4. snapshot missing、corrupt、foreign 或 incompatible 時，只要 canonical history 完整就 full replay；
5. Model / Tool call 隔離到 Effect Boundary，先寫 intent，logical retry 重用 stable idempotency key；
6. external outcome ambiguous 時先 query/reconcile，不把 local event log 誤稱為 exactly-once；
7. iteration / budget / cancellation 在 dispatch 新 effect 前檢查，terminal reason 寫入 history；
8. rollback 採 append-only compensation；不刪除或倒轉已提交 history；
9. Firecracker snapshot 僅可作 compatible execution environment 的額外 accelerator，restore 後仍要過 manifest、credential、lease 與 effect-reconciliation gate。

Production adoption 仍需 persistent Event Store、transaction / Outbox、lease fencing、historical replay fixtures、load benchmark、security review 與 provider-specific idempotency qualification；本 ADR 不把 local Lab 外推為 production readiness。

## Alternatives Considered

| Alternative | Canonical source | Same-workload local evidence | Strength | Rejected / bounded because |
| --- | --- | --- | --- | --- |
| Full replay | Full event history | 5 events → 5 reducer applications | 最簡單；audit path 完整；沒有 snapshot trust problem | Long history recovery cost 線性增加；仍不解決 external effect ambiguity |
| Snapshot-only | Snapshot blob | 未作為合法 fallback 執行 | Recovery work 最少 | Snapshot corrupt/missing/foreign/schema mismatch 時沒有可信重建路徑；不可取代 external truth |
| Validated snapshot + tail replay | History；snapshot 是 cache | 3-event snapshot + 2-event tail → 2 applications；state 與 5-event full replay相同 | 保留 auditability，同時降低 replay work；可 fail closed / fallback | 需要 checksum、history binding、schema/version gate 與 canonical history retention |
| Firecracker-assisted hybrid | Logical history + environment manifest；VM snapshot 是 cache | 未執行，本地 evidence = `unknown` | 可能降低 runtime cold start | VM snapshot 不含完整 disk/host/network/external truth；有 compatibility、secret、uniqueness 與 artifact-size風險 |

## Consequences

### Positive

- Recovery correctness 可由 deterministic event assertions 驗證，不依賴 process memory。
- Replay work 有可比較的 deterministic metric。
- corrupt / missing snapshot 不會 silent poison state。
- foreign snapshot 會因 event-prefix mismatch 被拒絕。
- crash ambiguity 被迫在 Effect Boundary 處理，不會被「exactly-once」口號掩蓋。
- Terminal state、retry identity 與 compensation 都留下 audit trail。

### Negative

- Event/schema evolution、historical replay test 與 snapshot lifecycle 增加運維成本。
- Full history retention 或 validated compaction base 成為 recovery 前提。
- Provider idempotency 有 retention 與 semantic limits；有些 effects 只能 manual reconcile。
- Snapshot validation失敗時 recovery latency 會退化為 full replay。
- Environment snapshot 是另一套 artifact / compatibility / security lifecycle。

## Evidence

- Primary Source qualification：[Durable Agent State](../kb/durable-agent-state.md)
- Runnable Lab：[LAB-AA-01](../../exercises/production-labs/lab-01-durable-agent-state/README.md)
- Executed tests：[2026-08-11 Lab report](../eval-reports/2026-08-11-durable-agent-state-lab.md)
- System Design exercise：[SD-AA-01](../../exercises/system-design/sd-01-durable-agent-orchestrator.md)

Local evidence scope：Python `3.14.6`、in-memory deterministic simulation、9 tests。它驗證 reducer / Effect Boundary contract，不驗證 durable database、distributed lease、real provider 或 Firecracker latency。

## Review Date

- `2026-08-12`：第一次 active recall，重建 authority / resume order。
- `2026-08-18`：用 What-if Pivot 重答。
- 最遲 `2026-11-11`，或 pinned dependency major/version semantics 改變時，重新 qualify Primary Sources 與本 ADR。

## What-if Review Rule

若 production benchmark 顯示 full replay 已滿足 P99 resume budget，仍保留同一 canonical design，但可延後 snapshot 複雜度；若 canonical history 不能完整保留，則必須先設計可驗證 compaction/base snapshot 與 backup restore，不能把 snapshot-only 降級成 silent default。
