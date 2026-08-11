# prompt-library delivery dashboard

> Snapshot: `2026-08-11T15:36:33Z`。本頁是 GitHub event truth 的時間點快照，
> 不是 registry 的第二份真相，也不是個人生產力排名。

> Scope note: `github-delivery-loop` v1 的 Metrics／Publication 是 Repository-wide，
> 因此下方仍列出另一條 PRD #1 與 Issues #2–#7。`prompt-library` Line Receipt 則依
> Project #4 的 Live Items 限定為 PRD #8 與 Slices #9–#10；`open-delivery-slices`
> 是 Repository Publication Blocker，不代表 Prompt Library Slice 未完成。

## Truth boundary

```text
┌───────────────┐    ┌──────────────┐    ┌────────────────────────┐
│ GitHub events │ ─→ │ metrics.json │ ─→ │ Markdown decision view │
└───────────────┘    └──────────────┘    └────────────────────────┘
         │
         ├─→ GitHub Project (status projection only)
         └─→ publication attestation ─→ human visibility gate
```

## Current decision

- Repository: `ed3c/agent-architect-notes` (`PRIVATE`)
- Remote tree: `6e726207e9efc368e93dcc2d2381084955a70071` (33 files, orphan root: `YES`)
- Public ready: `NO`
- Blockers: `license-missing, open-delivery-slices, human-visibility-gate`
- Project: [Agent Architect Prompt Library Delivery](https://github.com/users/ed3c/projects/4)

## Flow health

| Signal | Value |
|---|---:|
| accepted slices | 2 |
| WIP | 0 |
| blocked | 0 |
| throughput 7d / 28d | 2 / 2 |
| closed_without_merge | 0 |

## Project projection

| Status | Items |
|---|---:|
| Done | 2 |
| Todo | 1 |

`closed_without_merge` 是證據缺口，不計入 throughput。p50/p85 只在有 merge event 樣本時顯示。

## Slice evidence

| Issue | State | Started PR | Accepted PR | Lead | Blocked |
|---:|---|---:|---:|---:|---:|
| #1 | OPEN | — | — | UNKNOWN | 0 |
| #2 | OPEN | — | — | UNKNOWN | 0 |
| #3 | OPEN | — | — | UNKNOWN | 0 |
| #4 | OPEN | — | — | UNKNOWN | 0 |
| #5 | OPEN | — | — | UNKNOWN | 0 |
| #6 | OPEN | — | — | UNKNOWN | 0 |
| #7 | OPEN | — | — | UNKNOWN | 0 |
| #9 | CLOSED | 11 | 11 | 1113 | 0 |
| #10 | CLOSED | 12 | 12 | 1633 | 0 |

## Human gate

只有 blockers 清空、publication attestation 與遠端 HEAD 對齊後，人類才可執行 PR merge 與 PRIVATE→PUBLIC。

## MVP extraction

| Step | Direct? | Undecided dependency | Permission | Measurable change | Size |
|---|---|---|---|---|---|
| Clear mechanical blockers | direct | none | repository scope | blockers count decreases | small |
| Human visibility decision | direct | owner review | owner only | visibility becomes PUBLIC | human gate |

Rejected now: custom daemon (extra operational surface); personal ranking (Goodhart risk); automatic merge/public toggle (violates human gate).
