# Agent Architect Notes

Private knowledge base and learning control plane for transitioning from senior software engineering into Agentic AI Systems.

## Control Plane

- Google Sheets dashboard: https://docs.google.com/spreadsheets/d/1cd-TL6N2_PD-EktZqZOafRsdCd-BZFOJO-ww3kYWnsA
- Daily cadence: `09:00 -> 14:00 -> 19:00` in `Asia/Taipei`.
- Role positioning: **Senior Software Engineer transitioning into Agentic AI Systems**.
- Primary route: Python 3 + DSA + Testing as the interview floor; Production Agent Systems + Evals + Security + System Design as the hiring ceiling.

## Agent Integration

Start here when Codex, Claude Code, or another learning agent operates on this repository:

- [Canonical Agent Instructions](AGENTS.md)
- [Claude Code Adapter](CLAUDE.md)
- [Integration Architecture and Requirements](docs/agent-integration/README.md)
- [Canonical Learning Orchestrator System Prompt](docs/agent-integration/SYSTEM_PROMPT.md)
- [Prompt Intent Classifier System Prompt](docs/agent-integration/PROMPT_CLASSIFIER_SYSTEM_PROMPT.md)
- [Context Routing Contract](docs/agent-integration/CONTEXT_ROUTING.md)
- [State and Evidence Contract](docs/agent-integration/STATE_EVIDENCE_CONTRACT.md)
- [Prompt Playbook](docs/agent-integration/PROMPT_PLAYBOOK.md)
- [Integration Qualification Tests](docs/agent-integration/INTEGRATION_TESTS.md)

The agent integration layer turns live learning state into a bounded task contract, protects Guided and Independent modes, requires evidence before completion, records long-form artifacts in GitHub, updates execution state in Google Sheets only when authorized, and schedules capability-based review.

## Main Index

- [Learning System](docs/learning-system/README.md)
- [Daily Cadence](docs/learning-system/daily-cadence.md)
- [28-Week Roadmap](docs/learning-system/roadmap-28-weeks.md)
- [Dashboard Scoring](docs/learning-system/dashboard-scoring.md)
- [Sheet Schema](docs/learning-system/sheet-schema.md)
- [ALG-LeetCode Mental Simulator](docs/learning-system/leetcode-alg-mental-simulator.md)
- [First Two Weeks](docs/learning-system/first-two-weeks.md)
- [Two Sum First Task](docs/learning-system/exercises/two-sum-first-task.md)
- [Knowledge Index](docs/learning-system/knowledge-index.md)
- [Prompt 分類法則](docs/learning-system/prompt-classification-rules.md)
- [Discord 可複製 Prompt 目錄](docs/learning-system/discord-prompt-catalog.md)
- [Repository Structure](docs/learning-system/repo-structure.md)
- [Agent Architect Capstone](docs/learning-system/agent-architect-capstone.md)

## Knowledge Base

- [Python Interview Foundation](docs/kb/python-interview-foundation.md)
- [Production Live Coding](docs/kb/production-live-coding.md)
- [System Design Index](docs/kb/system-design-index.md)
- [Agent Architecture Index](docs/kb/agent-architecture-index.md)
- [Durable Agent State：Replay、Snapshot、Resume](docs/kb/durable-agent-state.md)
- [Zero-trust Agent Sandbox：Isolation、Egress、Cleanup](docs/kb/zero-trust-agent-sandbox.md)
- [Evals, Security, Observability](docs/kb/evals-security-observability.md)

## Qualified Learning Units

- [LAB-AA-01：Durable Agent State](exercises/production-labs/lab-01-durable-agent-state/README.md)
- [SD-AA-01：Durable Agent Orchestrator](exercises/system-design/sd-01-durable-agent-orchestrator.md)
- [ADR-0001：Durable Agent Recovery Hybrid](docs/adr/adr-0001-durable-agent-recovery-hybrid.md)
- [LAB-AA-02：Zero-trust Agent Code Sandbox](exercises/production-labs/lab-02-zero-trust-sandbox/README.md)
- [SD-AA-02：Zero-trust Agent Code Execution](exercises/system-design/sd-02-zero-trust-agent-code-sandbox.md)

## Templates

- [Daily Session Note](docs/templates/daily-session-note.md)
- [Exercise Memory Capsule](docs/templates/exercise-memory-capsule.md)
- [System Design Note](docs/templates/system-design-note.md)
- [ADR Template](docs/templates/adr-template.md)
- [Postmortem Template](docs/templates/postmortem-template.md)

## Operating Rule

Google Sheets records execution, score, status, and evidence links. GitHub stores all long-form notes, exercise instructions, knowledge indexes, templates, integration contracts, system prompts, and portfolio architecture documents. Sheet document URLs should point back to this repository rather than Google Docs.
