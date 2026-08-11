# State and Evidence Contract

This document defines the exact state model shared by the GitHub knowledge base, the `Agent Architect Learning Dashboard`, and any learning agent using them.

The contract is intentionally strict. It prevents a plausible narrative from replacing live state, observable evidence, or a returned write receipt.

## 1. Spreadsheet identity

- Title: `Agent Architect Learning Dashboard`
- Spreadsheet ID: `1cd-TL6N2_PD-EktZqZOafRsdCd-BZFOJO-ww3kYWnsA`
- Locale: `zh_TW`
- Timezone: `Asia/Taipei`
- Learning plan start date: `2026-08-11`

Always read live metadata before ranges. Numeric `sheetId` values below are an observed snapshot and may change if a tab is deleted and recreated; exact visible titles remain the routing key.

## 2. Source-of-truth matrix

| Data | Canonical source | Secondary source | Conflict behavior |
| --- | --- | --- | --- |
| Planned task | `Daily Plan` row by `Plan ID` | Linked GitHub task document | Report conflict; do not merge silently |
| Actual status and session scores | `Session Log` row by `Plan ID` | Session note | Live keyed row wins for control state |
| Exercise stage and review date | `Exercise Log` row by `Exercise ID` | Memory capsule | Report conflict and preserve both locators |
| Long-form explanation and evidence | Committed GitHub artifact | Sheet URL and notes | GitHub commit is canonical artifact |
| Scoring weights | `Settings` plus scoring document | Formula in `Session Log` | Formula must match configured weights |
| User energy and self-reported independence | Current conversation | Session note | Never infer when absent |
| Current time | Runtime clock in `Asia/Taipei` | Planned row date/time | Runtime time is current; row is schedule |
| Agent behavior | `AGENTS.md` and `docs/agent-integration/` | Tool adapter | Canonical contract wins |

## 3. Live tab snapshot

Observed on `2026-08-11`:

| Tab | Observed `sheetId` | Purpose |
| --- | ---: | --- |
| Setup | `1212473063` | Human operating overview and links |
| Settings | `1829717250` | Timezone, slots, weights, and configuration |
| Daily Plan | `1981235131` | Scheduled 28-week sessions |
| Session Log | `542701851` | Actual session status, scores, and evidence |
| Daily Summary | `139904081` | Date-level rollup |
| Dashboard | `1118226086` | KPI and readiness view |
| LeetCode Tracker | `536920839` | Problem pattern and stage tracking |
| Production Labs | `1898043685` | Production lab tracking |
| System Design | `1835211534` | System-design tracking |
| English Drills | `1995855114` | English practice tracking |
| Exercise Log | `901706488` | Granular evidence and review schedule |
| Scoring Rubric | `1715236295` | Human-readable scoring definitions |
| GitHub Docs Index | `695687130` | Repository document index |
| Knowledge Index | `1292977536` | Domain-to-trigger knowledge map |
| First Task | `600062004` | Two Sum starter task |

A connector must resolve these titles from live metadata rather than hard-coding numeric IDs as the only lookup mechanism.

## 4. Key schemas

### 4.1 `Settings` — observed columns `A:E`

| Column | Header | Contract |
| --- | --- | --- |
| A | Key | Stable setting name |
| B | Value | Setting value |
| C | Notes | Meaning and constraints |
| D | Category | Schedule, Cadence, Scoring, or related group |
| E | GitHub Doc URL | Canonical supporting document |

Observed required keys:

- `start_date`
- `timezone`
- `slot_1`
- `slot_2`
- `slot_3`
- `correctness_weight`
- `independence_weight`
- `tests_weight`
- `explanation_weight`
- `review_weight`
- `energy_weight`

### 4.2 `Daily Plan` — observed columns `A:L`

| Column | Header |
| --- | --- |
| A | Plan ID |
| B | Date |
| C | Week |
| D | Day |
| E | Time |
| F | Slot |
| G | Phase |
| H | Track |
| I | Focus |
| J | Practice Task |
| K | Gate |
| L | GitHub Doc URL |

`Plan ID` is the stable unique key. Example format: `W01D1S1`.

### 4.3 `Session Log` — observed columns `A:U`

