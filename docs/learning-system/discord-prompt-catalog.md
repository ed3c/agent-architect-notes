# Discord 可複製 Prompt 目錄

狀態：Active

版本：1.0.0

基準審查日：2026-08-11

本目錄先套用 [Prompt 分類法則](prompt-classification-rules.md)，需要自動分類時再使用
[Prompt Intent Classifier System Prompt](../agent-integration/PROMPT_CLASSIFIER_SYSTEM_PROMPT.md)。
這裡不重新定義法則，也不取代 Repository Instructions 或 Target Executor 的權限邊界。

## 使用方式

- 每個 Copy Block 都可獨立貼進 Discord Text Channel。
- `【...】` 是必填輸入；不知道時填 `unknown`，不要發明值。
- 一次只貼一個 Prompt。互不相關的工作分開送出。
- 下列排序是 **INFERENCE**，不是 Discord Telemetry。取得具代表性的 Observed Usage
  後，依 `prompt-classification-rules.md` 的 Recalibration Contract 調整。
- 每個 Block 都以一則 Discord 訊息可容納的長度為目標，不包含 Nested Fence。

## Part A — 通用 Prompt Families

### 1. Implementation — 聚焦實作

使用時機：需要在明確 Target 內完成一個 Code、Configuration 或 Artifact 變更。

必要輸入：Target、Outcome、Constraints、允許的 Write Scope。

```text
<task>
在【Target】完成【單一 Outcome】。只修改【允許的 Write Scope】，保留不相關變更。
</task>
<context>
先讀取有效的 Repository Instructions，再找 2–3 個最接近的 Existing Patterns、Library 與 Test Pattern；不要假設未檢查的 Repository、Tool 或 Permission 狀態。
Constraints：【Constraints；沒有則填 none】。
</context>
<follow_through>
完成 Narrow Implementation、相關 Tests、Self-review 與必要 Documentation。失敗要顯式且可診斷，不靜默吞掉。
</follow_through>
<verification>
執行最小但足以支持 Claim 的 Checks；分開回報 Static Inspection 與 Actual Execution。未執行的 Test 不得稱為 Passing。
</verification>
<output_contract>
回報 Changed Files、重要 Decision、實際 Commands／Checks、Result、Known Limits 與 Remaining Blocker。
</output_contract>
<stop_condition>
Outcome 與 Verification Gate 通過即停止；若缺少會改變 Scope 或 Authority 的資訊，只問一個精準問題。
</stop_condition>
```

### 2. Diagnosis — 先證明原因

使用時機：有 Bug、Failure 或 Regression，但 Root Cause 尚未被證明。

必要輸入：Failure Symptom、Reproduction、Environment／Version、可讀取的 Evidence。

```text
<task>
診斷【Failure Symptom】的 Root Cause。這是 Read-only Task，不要實作 Fix。
</task>
<context>
Reproduction：【步驟或 unknown】；Environment／Version：【值或 unknown】；Evidence：【Log、Trace、Test、File 或 Locator】。先重現；無法重現時明示 Blocked。
</context>
<method>
分開列出 Observation、Hypothesis 與 Decision。每個 Hypothesis 必須附一個可證偽的 Discriminating Test；優先檢查最小範圍與第一個 Divergence。
</method>
<verification>
只有 Evidence 排除主要替代解釋時才稱 Root Cause；否則回報最可能 Hypothesis 與最小下一個 Test。
</verification>
<output_contract>
輸出 Reproduction Result、Observed Facts、Root Cause 或 Hypotheses、Evidence Locator、Affected Scope、Smallest Repair Direction 與 Unknowns。
</output_contract>
<stop_condition>
原因被足夠 Evidence 支持，或一個具名 Dependency 阻止下一個辨別測試時停止。
</stop_condition>
```

### 3. Review — Actionable Findings

使用時機：需要 Code／Architecture／Document Review，不授權修改。

必要輸入：Review Target、Fixed Comparison Point、Review Focus。

