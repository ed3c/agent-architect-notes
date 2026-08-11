# Durable Agent State：Replay、Checkpoint、Snapshot 與 Effect Boundary

> Issue: [#2 — Durable Agent state, replay, snapshot, and resume](https://github.com/ed3c/agent-architect-notes/issues/2)
> Retrieval Date: `2026-08-11`
> Evidence Stage: `source-qualified; lab-executed-local`
> Scope: 長時間執行、可 crash/restart、可 retry 且會呼叫 external tools 的 Agent orchestrator

## 1. Claim 標記

- `[SOURCE]`：Primary Source 明示的事實；同一 Claim 旁附 Citation。
- `[INFERENCE]`：由一個或多個來源推導，但來源沒有逐字保證此結論。
- `[HYPOTHESIS]`：需要 Lab／Benchmark 驗證的預測。
- `[DECISION]`：本 learning unit 採用的 Design Contract；不是外部產品的通用保證。
- `[LOCAL_OBSERVATION]`：本 Repository 或本次研究實際觀察到的狀態。

## 2. Executive Model

- `[SOURCE]` Temporal 的 canonical architecture 以 Event Sourcing 運作：每個 Workflow Execution 保存 append-only Event History，並可由 replay 重建所需 Workflow state；Workflow code 必須 deterministic 且不可直接做 side effects，Activity 則必須 idempotent 或 non-retryable。[T1]
- `[INFERENCE]` 對 durable Agent 而言，正確的核心不是「把 Python object dump 下來」，而是把可重播的 logical decisions 與不可重播的 external effects 分開。
- `[DECISION]` Canonical recovery source 是 validated append-only logical history；checkpoint 是有 history position 的重建加速器；execution-environment snapshot 是另一層 optimization，不得冒充 external-system truth。
- `[SOURCE]` Kafka 4.2 的官方 Design 文件明確把 exactly-once 限定在可協調的 transaction boundary；寫往其他 destination system 通常需要該系統合作。[K1]
- `[INFERENCE]` 因此 local event log 單獨不能保證 external side effect exactly-once：它最多證明本地「打算做」或「已記錄完成」，不能消除 remote commit 與 local acknowledgement 之間的 ambiguous window。

## 3. State Partition

| Partition | Canonical State | Persisted Shape | Resume Rule | 不可混淆的邊界 |
| --- | --- | --- | --- | --- |
| `[DECISION]` Conversation / Context | 使用者輸入、Agent 回覆、approved context references、redaction metadata | append-only message/context events；大型 payload 用 content-addressed reference | 依 sequence 重建；缺少 required payload 時 fail closed | Retrieval cache 不是 canonical knowledge；prompt text 不可取得更高 instruction authority |
| `[DECISION]` Control State | cursor、step、pending approvals、iteration/budget counters、termination status、retry schedule | deterministic events + reducer state | replay 到最後 validated event；只執行尚未 terminal 的 transition | wall clock、randomness、model output 不得在 replay 時偷偷重取 |
| `[DECISION]` Execution Environment | code/schema/reducer version、runtime image、dependency/model/tool manifest、optional VM snapshot reference | immutable manifest + optional snapshot artifacts + hashes | 先做 Compatibility Gate；不相容就不用 snapshot，改走 supported replay/migration path | VM snapshot 不包含所有 host resources、remote services 或 business facts |
| `[DECISION]` External Side Effects | remote system 才是 effect outcome 的 authority | local effect intent/result reference、operation ID、idempotency key、outbox status | 先 reconcile remote truth，再決定 retry；同一 logical effect 不換 key | local `effect_completed` event 不是 remote transaction 的替代品 |

- `[SOURCE]` LangGraph 官方 Persistence 文件把 checkpointer 定義為 thread-scoped graph-state snapshot，Store 則是 cross-thread application-defined state；兩者用途和 authority 不同。[L1]
- `[INFERENCE]` Conversation state、control state 與 cross-thread memory 若共用一個無 schema 的 blob，會讓 retention、privacy、migration 與 rollback boundary 同時失去可判性。

## 4. Append-only History 與 Deterministic Replay

### 4.1 Minimal Event Contract

- `[DECISION]` 每個 logical event 至少包含：`run_id`、monotonic `sequence`、`event_id`、`event_type`、`schema_version`、`producer_version`、`causation_id`、`correlation_id`、payload reference、integrity hash 與 committed timestamp。
- `[DECISION]` Reducer 介面固定為 `state[n+1] = reduce(state[n], event[n+1])`，且對同一 ordered history 必須產生相同 logical state。
- `[DECISION]` 修正採用 superseding 或 compensating event；不得 silent edit/delete 已提交 history。
- `[SOURCE]` Temporal History Service 文件說明 Workflow History 通常是 linear sequence；Reset 或 conflict resolution 時可能形成 branching topology，且 History Events 足以恢復 relevant Mutable State 與 tasks。[T2]
- `[INFERENCE]` 「append-only」不等於「永遠只有一條 branch」；若產品支援 fork/reset，branch identity 與 selected head 必須成為顯式 state。

### 4.2 Replay Determinism

- `[SOURCE]` Temporal Python SDK 禁止 Workflow code 使用 non-deterministic operations，例如 unordered `set` iteration、threading、randomness、network I/O、subprocess、disk I/O 與 global-state mutation。[T3]
- `[SOURCE]` 同一 SDK 的 Replayer 可把 exported Workflow History 餵給現行 Workflow code；偵測到 nondeterminism 時會丟出 error，官方建議用 past histories 檢查 code change 的 compatibility。[T3]
- `[DECISION]` 所有 replay-sensitive inputs 必須滿足其一：寫入 history、由 deterministic primitive 產生，或隔離到有 recorded result 的 effect/task boundary。
- `[DECISION]` Replay mode 禁止重新呼叫 Model、Tool、clock、random generator 或 network；它只 consume recorded result。
- `[DECISION]` CI 必須用 representative historical fixtures 跑 replay compatibility，不能只測 fresh run。

### 4.3 Code 與 Schema Versioning

- `[SOURCE]` Temporal Python SDK 的 `patched(id)` 在 fresh execution 或 history 已見該 patch 時走 new path，否則 replay 走 old path；只有確定舊路徑不再被歷史執行查詢後，才可 `deprecate_patch(id)`。[T4]
- `[INFERENCE]` 直接用最新 reducer 重播所有舊 events 並不天然安全；command order、branch condition、default value 或 serialization 的變更都可能造成 nondeterminism 或 semantic drift。
- `[DECISION]` 每次 resume 先比對 `event_schema_version`、`reducer_version`、`workflow_code_version` 與 `environment_manifest_version`。
- `[DECISION]` 不相容時只能選擇明示路徑：pinned old worker、tested upcaster/migrator、version marker/patch，或 stop with diagnostic；禁止 silently coerce。
- `[DECISION]` Migration 產生新的 versioned artifact 或 migration event，保留原 history 與 source hash。

## 5. Checkpoint / Snapshot Contract

### 5.1 Logical Checkpoint

- `[SOURCE]` LangGraph 的 checkpointer 保存單一 thread 的 graph state，支援 continuity、human-in-the-loop、time travel 與 fault tolerance；`InMemorySaver` 在 process restart 後會遺失，Production 應使用 persistent saver。[L1]
- `[DECISION]` Logical checkpoint 至少封裝：`run_id`、`history_sequence`、`history_hash`、reduced state、schema/reducer versions、created time、payload hash 與 completeness marker。
- `[DECISION]` 只有在 state bytes、metadata、hash 全部 durable 後，才 atomic publish checkpoint pointer；partial write 不得成為 latest。
- `[DECISION]` Checkpoint 是 cache，不是新 authority。接受它之前必須驗證 checksum、history prefix hash、version compatibility 與 required payload availability。

### 5.2 Corrupt / Absent Fallback

- `[SOURCE]` Axon Framework 5.1 明確把 snapshot 定義為 performance optimization，而非 events 的替代品；snapshot 不存在、version 不符、payload 無法轉換或已 corrupt 時，Framework 會忽略它並 full replay Event Stream，之後可依 policy 產生新 snapshot。[A1]
- `[SOURCE]` Firecracker state snapshot format 可包含 CRC64，但 CRC 是 optional；memory file 被 external modification 會 corrupt guest memory 並導致 undefined behavior，load failure 會回報 specific error 並終止可能已 invalid 的 Firecracker process。[F2][F1]
- `[INFERENCE]` Snapshot format 自帶 version/checksum 並不等於整個 Agent recovery set 完整；history、memory、disk、environment manifest 與 remote effects 仍需 application-level manifest 綁定。
- `[DECISION]` `checkpoint absent`：由 genesis 或最早 retained canonical history 開始 replay；若 history 已被 compact 且沒有可驗證 base，狀態為 `blocked`，不可猜測。
- `[DECISION]` `checkpoint corrupt`：quarantine 該 artifact、記錄 diagnostic evidence、嘗試較舊的 validated checkpoint，再 replay remaining history。
- `[DECISION]` 所有 checkpoint 都無效：完整 history 尚在則 full replay；history 不完整則 fail closed 並要求 restore canonical backup。
- `[DECISION]` Fallback 絕不自動重送 unresolved external effect；先進入 Effect Reconciliation。

### 5.3 Firecracker Execution-environment Boundary

- `[SOURCE]` Firecracker snapshot 序列化 guest memory 與 emulated hardware/VMM state；attached block-device contents 不屬於 state snapshot，disk files、TAP devices 與 vsock resources 必須由使用者另行管理並在 restore host 可取得。[F1][F2]
- `[SOURCE]` Firecracker snapshot format 與 Firecracker version 分離，load 會檢查 format compatibility；跨 CPU architecture/model 不相容，跨 host kernel restore 也可能不穩定。[F2]
- `[SOURCE]` Snapshot restore 不保證 network connection state；vsock connections 會 reset，metrics/log configuration 與部分 data store 也不在 snapshot 內。[F1]
- `[SOURCE]` 從同一 snapshot 恢復多個 execution copies 可能重複 identifiers、random values 或 cryptographic tokens；Firecracker 明確視缺少 uniqueness mechanism 的重複恢復為 insecure。[F1]
- `[INFERENCE]` Firecracker snapshot 的正確用途是加速 compatible execution environment 的 resume，不是替代 logical event history、Tool idempotency、network reconciliation 或 authorization refresh。
- `[DECISION]` Environment snapshot manifest 必須另列 Firecracker binary/snapshot format、CPU template、kernel、rootfs/block hashes、network/vsock recreation steps、secret re-injection policy 與 single-consumer lease。
- `[DECISION]` Restore 完成仍先停在 `Paused/Reconcile` gate；重新取得短效 credentials、更新 clock、確認 lease 與 unresolved effects 後才能繼續執行。

## 6. External Effect Boundary

### 6.1 為何 Local Log 不等於 Exactly-once

- `[SOURCE]` Kafka 4.2 只對 Kafka topic 內的 read/process/write 提供其 exactly-once primitives；輸出到 other destination systems 通常需要 destination cooperation，常見解法是讓 output 與 consumer position 共用 transaction boundary 或讓 destination 支援 deduplication。[K1]
- `[SOURCE]` Temporal architecture 要求可能 retry 的 Activity idempotent；否則應採 non-retryable，分別對應 at-least-once 或 at-most-once trade-off。[T1]
- `[SOURCE]` Temporal 官方 Error Handling 文件直接描述 ambiguity window：Worker 可能已完成 Activity，卻在向 Temporal Service 回報前 crash；因 Service 沒有 completion record，Activity 會 retry。官方建議以 Workflow Run ID 加 Activity ID 作為跨 retry 穩定的 idempotency key。[T5]
- `[INFERENCE]` Crash 發生在 remote commit 成功之後、local completion record 之前時，recovery 只讀 local log 無法判定 effect「未發生」或「已發生但 acknowledgement 遺失」。這是 distributed commit ambiguity，不是多寫一筆 local event 就能消除。
- `[DECISION]` 文件與 API 不使用無限定的 `exactly-once`；應寫成「在指定 idempotency retention／transaction／dedup boundary 內，logical effect 至多產生一個 accepted outcome」。

### 6.2 Idempotency Key Contract

- `[SOURCE]` Stripe API 用 client-generated `Idempotency-Key` 辨識 retry；相同 key 會重用第一次已開始執行的結果，並檢查 parameters 是否一致。Stripe 也明示 key 可在至少 24 小時後被移除，之後重用會視為新 request。[S1]
- `[DECISION]` Key 由 stable logical identity 派生：`tenant/run/effect-kind/logical-operation-id`；retry attempt number 不進入 key。
- `[DECISION]` 同 key 必須對應 canonicalized identical request；payload 不同即 hard error，不得偷偷換 key 繞過。
- `[DECISION]` Persist `effect_intent` 後才 dispatch；結果保存 remote request/operation ID、response digest 與 reconciliation locator，避免保存 secret 或完整敏感 payload。
- `[INFERENCE]` Idempotency guarantee 有 retention 與 provider-specific semantics；resume 若超出 window，必須先 query/reconcile，不可假設 key 永久有效。

### 6.3 Transactional Outbox Boundary

- `[SOURCE]` Debezium Outbox Event Router 的目的，是避免 service internal database state 與下游 consumed events 不一致；outbox row 的 unique event ID 可供 consumer 去除 duplicates。[D1]
- `[DECISION]` 當 Agent 必須同時提交本地 business state 與發佈 downstream event 時，兩者寫入同一 database transaction；CDC/outbox publisher 在 transaction 之外重試 delivery。
- `[INFERENCE]` Outbox 解決 database commit 與 message publication 的 dual-write gap，但 downstream consumer 仍需用 event ID 去重；它不把任意 third-party API 納入同一 atomic transaction。

### 6.4 Effect State Machine

| State/Event | Contract |
| --- | --- |
| `[DECISION] effect_intent_recorded` | 已持久化 stable operation ID、canonical request digest、permission/approval evidence 與 retry policy；尚未宣稱 remote success |
| `[DECISION] effect_dispatched` | 記錄 attempt ID 與 dispatch time；同一 logical effect 保持同 idempotency key |
| `[DECISION] effect_outcome_observed` | 收到 remote outcome 或可查詢 operation ID；response 經 schema validation |
| `[DECISION] effect_completed` | remote truth 已 reconcile，且 local result event durable；之後 replay 只讀 recorded result |
| `[DECISION] effect_ambiguous` | timeout/crash 使 outcome unknown；禁止盲目 resend，轉 query/dedup/manual review |
| `[DECISION] effect_compensation_requested` | 新增 compensating intent；不修改原 effect history，也不宣稱一定能完全 rollback |

## 7. Termination、Retry、Resume 與 Rollback Contracts

### Termination

- `[DECISION]` Terminal states 僅有 `completed`、`failed_non_retryable`、`cancelled`、`budget_exhausted`、`policy_blocked`；每個 terminal event 含 reason、final sequence、unresolved effect count 與 evidence locator。
- `[DECISION]` 每次 Model/Tool transition 前檢查 max iterations、wall-time deadline、token/cost budget、cancellation 與 approval lease；超限先寫 terminal event，不再啟動新 effect。
- `[DECISION]` `completed` 必須同時滿足 success assertions、無 pending mandatory step、無 unresolved high-risk effect。

### Retry

- `[DECISION]` Retry policy 明示 max attempts、retryable taxonomy、backoff/jitter、per-attempt timeout 與 total deadline；永久錯誤快速失敗。
- `[DECISION]` Logical retry 重用 operation ID/idempotency key；physical attempt 使用新的 attempt ID，讓 deduplication 與 observability 同時成立。
- `[DECISION]` Replay 不增加 retry count，也不重算 random jitter；下一個 scheduled time 是 history 的一部分。

### Resume

- `[DECISION]` Resume order：取得 single-run lease → 讀 terminal/approval state → 驗證 history → 驗證 checkpoint/snapshot manifest → replay/reduce → reconcile ambiguous effects → enforce budgets → 才 dispatch next transition。
- `[DECISION]` 同一 run 同時只能有一個 effect-dispatch owner；lease fencing token 寫入 dispatch evidence，避免 split-brain workers。
- `[DECISION]` Snapshot restore 不能繼承已過期 authorization；Tool credentials 必須重新取得且縮到最小 scope。

### Rollback

- `[DECISION]` Logical rollback 是 append compensation 或 fork new branch，不是倒轉/刪除 history。
- `[DECISION]` External rollback 只在 provider 支援且 business contract 定義時執行；例如 refund 是新 effect，不等於 erase 原 payment。
- `[DECISION]` Code rollback 仍需通過 historical replay compatibility；舊 binary 不一定能讀新 schema/snapshot。

## 8. Failure Matrix 與 Required Assertions

| Scenario | Expected Contract | Evidence Status |
| --- | --- | --- |
| `[DECISION]` Crash after remote effect, before completion record | Resume 進入 `effect_ambiguous`；以同 key query/reconcile，不盲目 resend | `[LOCAL_OBSERVATION] PASS — test_resume_deduplicates_effect_after_crash_before_completion_record；boundary calls=2、applications=1` |
| `[DECISION]` Duplicate event delivery | `event_id` dedup；reducer state/hash 不變；duplicate 有 metric | `[LOCAL_OBSERVATION] PASS — test_duplicate_event_id_is_applied_once` |
| `[DECISION]` Code/schema change during resume | Compatibility Gate 選 pinned worker、tested migrator/patch 或 diagnostic stop | `[LOCAL_OBSERVATION] PARTIAL PASS — unknown snapshot schema 會 full replay；未執行 reducer code migration / pinned worker` |
| `[DECISION]` Snapshot corrupt or absent | quarantine/skip snapshot；validated history 完整時 replay；不完整則 blocked | `[LOCAL_OBSERVATION] PASS（bounded）— corrupt、missing、foreign snapshot 均 full replay；未測 history 不完整` |
| `[DECISION]` Iteration/budget exceeded | terminal event durable；後續無新 Model/Tool effect | `[LOCAL_OBSERVATION] PASS — max_iterations 與 max_budget 均先寫 terminal event，再拒絕 iteration` |

- `[LOCAL_OBSERVATION]` Python `3.14.6` in-memory Lab 共執行 9 tests；同一 5-event workload 的 full replay 為 5 work units，3-event snapshot + tail replay 為 2 work units，最終 logical state 相同。這是 deterministic operation count，不是 production latency benchmark。
- `[INFERENCE]` 對 history 長、logical state 小的 workload，`validated logical checkpoint + deterministic tail replay` 可減少 reducer work，同時保留 event-history auditability；實際 latency / cost 仍需 persistent store 與 production workload benchmark。
- `[HYPOTHESIS]` Firecracker snapshot 可能再降低 environment cold-start latency，但 Compatibility、artifact size、secret/uniqueness 與 network reconciliation 成本可能抵銷收益。
- `[DECISION]` 在 replay-only、logical-checkpoint hybrid 與 Firecracker-assisted hybrid 以同一 workload 並列量測前，不做最終 ADR 選擇。

## 9. What-if Pivot

> `[DECISION]` **What if：** Run 在 `effect_intent_recorded` 後升級到新 reducer/schema；remote provider 已接受 request，但 Worker 在寫 `effect_completed` 前 crash，而最新 snapshot 又 checksum mismatch？

- `[DECISION]` 回答必須依序指出：哪一份 state 是 canonical、snapshot 為何可丟棄、哪個 version gate 決定 reducer、如何辨識 ambiguous external effect、是否重用 idempotency key、何時才允許下一個 transition。
- `[DECISION]` 合格答案不能說「從 snapshot 繼續再 call 一次」；它必須先由 validated history 重建，再對 remote operation 做 reconciliation。

## 10. Next-review Rule

- `[DECISION]` 第一次 Review 在完成 reducer/effect-boundary Lab 後 24 小時內：不看筆記重建四個 state partitions、完整 resume order、ambiguous effect window 與 corrupt-snapshot fallback。
- `[DECISION]` 7 天後用上述 What-if Pivot 做 active recall；若漏掉 version gate、idempotency retention、single-run lease 或 Firecracker external resources 任一項，建立 targeted repair 並於 48 小時內重測。
- `[DECISION]` Primary Source Review 在任一 pinned dependency major upgrade、Firecracker snapshot-format/Compatibility 變更、Temporal/LangGraph replay semantics 變更，或最遲 `2026-11-11` 觸發；重讀 current official docs 並更新 commit/version 與 Known Limits。

## 11. Source Qualification Ledger

### [T1] Temporal Server Architecture

- `[SOURCE]` URL: [Temporal canonical architecture README at `b4fbfe00ddb2ebd48236e9b4ffbabb5f10e71b72`](https://github.com/temporalio/temporal/blob/b4fbfe00ddb2ebd48236e9b4ffbabb5f10e71b72/docs/architecture/README.md)
- `[SOURCE]` Retrieval Date: `2026-08-11`; Version: full commit `b4fbfe00ddb2ebd48236e9b4ffbabb5f10e71b72`.
- `[INFERENCE]` Applies to: Temporal Server 的 Event Sourcing、Workflow/Activity boundary 與 durability design premise。
- `[INFERENCE]` Known Limits: Temporal-specific architecture；不直接規定自製 Agent log schema、checkpoint checksum 或 arbitrary third-party API semantics。

### [T2] Temporal History Service

- `[SOURCE]` URL: [History Service at `b4fbfe00ddb2ebd48236e9b4ffbabb5f10e71b72`](https://github.com/temporalio/temporal/blob/b4fbfe00ddb2ebd48236e9b4ffbabb5f10e71b72/docs/architecture/history-service.md)
- `[SOURCE]` Retrieval Date: `2026-08-11`; Version: full commit `b4fbfe00ddb2ebd48236e9b4ffbabb5f10e71b72`.
- `[INFERENCE]` Applies to: Workflow History topology 與由 History Events recovery relevant state 的能力。
- `[SOURCE]` Known Limits: Reset/conflict resolution 可形成 branch；不可把一般 case 的 linear history 誤寫成永不分支。

### [T3] Temporal Python SDK — Determinism and Replayer

- `[SOURCE]` URL: [Temporal Python SDK README at `b425e66180a697a29296e09e52898e1babd0ae98`](https://github.com/temporalio/sdk-python/blob/b425e66180a697a29296e09e52898e1babd0ae98/README.md)
- `[SOURCE]` Retrieval Date: `2026-08-11`; Version: release `1.31.0`（published `2026-07-29`）；researched full commit `b425e66180a697a29296e09e52898e1babd0ae98`。
- `[INFERENCE]` Applies to: Python Workflow deterministic constraints 與 history replay compatibility testing。
- `[INFERENCE]` Known Limits: Language SDK-specific；其他 runtimes 的禁用 API、sandbox 與 error type 可能不同。

### [T4] Temporal Python SDK — Patch Versioning

- `[SOURCE]` URL: [`patched` / `deprecate_patch` source at `b425e66180a697a29296e09e52898e1babd0ae98`](https://github.com/temporalio/sdk-python/blob/b425e66180a697a29296e09e52898e1babd0ae98/temporalio/workflow/_context.py#L552)
- `[SOURCE]` Retrieval Date: `2026-08-11`; Version: release `1.31.0`; full commit `b425e66180a697a29296e09e52898e1babd0ae98`。
- `[INFERENCE]` Applies to: 同一 Workflow History 跨 code path change 的 patch marker semantics。
- `[INFERENCE]` Known Limits: Patch API 不是任意 payload/schema migration engine；必須另測 data compatibility。

### [T5] Temporal Activity Error Handling and Idempotence

- `[SOURCE]` URL: [Temporal documentation source at `e71e76656dd9ead376fc8715eb7c5dc64bc8bf0c`](https://github.com/temporalio/documentation/blob/e71e76656dd9ead376fc8715eb7c5dc64bc8bf0c/docs/best-practices/error-handling.mdx#L111)
- `[SOURCE]` Retrieval Date: `2026-08-11`; Version: documentation full commit `e71e76656dd9ead376fc8715eb7c5dc64bc8bf0c`。
- `[INFERENCE]` Applies to: Activity retry、completion-report crash window 與 idempotency-key construction。
- `[INFERENCE]` Known Limits: Temporal Activity-specific recipe；destination 自身仍須接受並正確實作 idempotency semantics。

### [L1] LangGraph Persistence

- `[SOURCE]` URL: [LangGraph OSS Python — Persistence](https://docs.langchain.com/oss/python/langgraph/persistence)
- `[SOURCE]` Retrieval Date: `2026-08-11`; Version context: LangGraph release `1.2.11`、canonical repo full commit `644815f9e5bc52ad8f7a5227a456227e9c3e639b`；rendered page 未提供可驗證的 exact docs commit。
- `[INFERENCE]` Applies to: checkpointer/store state partition、thread continuity 與 persistent saver requirement。
- `[LOCAL_OBSERVATION]` Known Limits: Framework checkpoint semantics；文件沒有承諾 corrupt-checkpoint fallback，因此本 note 的 quarantine/replay 行為是 local `DECISION`。

### [A1] Axon Framework Snapshotting

- `[SOURCE]` URL: [Axon Framework snapshotting source at `4a160b775cbf9e152d0f7353c30747e5a14ef493`](https://github.com/AxonIQ/AxonFramework/blob/4a160b775cbf9e152d0f7353c30747e5a14ef493/docs/reference-guide/modules/tuning/pages/snapshotting.adoc)
- `[SOURCE]` Retrieval Date: `2026-08-11`; Version: release `v5.3.0`; full commit `4a160b775cbf9e152d0f7353c30747e5a14ef493`；qualified page is the `5.1` reference route at retrieval time。
- `[INFERENCE]` Applies to: Event-sourced entity 的 snapshot-as-cache semantics，以及 absent/incompatible/corrupt snapshot 的 full Event Stream fallback。
- `[INFERENCE]` Known Limits: Fallback 依賴完整、可讀且 schema-compatible 的 Event Stream；不代表 arbitrary VM snapshot 或已 corrupt canonical history 也能恢復。

### [K1] Apache Kafka 4.2 Design

- `[SOURCE]` URL: [Apache Kafka 4.2 — Design: Message Delivery Semantics](https://kafka.apache.org/42/design/design/#message-delivery-semantics)；[canonical source at `a18251bae0b825c69794a50dffd4c3100cf5ca5b`](https://github.com/apache/kafka/blob/a18251bae0b825c69794a50dffd4c3100cf5ca5b/docs/design/design.md#L195)。
- `[SOURCE]` Retrieval Date: `2026-08-11`; Version: `4.2.0`; release commit `a18251bae0b825c69794a50dffd4c3100cf5ca5b`。
- `[INFERENCE]` Applies to: exactly-once transaction boundary、consumer position/output coordination 與 external destination cooperation。
- `[SOURCE]` Known Limits: Kafka guarantees 不等於 Agent orchestrator 或第三方 Tool guarantee；此來源用於界定 boundary，不用來宣稱 Kafka 是必要 implementation。

### [S1] Stripe Idempotent Requests

- `[SOURCE]` URL: [Stripe API — Idempotent requests](https://docs.stripe.com/api/idempotent_requests)
- `[SOURCE]` Retrieval Date: `2026-08-11`; Version: live API reference，page 未提供 immutable commit/version。
- `[INFERENCE]` Applies to: provider-side idempotency-key recognition、parameter matching、result reuse 與 retention limit 的 concrete example。
- `[INFERENCE]` Known Limits: Stripe-specific；其他 Tool provider 可能沒有 idempotency、保留時間不同，或對 validation/rate-limit failures 有不同語意。

### [D1] Debezium Outbox Event Router

- `[SOURCE]` URL: [Debezium canonical Outbox Event Router source at `4d5cc38180816ec2ddfe184d968ad4aa254098c7`](https://github.com/debezium/debezium/blob/4d5cc38180816ec2ddfe184d968ad4aa254098c7/documentation/modules/ROOT/pages/transformations/outbox-event-router.adoc)
- `[SOURCE]` Retrieval Date: `2026-08-11`; Version: full commit `4d5cc38180816ec2ddfe184d968ad4aa254098c7`；rendered `stable` example reports connector version `3.6.1.Final`。
- `[INFERENCE]` Applies to: database/outbox consistency、event identity、CDC routing 與 consumer dedup support。
- `[SOURCE]` Known Limits: Outbox 不原子化 arbitrary remote API call；MongoDB 使用不同 SMT；downstream dedup 仍是 consumer responsibility。

### [F1] Firecracker Snapshot Support

- `[SOURCE]` URL: [Firecracker snapshot support at `48f1b9fb52e90f00b61adefcad002183d07195c1`](https://github.com/firecracker-microvm/firecracker/blob/48f1b9fb52e90f00b61adefcad002183d07195c1/docs/snapshotting/snapshot-support.md)
- `[SOURCE]` Retrieval Date: `2026-08-11`; Version: latest release `v1.16.1`（published `2026-07-02`）；researched full commit `48f1b9fb52e90f00b61adefcad002183d07195c1`。
- `[INFERENCE]` Applies to: microVM snapshot contents、load prerequisites、network/vsock behavior、immutable memory artifact、uniqueness/security 與 failure semantics。
- `[SOURCE]` Known Limits: Diff snapshot 仍為 developer preview；snapshot 不含完整 disk/host/network/application truth，且不是 Agent logical checkpoint。

### [F2] Firecracker Snapshot Versioning

- `[SOURCE]` URL: [Firecracker snapshot versioning at `48f1b9fb52e90f00b61adefcad002183d07195c1`](https://github.com/firecracker-microvm/firecracker/blob/48f1b9fb52e90f00b61adefcad002183d07195c1/docs/snapshotting/versioning.md)
- `[SOURCE]` Retrieval Date: `2026-08-11`; Version: latest release `v1.16.1`; full commit `48f1b9fb52e90f00b61adefcad002183d07195c1`。
- `[INFERENCE]` Applies to: snapshot format version/CRC、CPU/kernel/device compatibility 與 external host-resource references。
- `[SOURCE]` Known Limit: CRC64 是 optional。[F2]
- `[INFERENCE]` Known Limit: format compatibility 不是 workload semantic correctness 或 external effect consistency 的證明。

## 12. Claimed Acquisition Context（Non-load-bearing）

- `[LOCAL_OBSERVATION]` Issue #2 列出候選 Conference Talk：<https://www.youtube.com/watch?v=vi-2nasppAg>。
- `[LOCAL_OBSERVATION]` Issue #2 列出候選 Conference Talk：<https://www.youtube.com/watch?v=svCnShDvgQg>。
- `[LOCAL_OBSERVATION]` 這些影片與可能的 Gemini-expanded notes 只保留為 `claimed acquisition context`；本 note 沒有用它們支撐任何 load-bearing Claim，也沒有聲稱已觀看或驗證其內容。

## 13. Overall Known Limits

- `[INFERENCE]` 各 cited system 的 guarantee 都受自身版本、runtime 與 boundary 限制；Source Ledger 已逐一記錄 applicability。
- `[LOCAL_OBSERVATION]` Stripe 與 LangGraph rendered docs 沒有 immutable docs commit；已記錄 mutable-page limit，且沒有捏造版本 pin。
- `[LOCAL_OBSERVATION]` 已有 deterministic in-memory crash-boundary、duplicate delivery、corrupt/missing/foreign snapshot、unknown snapshot schema、termination 與 replay-work evidence；沒有 process-level durable store、real provider、distributed lease、reducer migration、Firecracker 或 production latency/cost evidence。
- `[LOCAL_OBSERVATION]` 本 note 的核心 reducer/effect-boundary contracts 已由 local assertions 操作化；因上述 external/distributed gaps，仍不能宣稱 production-ready。