| Column | Header | Write rule |
| --- | --- | --- |
| A | Plan ID | Stable key; never change during a normal record operation |
| B | Date | Preserve planned date unless explicitly correcting schedule |
| C | Week | Preserve |
| D | Day | Preserve |
| E | Time | Preserve |
| F | Phase | Preserve current plan phase |
| G | Track | Preserve current plan track |
| H | Planned Task | Preserve or source from matching `Daily Plan` |
| I | Status | Use exact enum below |
| J | Minutes | Learner-observed or timer-observed integer |
| K | Correctness 0-5 | Evidence-backed integer |
| L | Independence 0-5 | Interaction-backed or learner-declared integer |
| M | Tests 0-5 | Execution-evidence-backed integer |
| N | Explanation 0-5 | Evaluated from actual explanation |
| O | Review 0-5 | Active-recall evidence-backed integer |
| P | Energy 0-5 | Learner-reported integer |
| Q | Weighted Score | Formula-owned; do not write a guessed value |
| R | Evidence URL | Required for `Done` |
| S | Notes | Concise observed result, drift, or blocker |
| T | Next Action | One concrete repair, review, or advancement action |
| U | GitHub Doc URL | Canonical task or evidence document |

Observed formula pattern in column `Q`:

```text
=IF(I2<>"Done","",ROUND((K2*0.3+L2*0.2+M2*0.15+N2*0.15+O2*0.1+P2*0.1)/5*100,1))
```

The row number varies. Preserve the formula and ensure weights stay aligned with `Settings` and the scoring document.

### 4.4 `Exercise Log` — observed columns `A:P`

| Column | Header | Contract |
| --- | --- | --- |
| A | Exercise ID | Stable unique key, for example `EX-0001` |
| B | Date | Local date in `Asia/Taipei` |
| C | Type | LeetCode, Production Mini Lab, System Design, English, or an explicit registered type |
| D | Track | Pattern or capability family |
| E | Title | Human-readable exercise title |
| F | Pattern / Ability | Reusable trigger or capability |
| G | Stage | Exact enum below |
| H | Contract Passed | `Yes`, `No`, or `Partial` |
| I | Tests Passed | `Yes`, `No`, or `Partial` |
| J | Edge Cases | Current sheet contains descriptive text in existing rows; preserve existing content and validate before future schema migration |
| K | What-if Completed | `Yes`, `No`, or `Partial` |
| L | English Explanation | `Yes`, `No`, or `Partial` |
| M | Score | Exercise-level score; must be traceable to a rubric or session score |
| N | Next Review Date | Local date derived from the review algorithm |
| O | Memory Capsule URL | GitHub artifact URL |
| P | Notes | Evidence, first divergence, or migration note |

The observed `Edge Cases` column currently has a validation/content mismatch: existing descriptive text such as `Empty, single, duplicate, negative, no-solution` coexists with a `Yes/No/Partial` validation rule. Treat this as `schema_drift`. Do not overwrite descriptive evidence merely to satisfy the validation.

### 4.5 `GitHub Docs Index` — observed columns `A:D`

| Column | Header |
| --- | --- |
| A | Name |
| B | Path |
| C | GitHub URL |
| D | Purpose |

Path is the logical unique key. Add or update the index only after the GitHub file exists.

### 4.6 `Knowledge Index` — observed columns `A:G`

| Column | Header |
| --- | --- |
| A | Domain |
| B | Capability |
| C | Trigger Prompt / Signal |
| D | Primary Evidence Artifact |
| E | GitHub URL |
| F | Review Cadence |
| G | Status |

Observed `Status` enum:

- `Active`
- `Draft`
- `Archived`

## 5. State machines

### 5.1 Session status enum

Use exactly:

- `Planned`
- `In Progress`
- `Done`
- `Blocked`
- `Skipped`
- `Review`

Allowed transitions:

```text
Planned -> In Progress | Blocked | Skipped
In Progress -> Done | Blocked | Skipped
Blocked -> In Progress | Skipped
Done -> Review
Review -> In Progress | Done | Blocked
Skipped -> Planned   # explicit reschedule only
```

Rules:

- Do not transition directly from `Planned` to `Done` unless the same operation includes complete evidence and score inputs and the before/after receipt makes the combined transition explicit.
- A correction from `Done` to another state requires a reason and preserved prior value in the receipt.
- `Review` means previously completed work is due for active recall; it is not a substitute for a review result.

### 5.2 Exercise stage enum

Observed strict validation allows:

- `Concept`
- `Guided`
- `Independent`
- `Correctness Gate`
- `What-if`
- `7d Review`
- `Done`

Expected progression:

```text
Concept -> Guided -> Independent -> Correctness Gate -> What-if -> 7d Review -> Done
```

Regression is allowed when evidence requires repair:

```text
Independent -> Guided
Correctness Gate -> Independent | Guided
What-if -> Correctness Gate
7d Review -> Independent | Correctness Gate | What-if
Done -> 7d Review                # explicit reopened review only
```

Do not skip a stage merely because a solution looks familiar.

### 5.3 Existing stage drift

Some existing `Exercise Log` cells display `Planned`, although `Planned` is outside the observed strict validation list.

Interpretation rules:

