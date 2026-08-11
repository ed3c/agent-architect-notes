# GitHub Delivery Receipt

`prompt-library` Line 使用 [Project #4](https://github.com/users/ed3c/projects/4) 作為
Scope Projection：

- PRD：[Issue #8](https://github.com/ed3c/agent-architect-notes/issues/8)
- Slices：[Issue #9](https://github.com/ed3c/agent-architect-notes/issues/9)、
  [Issue #10](https://github.com/ed3c/agent-architect-notes/issues/10)
- Delivery PRs：[PR #11](https://github.com/ed3c/agent-architect-notes/pull/11)、
  [PR #12](https://github.com/ed3c/agent-architect-notes/pull/12)、
  [PR #13](https://github.com/ed3c/agent-architect-notes/pull/13)（Receipt 與 PRD Closure）

## Multi-PRD Scope Limitation

`github-delivery-loop` v1 的 Live Sync 會把釘選 PRD 以外的所有 Repository Issues 都寫入
`issue_urls`，不會按 `Part of #N` 或 GitHub Project Items 篩選。此 Repository 同時有
PRD #1 與 PRD #8，因此未校正的 Sync 會把 #1–#7 錯列為 `prompt-library` Slices。

本 Line 的 Receipt 已依 2026-08-11T15:36:33Z 回讀的 Project #4 Live Items 校正為
#9–#10。Repository-wide Metrics／Publication 保留原始輸出，因此其
`open-delivery-slices` 只表示另一條 PRD 尚未完成，不阻止 #8 的 Line Completion。

未來每次 Live Sync 後都必須：

1. 回讀 `gh project item-list 4 --owner ed3c --format json`。
2. 確認 Project 只有 #8、#9、#10，且 #9／#10 為 `Done`。
3. 確認 Receipt 的 `prd_issue_url` 是 #8，`issue_urls` 只有 #9／#10，`pr_urls` 只有
   #11／#12／#13。
4. 執行 Zero-network Gate：
   `python3 <github-delivery-loop>/scripts/github_delivery.py check --registry .github-delivery/registry.json`。

在 Shared Skill 原生支援 Multi-PRD Line Scope 前，不得把未校正的 Repository-wide
`issue_urls` 當成本 Line Receipt。
