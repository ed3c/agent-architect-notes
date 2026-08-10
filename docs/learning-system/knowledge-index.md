# Knowledge Index

This is the GitHub source of truth behind the Google Sheets Knowledge Index tab.

## Domains

| Domain | Trigger | Primary File |
| --- | --- | --- |
| Python 3 | Need fast syntax-free coding | `docs/kb/python-interview-foundation.md` |
| DSA | New LeetCode problem or code review | `docs/learning-system/leetcode-alg-mental-simulator.md` |
| Testing | Correctness or BugFree review | `docs/learning-system/dashboard-scoring.md` |
| Production Coding | API, async, retry, queue, cache, logging | `docs/kb/production-live-coding.md` |
| System Design | 45-60 minute architecture prompt | `docs/kb/system-design-index.md` |
| Agent Architecture | State, memory, termination, tool gateway | `docs/kb/agent-architecture-index.md` |
| Evals | Dataset, grader, regression threshold | `docs/kb/evals-security-observability.md` |
| Security | Tool use, prompt injection, sandbox, RBAC | `docs/kb/evals-security-observability.md` |
| English Interview | Explanation, deep dive, behavioral | `docs/learning-system/roadmap-28-weeks.md` |
| Portfolio | SKILL.md / MCP / Skill Arena capstone | `docs/learning-system/agent-architect-capstone.md` |

## Indexing Rule

Each new note should include:

- Problem or design trigger.
- Source or evidence path.
- Current stage.
- What changed in the learner's mental model.
- Next active recall date.

## Retrieval Rule

When a new task arrives, choose the smallest relevant file first. Do not load the whole repository unless the task crosses multiple domains.