- Read: classify the row as `schema_drift` and operationally `not started`.
- New write: do not write `Planned` into the Stage column.
- Repair: requires an explicit migration decision to either add `Planned` to validation or map legacy rows to `Concept`.
- Never silently normalize the cell during an unrelated update.

## 6. Stable keys and idempotency

### Stable keys

- Session plan and result: `Plan ID`.
- Exercise: `Exercise ID`.
- GitHub document index: repository `Path`.
- Knowledge entry: `Domain + Capability` unless a future schema introduces an explicit ID.
- GitHub artifact: normalized repository path plus commit SHA for a concrete version.

### Idempotent write algorithm

1. Read live metadata.
2. Read the header and the smallest range containing the expected key.
3. Confirm zero, one, or multiple matching rows.
4. If zero matches, append only when the operation is allowed to create that record.
5. If one matches, update only intended cells.
6. If multiple match, stop with `duplicate_key` and do not guess which row is canonical.
7. Re-read changed cells.
8. Return before/after values and provider revision or commit.

The idempotency key for a persistence request is:

```text
<target-system>:<stable-key>:<evidence-digest>:<operation-type>
```

A retried request with the same key must not create a second logical record.

## 7. Evidence model

### 7.1 Evidence maturity

- `unknown` — not observed and not disproven.
- `claimed` — asserted by a person, note, or model without direct verification.
- `observed` — directly read or captured, but not independently reproduced.
- `verified` — checked against a contract through tests, replay, review, or another independent mechanism.
- `contradicted` — two or more sources conflict.
- `blocked` — verification could not run because a named dependency or permission is missing.

Never convert `unknown` or `blocked` into `No`, `False`, `Absent`, or `Failed` without supporting evidence.

### 7.2 Evidence classes

| Class | Examples | What it can support |
| --- | --- | --- |
| Source | Repository file, official docs, specification, paper | What a source states |
| Static | Code path, type, schema, invariant, architecture graph | What is possible or required by structure |
| Execution | Test log, trace, benchmark, sandbox receipt | What occurred in that environment and version |
| Learner | Independent code, explanation, recall answer, self-report | Current learner performance under stated conditions |
| Review | Rubric-scored assessment, human approval, code review | A bounded judgment tied to evidence |
| Deployment/Production | Artifact-to-SHA mapping, deployment receipt, production observation | What version was deployed or observed in production |

Do not use static evidence to claim runtime execution. Do not use a local test to claim production behavior.

### 7.3 Evidence receipt

A significant result should be representable as:

```yaml
evidence_id: EV-YYYYMMDD-NNN
claim: "What this evidence supports"
kind: source | static | execution | learner | review | deployment | production
maturity: unknown | claimed | observed | verified | contradicted | blocked
locator:
  repository: ed3c/agent-architect-notes
  path: path/to/artifact.md
  commit_sha: full-sha-or-null
  sheet_tab: exact-tab-or-null
  stable_key: plan-or-exercise-id-or-null
  external_source: url-or-null
produced_at: ISO-8601-with-offset
contract: "Assertion or task contract used"
result: pass | partial | fail | blocked
assumptions:
  - explicit assumption
limitations:
  - known limit
redaction: none | applied
supersedes: prior-evidence-id-or-null
```

A Sheet row may store only the locator and summary; the long-form receipt belongs in GitHub when detail is needed.

## 8. Completion gate

A session may be `Done` only when all are true:

1. The planned task contract is known.
2. The result is supported by a GitHub, test, transcript, trace, or other durable evidence locator.
3. Correctness, Independence, Tests, Explanation, Review, and Energy are all known integers from `0` to `5`.
4. The evidence supports the stated score values.
5. `Evidence URL` is populated.
6. `Next Action` is concrete.
7. The write has been re-read successfully.

A topic-level gate additionally requires:

- Reconstruction without opening the answer.
- Stated invariant or business invariant.
- Tests or counterexamples.
- Complexity or system trade-offs.
- At least one what-if pivot.
- Traceable evidence URL.

## 9. Scoring contract

Use:

```text
Weighted Score =
(Correctness*0.30
 + Independence*0.20
 + Tests*0.15
 + Explanation*0.15
 + Review*0.10
 + Energy*0.10) / 5 * 100
```

### Evidence requirements by dimension

| Dimension | Minimum evidence |
| --- | --- |
| Correctness | Contract comparison plus code/design/output or counterexample analysis |
| Independence | Interaction history or explicit learner declaration of hints/tools used |
| Tests | Actual test output, manually verified cases, or a clearly labeled non-executed test design with a lower score |
| Explanation | Actual written or spoken answer |
| Review | Active-recall attempt before rereading |
| Energy | Learner self-report |