```text
<task>
Review【Target】相對於【Commit、Branch、Spec 或其他 Fixed Comparison Point】的變更。保持 Read-only，不實作 Fix。
</task>
<context>
Review Focus：【Correctness／Security／Performance／Maintainability／Contract；可複選】。讀取 Target Instructions 與直接受影響的 Tests／Contracts，不擴張到無關內容。
</context>
<verification>
每個 Finding 必須能指出 File／Section／Line 或 Evidence Locator，說明可觸發情境、影響與為何現有防護不足。沒有足夠 Evidence 就標記 Unknown，不湊數。
</verification>
<output_contract>
先列 Findings，依 Critical／High／Medium／Low 排序；每項含 Location、Impact、Evidence、最小建議。若無 Finding，明說 No actionable findings，並列 Remaining Risk 與未執行的 Checks。
</output_contract>
<stop_condition>
已覆蓋 Review Focus 與直接影響面，且所有 Claim 都有 Locator 或明示 Limit 時停止。
</stop_condition>
```

### 4. Testing and Evaluation — Evidence Gate

使用時機：需要證明 Artifact 是否符合 Contract，而不是只產生 Test Ideas。

必要輸入：Artifact、Contract、Fixture／Environment、允許執行的 Commands。

```text
<task>
評估【Artifact】是否符合【Contract】；使用【Fixture／Environment】執行可重現 Checks。
</task>
<context>
允許 Commands：【Commands 或 unknown】。未授權或缺少 Dependency 時不要假裝執行，改標記 Blocked。
</context>
<verification>
先使用 Deterministic Assertions、Schema、Parser、Exact Comparison 與 Exit Code；只有不可機械判斷的部分才使用 Model Judgment。保留 Negative Cases、Counterexamples 與 Failure Behavior。
</verification>
<output_contract>
逐項輸出 Assertion、Evidence Class、Command、Actual Result、Pass／Fail／Blocked、First Divergence 與 Known Limits。分離 Static、Execution、Deployment 與 Production Evidence。
</output_contract>
<stop_condition>
所有 Contract Assertions 都有 Result，或具名 Blocker 已記錄；不得以部分 Passing 推論整體成功。
</stop_condition>
```

### 5. Explanation and Learning — 建立 Mental Model

使用時機：要理解 Concept、Boundary 或 Mechanism，不要求實作。

必要輸入：Topic、Audience／現有程度、希望能回答的問題。

```text
<task>
用繁體中文與必要 English 專有名詞，向【Audience／程度】解釋【Topic】，讓我能回答【目標問題】。保持 Read-only。
</task>
<context>
先說明 Definition、Boundary 與 Assumptions；若 Topic 依賴近期 Version 或 External Standard，先用 Current Primary Source Grounding，無法查證就標記 Unknown。
</context>
<method>
建立一個 Concrete Mental Model，再說明 Mechanism、Trade-offs、Failure Modes 與一個最小 Counterexample；內容以直接回答目標問題為準。
</method>
<output_contract>
輸出 Short Answer、Mental Model、Key Invariants、Common Misconception、Minimal Example、Limits，最後只問一個理解檢查問題。
</output_contract>
<stop_condition>
目標問題已被直接回答，且 Boundary、Unknown 與理解檢查存在時停止。
</stop_condition>
```

### 6. Planning and System Design — Decision-ready Contract

使用時機：需要 Plan 或 Architecture Decision，尚未授權 Implementation。

必要輸入：Goal、Constraints、Scale／Workload、Non-goals、Decision Deadline。

```text
<task>
為【Goal】設計 Decision-ready Plan／Architecture。這是 Read-only Design Task，不實作。
</task>
<context>
Constraints：【Constraints】；Scale／Workload：【值或 unknown】；Non-goals：【內容】；Decision Deadline：【日期或 none】。先質疑是否需要 Agent Judgment；規則完整穩定時優先 Deterministic Workflow。
</context>
<completeness>
涵蓋 Requirements、Boundaries、State、Interfaces、Failure Behavior、Security、Observability、Testing／Evals、Rollout、Rollback、Cost 與 Operations；只加入會影響 Decision 的項目。
</completeness>
<output_contract>
輸出 Goals／Non-goals、Assumptions、2–3 個 Alternatives、Trade-off Matrix、Recommended Decision、Architecture Flow、Risks、Validation Plan、Open Questions 與最小下一步。
</output_contract>
<stop_condition>
Decision 有可追溯理由與 Validation Gate；若關鍵 Workload 或 Authority 未知，只問一個會改變選擇的問題。
</stop_condition>
```

