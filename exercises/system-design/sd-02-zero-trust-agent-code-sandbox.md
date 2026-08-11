# SD-AA-02：Zero-trust Agent Code Execution

> Issue: [#3](https://github.com/ed3c/agent-architect-notes/issues/3)
> Date: `2026-08-11`
> Status: `Accepted — learning-unit design；production qualification pending`

## 1. Business Objective

讓 Agent 能執行 generated code、tests 與 data transform，同時把 workload 視為 hostile。成功條件不是「command 跑完」，而是 code 只能取得 task contract 明示的 capabilities；RCE、prompt injection、exfiltration、confused deputy、DoS 與 residual state 都有可觀測的阻擋或 containment path。

## 2. Workload Classes

| Class | Example | Data sensitivity | Egress | Adversary assumption |
| --- | --- | --- | --- | --- |
| W1 | 純文字/JSON transform | public / synthetic | none | accidental bad code |
| W2 | private repository tests | proprietary source | package proxy / approved Tool only | prompt injection、dependency attack |
| W3 | multi-tenant code judge / autonomous coding Agent | tenant-confidential | default none；per-action broker | deliberate hostile code、escape attempt |

本地 [LAB-AA-02](../production-labs/lab-02-zero-trust-sandbox/README.md) 只驗 W1/W2 的 bounded Docker profile，不能當 W3 production acceptance。

## 3. Trust Model

### Assets

- tenant code / data、model context、Tool credentials、host filesystem、control-plane API、audit trail、compute budget、other tenants。

### Identities

- human requester、Agent run、orchestrator、sandbox instance、credential broker、Tool/resource server、audit writer。

Agent natural-language output 不是 authorization principal。每個 effect 都綁定 `tenant_id + user_id + run_id + sandbox_id + action + resource + expiry`。

### Approval Points

- 新增 network destination、writable persistent volume、device/GPU、credential scope、privileged capability、cross-tenant data 或 destructive Tool action。
- Workload 不能透過 prompt 自行批准 policy expansion。

## 4. Threat-to-Control Contract

| Threat | Prevent / contain | Detect | Recovery |
| --- | --- | --- | --- |
| RCE / escape | non-root、no-new-privileges、drop caps、minimal image；高風險用 gVisor/MicroVM | runtime violation、kernel/runtime alert | kill + quarantine evidence；rotate exposed capability |
| Prompt injection | instructions 是 untrusted data；policy 在 deterministic control plane | denied capability request / policy delta | keep sandbox default-deny；human review expansion |
| Data exfiltration | no egress；approved traffic只經 identity-aware proxy/broker | destination/action/bytes audit；deny metric | revoke short-lived grant；isolate run |
| Confused deputy | broker independently authorize subject/action/resource | subject/resource mismatch | deny、audit、require fresh consent |
| DoS | CPU/time/memory/PID/output/storage quotas | limit hit、timeout、queue saturation | terminate instance；budget terminal state |
| Residual state | per-run ephemeral root/data；no sandbox reuse across tenants | inventory/leak canary | destroy instance/storage key；block pool reuse |

## 5. Isolation Alternatives — Same Matrix

Network identity 是 orthogonal authorization control，不是 RCE isolation alternative；拿「有 SPIFFE identity」取代 container/MicroVM boundary 是 category error。

| Boundary | Kernel isolation | Startup / density | W1 | W2 | W3 | Main limit |
| --- | --- | --- | --- | --- | --- | --- |
| Same-process / language sandbox | none；依 runtime verifier | best | 僅限非任意 native code | reject | reject | runtime escape = host process compromise |
| OS process + uid/rlimit | shared host kernel / filesystem config | high density | conditional | reject by default | reject | policy composition fragile；network/filesystem containment不足 |
| OCI container / runc | namespaces/cgroups/seccomp；shared kernel | fast / dense | accept | conditional | insufficient alone | kernel/runtime escape blast radius |
| gVisor sandboxed container | user-space application kernel mediates syscalls | medium | accept | preferred option | conditional after benchmark | compatibility/performance gaps；仍需 network/identity controls |
| Firecracker MicroVM | dedicated guest kernel + VMM boundary | lower density / stronger boundary | optional | preferred for high sensitivity | baseline candidate | lifecycle/image/network complexity；not absolute security |
| Network identity / egress proxy | no compute isolation | orthogonal | required when egress opens | required | required | stolen/confused identity 若 authorization錯仍可外洩 |

## 6. Decision

### Local Learning Lab

使用 pinned Docker image + runc，因為可在現有環境實際量測 filesystem/network/resource/cleanup controls。所有 claim 明確限於 local Docker boundary。

### Production W2 / W3

1. W2 先以 gVisor 或 per-run MicroVM candidate 做同一 negative corpus / compatibility / cost benchmark。
2. W3 預設 per-run MicroVM、ephemeral disk key、single-tenant instance；除非反證顯示 gVisor 在指定 threat model 已足夠。
3. 任何 egress 都經 deterministic policy compiler + identity-aware proxy / Tool broker；sandbox 沒有 raw long-lived credential。
4. Control plane、credential broker、audit sink 與 image builder 不在 sandbox trust domain。

這是候選決策，不是 vendor guarantee；production acceptance 需要真正 gVisor/Firecracker rebuild-and-compare evidence。

## 7. High-level Architecture

```text
User / Agent request (untrusted intent)
          |
          v
Task Contract + Policy Compiler -----> Human Approval (policy expansion only)
          |
          v
Scheduler + Quota -----> Ephemeral Sandbox (no credentials, default no egress)
          |                         |
          |                         +--> stdout/stderr/result (bounded + redacted)
          |                         |
          |                         +--> Broker request (subject/action/resource)
          |                                      |
          +--> Audit Writer <--------------------+--> Approved Tool / Egress Proxy
          |
          +--> Timeout/Kill/Cleanup --> Inventory & Residual-state verifier
```

## 8. API and Evidence Contract

`CreateExecution` 必須明示 immutable image digest、command/entrypoint、input artifact hashes、CPU/time/memory/PID/output limits、filesystem mounts、network mode、capability requests、tenant/run identity、approval receipts 與 retention。

Execution receipt 至少含 policy hash、runtime/version、image digest、sandbox identity、start/end/termination reason、limit hits、broker decisions、network destinations、mount manifest、cleanup result與 redacted output hashes。Audit log 不存 raw credential。

## 9. Egress and Credential Flow

1. Default route = none。
2. Workload 只能送 structured action request 給 broker，不自行取得 credential。
3. Broker 重新驗證 human/user/run identity、approval、action、resource、budget、expiry。
4. Broker 代表 subject 呼叫 Tool，或簽發 destination-bound、short-lived、single-purpose capability。
5. Proxy 同時 enforce DNS/IP/port/SNI/HTTP action、response size、redirect 與 rebinding policy。
6. Outcome 以 result reference 回 sandbox；raw long-lived secret 永不進 sandbox memory/environment/filesystem。

## 10. Cleanup State Machine

`RUNNING → TERMINATING → RUNTIME_REMOVED → EPHEMERAL_STORAGE_DESTROYED → LEASE_REVOKED → VERIFIED_CLEAN`。

Success、nonzero failure、timeout、cancellation、orchestrator crash 都進同一 idempotent cleanup workflow。若 inventory、storage key destruction或 lease revoke 任一步未知，狀態是 `cleanup_pending/blocked`，sandbox ID 不得重用。

## 11. Rollout / Rollback

- 用固定 negative corpus 對每個 runtime/image/kernel/version重跑。
- Shadow 模式只比較 policy decision，不把 production data 送新 sandbox。
- Canary 依 tenant/risk class，小量放行並監控 denied requests、escape signal、cleanup lag、latency/cost。
- Runtime rollback 仍需確認舊版能讀新 policy/receipt schema；不能用 rollback 停用 security control。
- 發現 escape 或 residual state 時，停止該 runtime pool、revoke grants、保存最小 forensic evidence、rotate可能受影響 credential。

## 12. Evidence

- Primary Source threat model：[Zero-trust Agent Sandbox](../../docs/kb/zero-trust-agent-sandbox.md)
- Docker negative Lab：[LAB-AA-02](../production-labs/lab-02-zero-trust-sandbox/README.md)
- Executed security report：[2026-08-11](../../docs/eval-reports/2026-08-11-zero-trust-sandbox.md)

## 13. What-if Pivot / Review

> W3 workload 需要從 private package registry 下載 dependency，又要呼叫能讀 customer records 的 Tool。dependency manifest 可能被 prompt injection 修改。你會把 network、identity、credential 與 approval 分在哪些 boundary？redirect / DNS rebinding / package post-install script 怎麼處理？

Pass rule：答案必須區分 compute isolation 與 network identity；raw credential 不進 sandbox；package fetch 與 customer Tool 是不同 capability；所有 expansion 有 approval/evidence；cleanup不因 task failure略過。

Review：`2026-08-12` active recall；`2026-08-18` 用 What-if 重答。任何 runtime/kernel major change、image digest change 或新 egress capability 都立即重新 qualify。