Do not infer Energy. Do not award full Tests credit for writing tests that were never run. Do not award full Independence after hidden hints or copied answers.

## 10. Adaptive review algorithm

Calculate dates in `Asia/Taipei` from the date of the evaluated attempt.

| Condition | Next action | Next review |
| --- | --- | --- |
| Contract broken, Correctness `0–1`, or first divergence unresolved | `repair` | `D+1` |
| Correctness or Tests `2`, or Weighted Score `<60` | targeted repair | `D+1` |
| Weighted Score `60–74.9` | guided recall | `D+2` |
| Weighted Score `75–84.9` | independent recall | `D+3` |
| Weighted Score `85–92.9` and Independence `>=4` | what-if recall | `D+7` |
| Weighted Score `>=93`, Independence `>=4`, Review `>=4` | transfer problem | `D+14` |
| Successful `D+14` transfer review | maintenance recall | `D+30` |

Reset rules:

- A failed review returns to the earliest failed stage and uses `D+1` or `D+2`.
- A review with new hints cannot preserve a prior full Independence rating for that attempt.
- Do not create duplicate review records for the same exercise and date.
- `Next Review Date` is a date, not proof that a scheduler or notification was created.

## 11. Interview gates

### Micro interview drills

Allowed from the beginning:

- One what-if question.
- One 3–5 sentence English explanation.
- One trade-off or counterexample question.

### Full English-only mock

All conditions are required:

1. The first two weeks are completed or explicitly waived for a diagnostic mock.
2. Two consecutive relevant sessions have evidence URLs.
3. Both sessions have Correctness `>=4` and Independence `>=4`.
4. Explanation is `>=3` in both sessions.
5. No unresolved correctness blocker exists for the mock's core domain.
6. The mock type, duration, rubric, stop condition, and recording policy are stated before starting.

If the gate fails, return a smaller English drill and list the missing gate evidence.

## 12. GitHub artifact contract

A normal learning artifact includes:

- Stable Plan or Exercise ID.
- Date and mode.
- Trigger and task contract.
- Assumptions.
- Work or answer.
- Evidence locator or reproducible command.
- Result and known limits.
- First divergence or blocker.
- Score evidence when evaluated.
- Next action and review date.

Use repository-relative paths in documents. Do not include local absolute paths such as `/Users/...` as required dependencies.

Corrections should add `Supersedes`, `Revises`, or a clear change history rather than deleting a prior claim without trace.

## 13. Sheet write protocol

Before any Sheet write:

1. Confirm the exact spreadsheet ID.
2. Read metadata and exact tab title.
3. Read the target header and keyed row.
4. Inspect formulas, validation, hyperlinks, and neighboring constraints.
5. Compute the smallest cell patch.
6. Reject duplicate keys or ambiguous ranges.
7. Write only after the user requested recording or execution.
8. Re-read the changed cells.
9. Return a persistence receipt.

Do not:

- Guess a tab name.
- Scan an unbounded grid.
- Rewrite an entire row when two cells are changing.
- Replace formula cells with literal values.
- Convert legacy drift during an unrelated task.
- Claim success from a prepared request body alone.

## 14. Conflict and drift handling

Use these error classes:

- `state_unavailable` — live source could not be read.
- `duplicate_key` — multiple rows match a stable key.
- `schema_drift` — value, header, formula, or validation differs from the current contract.
- `evidence_missing` — requested completion lacks a durable locator.
- `score_incomplete` — one or more score inputs are unknown.
- `write_conflict` — live value changed after the read.
- `permission_blocked` — connector or repository permission is insufficient.
- `source_contradiction` — two sources support incompatible claims.

For each error, return:

- Observed facts.
- Exact locator.
- Operation that was not performed.
- Safest next action.

## 15. Persistence receipt

```yaml
target_system: github | google_sheets
stable_key: W01D1S1 | EX-0001 | repository/path
operation: create | update | no-op | blocked
before_state: {}
after_state: {}
paths_or_ranges:
  - exact/path/or/range
evidence_urls:
  - durable-locator
commit_or_revision: provider-returned-id-or-null
validation_result: pass | partial | fail | blocked
unresolved_drift:
  - drift-or-empty
```

A receipt with `commit_or_revision: null` cannot report a successful provider write.

## 16. Privacy and redaction

- Keep the repository private unless the user explicitly changes visibility.
- Never store API keys, access tokens, OAuth codes, raw credentials, or secret-bearing environment files.
- Redact personal or production data before creating evidence artifacts.
- Prefer hashes, synthetic examples, bounded excerpts, and provenance metadata over raw logs.
- A redacted artifact must say that redaction was applied and what evidence class remains valid.