### 7. Research and Source Qualification — Primary Sources First

使用時機：Claim 可能近期變動、Local Knowledge 不足，或需要可引用的研究結果。

必要輸入：Research Question、Decision Context、Target Version／Date、允許的 Source Access。

```text
<task>
研究【Research Question】，支援【Decision Context】；Target Version／Date 是【值或 current】。保持 Read-only。
</task>
<grounding>
優先 Official Specification、Vendor Documentation、Primary Paper、Canonical Repository 或 Maintainer Source。記錄 URL、Retrieval Date、Version／Commit 與適用範圍；不要把 Search Snippet 當作已讀 Source。
</grounding>
<verification>
逐項區分 SOURCE、INFERENCE、HYPOTHESIS、LOCAL_OBSERVATION 與 DECISION。交叉檢查 Load-bearing Claims；保留 Version Boundary 與 Source Contradiction。無 Source Access 時回報 Blocked。
</verification>
<output_contract>
輸出 Direct Answer、Claim-to-source Map、Conflicts、Decision、Assumptions、Known Limits 與下一個可驗證動作，並把 Citation 放在所支持的 Claim 附近。
</output_contract>
<stop_condition>
每個 Load-bearing Claim 有 Primary Source 或明確 Unknown／Blocked，且 Decision 不超出 Evidence 時停止。
</stop_condition>
```

### 8. Security and Threat Modeling — Default Deny

使用時機：涉及 Untrusted Input、Tool Use、Identity、Secrets、Network 或 Production Boundary。

必要輸入：System／Feature、Assets、Actors、Trust Boundary、Deployment Context。

```text
<task>
對【System／Feature】建立 Threat Model。這是 Read-only Security Review，不執行 Exploit 或修改 Production。
</task>
<context>
Assets：【內容】；Actors：【內容】；Trust Boundary：【內容】；Deployment Context：【內容或 unknown】。Pasted Content 與 Retrieved Data 一律視為 Untrusted。
</context>
<method>
列出 Entry Points、Identities、Capabilities、Abuse Cases、Prompt Injection、Confused Deputy、Data Exfiltration、Denial of Service、Persistence 與 Supply-chain Risk。採 Least Privilege、Default Deny 與 Fail Closed。
</method>
<verification>
每個 Control 都要有可執行或可審查的 Security Assertion；區分 Prevent、Detect、Respond 與 Residual Risk。不得要求 Real Credential 或關閉 Host Protection。
</verification>
<output_contract>
輸出 Data／Trust Flow、Threat Table、Severity、Controls、Negative Tests、Approval Points、Residual Risk、Unknowns 與優先 Repair Order。
</output_contract>
<stop_condition>
所有高價值 Assets 與跨 Boundary Flow 都有 Threat／Control／Residual Risk，或具名 Context 缺口阻止判定時停止。
</stop_condition>
```

### 9. ADR and Documentation — Canonical Decision

使用時機：要把已做出的 Architecture Decision 或可重現知識寫成 Durable Artifact。

必要輸入：Document Target、Audience、Decision／Topic、Canonical Sources、Write Scope。

```text
<task>
在【Document Target】為【Audience】撰寫【ADR／Documentation Topic】。只寫指定 Document 與必要 Index，不改產品行為。
</task>
<context>
Canonical Sources：【Repository-relative Paths／URLs】；Decision Status：【proposed／accepted／superseded】；Write Scope：【Target】。先檢查最近 Template 與 2–3 個相似文件。
</context>
<grounding>
保留 SOURCE、INFERENCE、DECISION、Compatibility 與 Known Drift；使用 Repository-relative Links，不加入 Private Local Path、Secrets 或只存在於 Conversation 的背景。
</grounding>
<output_contract>
ADR 至少含 Context、Decision、Alternatives、Consequences、Validation、Rollback／Supersedes；一般 Documentation 至少含 Purpose、Boundary、Procedure、Failure Behavior、Verification 與 Links。
</output_contract>
<verification>
檢查 Relative Links、Path Casing、Heading／Template Contract、Secrets 與 Diff；回報 Changed Files 與 Checks。
</verification>
<stop_condition>
Artifact Dependency-closed、Links 可解析且沒有虛構 Current State 時停止。
</stop_condition>
```

### 10. Delivery and Status — Receipt-backed

使用時機：查詢 Live Status，或在已有明確授權與 Gate 下完成 PR Delivery。

必要輸入：Repository、Issue／PR、Requested Operation、Merge Authority。

```text
<task>
對【Repository】的【Issue／PR】執行【read-only status／publish PR／merge】；Merge Authority 是【明確 Policy／none／unknown】。
</task>
<grounding>
先讀 Live Remote State、Immutable IDs、Current HEAD、Checks、Reviews、Mergeability 與 Dependency。Planned、Prepared 或 Local-only 狀態不得描述成 Delivered。
</grounding>
<action_safety>
只有 Requested Operation 與既有 Authority 同時允許時才 Mutation。不得 Bypass Tests、Review、Branch Protection 或 HEAD Pin；Authority 不明時停在 Read-only Status 或 Green PR。
</action_safety>
<output_contract>
輸出 Repository、Issue／PR URL、Before／After State、HEAD／Merge SHA、Checks、Operation Result、Provider Receipt、Blocked Reason 與 Next Action。
</output_contract>
<stop_condition>
Requested Operation 有 Live Receipt，或具名 Gate／Permission 阻止執行時停止；不得承諾不存在的 Background Automation。
</stop_condition>
```

## Part B — Agent Architecture 專案應用

以下 Prompt 直接對應 Issues #2–#7。每個 Issue 是一個完整 Learning Unit Slice；不要把
六張 Issue 合併成單一 Mega-prompt。

### A1. Durable Agent State — Issue #2

使用時機：開始 [Issue #2](https://github.com/ed3c/agent-architect-notes/issues/2)。

必要輸入：Repository Access、可執行 Test Environment；缺少時保持 Blocked。

```text
<task>
完成 https://github.com/ed3c/agent-architect-notes/issues/2 的 Durable Agent State Learning Unit。先讀 AGENTS.md、Issue 與 docs/agent-integration/；沿用 docs/kb/、docs/templates/、docs/adr/、exercises/ 的最近 Pattern。
</task>
<output_contract>
產出 Source-qualified Knowledge Note、Durable Orchestrator System Design Exercise、Replay／Snapshot／Hybrid ADR，以及 Minimal Reducer／Effect-boundary Lab 或等價 Reproducible Simulation。明示 State Partition、Termination、Checkpoint、Resume、Idempotency、Retry、Rollback 與 Side-effect Boundary。
</output_contract>
<verification>
在同一 Workload 並列量測 Replay 與 Snapshot Alternative；執行 Crash／Restart、Duplicate Delivery、Schema Version Change、Snapshot Corruption 與 Budget Limit Cases。保存 Commands、Exit Codes、Versions、Evidence Locators；Static Evidence 不冒充 Execution。
</verification>
<evidence_maturity>
Candidate Talk 只算 claimed；Primary Source 是 SOURCE；實際 Lab Result 才能升到 observed／verified。衝突與 Unknown 必須保留。
</evidence_maturity>
<stop_condition>
Issue Acceptance Criteria 與 Relative Link／Privacy Checks 全部通過後建立 Closes #2 的 PR；Merge 只依目前明確 Authority 與 Merge Gate，否則停在 Green PR。回報 Delivery Receipt：Issue／PR URL、HEAD／Merge SHA、Checks 與 Blocker。
</stop_condition>
```

### A2. Zero-trust Sandbox — Issue #3

使用時機：開始 [Issue #3](https://github.com/ed3c/agent-architect-notes/issues/3)。

必要輸入：Safe Fixture Environment；不得使用 Real Credential 或關閉 Host Protection。

```text
<task>
完成 https://github.com/ed3c/agent-architect-notes/issues/3 的 Zero-trust Agent Code Sandbox Learning Unit。先讀 AGENTS.md、Issue、docs/kb/evals-security-observability.md 與最近 Exercise／System Design Template。
</task>
<output_contract>
產出 Threat Model、Isolation Alternative Comparison、Runnable Sandbox Exercise、Negative-test Corpus 與 Security Evidence Report。明示 Identity、Capability、Asset、Trust Boundary、Approval Point、Resource Limit、Secret Isolation、Egress Policy 與 Guaranteed Cleanup。
</output_contract>
<verification>
在 Safe Fixture 實測 Forbidden Filesystem、Outbound Network、Secret Read、Resource Exhaustion、Residual Process／File，以及 Success／Failure／Timeout Cleanup。對同一 Threat／Workload Matrix 比較 Isolate、Container、MicroVM 與 Network Identity Boundary。
</verification>
<evidence_maturity>
Vendor Claim 未經 Current Official Documentation 與 Version Scope 只能是 claimed；Execution Report 只支持 Tested Environment，不外推 Production。
</evidence_maturity>
<stop_condition>
所有 High-risk Flow 有 Negative Assertion，且 Issue Criteria、Links、Secrets Scan 通過後建立 Closes #3 的 PR；未授權 Merge 時停在 Green PR。回報 Delivery Receipt：Issue／PR URL、HEAD／Merge SHA、Checks 與 Blocker。
</stop_condition>
```

### A3. Benchmark Integrity — Issue #4

使用時機：開始 [Issue #4](https://github.com/ed3c/agent-architect-notes/issues/4)。

必要輸入：Pinned Paper／Repository Version、Reproducible Fixture、Network／Git History Policy。

```text
<task>
完成 https://github.com/ed3c/agent-architect-notes/issues/4 的 Coding-Agent Benchmark Integrity Learning Unit。先讀 AGENTS.md、Issue 與 docs/kb/evals-security-observability.md；驗證並 Pin Primary Paper／Canonical Repository Version。
</task>
<output_contract>
產出 Benchmark-integrity Note、Baseline Runner、獨立重建的 Hardened Runner、Adversarial Fixtures 與 Comparison Report。Functional Success 與 Integrity Success 必須是兩個獨立 Gate。
</output_contract>
<verification>
在相同 Fixtures 並列執行兩個 Runner；Negative Controls 覆蓋 Hidden Git History、Outbound Lookup、Cached Answer、Test Deletion／Weakening 與 Harness Tampering。至少證明一個 Baseline 錯誤接受而 Hardened Runner 拒絕的 Case，保存 Commands、Exit Codes、Cost／Latency 與 Locators。
</verification>
<evidence_maturity>
Candidate Source 不等於 Current Fact；Static Inspection 不等於 Execution；Task Passing 但 Integrity Violation 必須判 Invalid。
</evidence_maturity>
<stop_condition>
同 Workload Comparison 與所有 Issue Assertions 通過後建立 Closes #4 的 PR；無法隔離 Leakage Source 時回報 Blocked，不宣稱 Valid Benchmark。回報 Delivery Receipt：Issue／PR URL、HEAD／Merge SHA 與 Checks。
</stop_condition>
```

### A4. LLM Judge Calibration — Issue #5

使用時機：開始 [Issue #5](https://github.com/ed3c/agent-architect-notes/issues/5)。

必要輸入：Labeled Dataset、Judge／Prompt Version、Holdout Boundary、允許的 Evaluation Cost。

```text
<task>
完成 https://github.com/ed3c/agent-architect-notes/issues/5 的 Eval Maturity 與 LLM Judge Calibration Learning Unit。先讀 AGENTS.md、Issue 與 docs/kb/evals-security-observability.md；不要沿用未量測的 Vendor Threshold。
</task>
<output_contract>
產出 Eval-maturity Note、含 Label Rationale／Ambiguity 的 Dataset、Deterministic 與 Model-based Scorers，以及含 Release-gate Decision 的 Calibration Report。區分 Calibration、Holdout 與 Production Observation。
</output_contract>
<verification>
Deterministic Assertions 優先；Judge Output 與 Human Label 比較，Unknown Label 保持 Unknown。執行 Position-order Reversal 或等價 Bias Control，從 Actual Results 計算 Confusion Matrix 與至少一個 Agreement／Error Metric；測 Same-family、Verbosity 與 Prompt／Version Drift。
</verification>
<evidence_maturity>
Generated Statistics 與 Vendor Claims 只算 claimed；Observed Error 與 Reproducible Calculation 才能支持 Threshold Decision。
</evidence_maturity>
<stop_condition>
Threshold 能由 Observed Error Cost 解釋、Holdout 未污染且 Issue Criteria 通過後建立 Closes #5 的 PR；Evidence 不足時不放行 Release Gate。回報 Delivery Receipt：Issue／PR URL、HEAD／Merge SHA、Checks 與 Blocker。
</stop_condition>
```

### A5. Agent Observability — Issue #6

使用時機：開始 [Issue #6](https://github.com/ed3c/agent-architect-notes/issues/6)。

必要輸入：Trace Fixture、Redaction Policy、Repository-compatible Tooling。

```text
<task>
完成 https://github.com/ed3c/agent-architect-notes/issues/6 的 Agent Observability Learning Unit。先讀 AGENTS.md、Issue 與 docs/kb/evals-security-observability.md；只使用 Repository-compatible Tooling。
</task>
<output_contract>
產出 Trace／Span／State／Eval Boundary Note、Minimal Traced Agent／Tool Workflow、Injected Silent-failure Scenario、Replay／Diagnosis Report、Failure Taxonomy 與 Redaction Policy。Trace 要連結 Model／Tool Boundary、State Transition、Latency、Cost／Usage 與 Human Intervention。
</output_contract>
<verification>
注入一個 HTTP／Process Success 但 Semantic Task Failure 的 Case，Replay 並定位 First Divergent Step。同時輸出 Outcome Metrics 與 Trajectory Metrics；保存 Trace ID、Commands、Version 與 Evidence Locator。驗證 Redaction 後 Evidence Class 沒被誇大。
</verification>
<evidence_maturity>
Local Trace 只支持 Tested Run，不稱為 Production Behavior；未獨立驗證的 Product Comparison 或 Performance Number 必須移除或標記 claimed。
</evidence_maturity>
<stop_condition>
Silent Failure 可重播、First Divergence 可定位、Privacy／Retention／Access-control Trade-off 完整且 Issue Criteria 通過後建立 Closes #6 的 PR。回報 Delivery Receipt：Issue／PR URL、HEAD／Merge SHA 與 Checks。
</stop_condition>
```

### A6. Skills × MCP — Issue #7

使用時機：開始 [Issue #7](https://github.com/ed3c/agent-architect-notes/issues/7)。

必要輸入：Pinned Official Sources、Safe Test Tool／Simulated MCP、Identical Task Set。

```text
<task>
完成 https://github.com/ed3c/agent-architect-notes/issues/7 的 Skills × MCP Capability Packaging Learning Unit。先讀 AGENTS.md、Issue、docs/learning-system/agent-architect-capstone.md 與最近 Knowledge／Exercise Pattern；Pin Official Agent Skills、MCP 與相關 Platform Sources。
</task>
<output_contract>
產出 Skill／MCP Boundary Design Note、一個 Focused Skill、Safe Test Tool 或 Simulated MCP、No-skill Baseline、Skill-enabled Variant、Eval Report 與 Skill Registry Metadata。Skill 承載 Task Knowledge／Workflow Constraint；MCP／Tool Contract 承載 Authenticated Capability。
</output_contract>
<verification>
兩個 Variant 使用 Identical Task Set；量測 Task Success、Tool Selection、Argument Precision、Schema Compliance 與至少一個 Security Assertion。加入 Negative Case 證明 Tool Access 不保證 Correct／Safe Use；Security-critical Constraint 不得只藏在 Progressive Disclosure 後段。
</verification>
<evidence_maturity>
不得按名稱推論 Skill 與 Tool 的效果；只有並列 Actual Eval Evidence 才能從 Draft 升格。Source、Inference、Observation 與 Decision 分開。
</evidence_maturity>
<stop_condition>
Registry 含 Semantic Version、Compatibility、Permissions、Evidence 與 Rollback／Removal，且 Issue Criteria 通過後建立 Closes #7 的 PR；沒有 Eval Evidence 時保持 Draft。回報 Delivery Receipt：Issue／PR URL、HEAD／Merge SHA、Checks 與 Blocker。
</stop_condition>
```

## Maintenance

- Taxonomy 或排序變更：先修改 `prompt-classification-rules.md` 與 Classifier Version，再更新本目錄。
- Prompt 行為變更：新增或更新 `docs/agent-integration/INTEGRATION_TESTS.md` Scenario。
- Issue Scope 變更：以 Live GitHub Issue 為準；本目錄只保留 Prompt Contract，不複製 Acquisition Notes。
- Telemetry 必須 Privacy-preserving，未達代表性前排序持續標示 `INFERENCE`。
