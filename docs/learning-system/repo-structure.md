# Repository Structure

```text
agent-architect-notes/
  README.md
  docs/
    learning-system/
      README.md
      daily-cadence.md
      roadmap-28-weeks.md
      dashboard-scoring.md
      sheet-schema.md
      leetcode-alg-mental-simulator.md
      first-two-weeks.md
      knowledge-index.md
      repo-structure.md
      agent-architect-capstone.md
      exercises/
        two-sum-first-task.md
    kb/
      python-interview-foundation.md
      production-live-coding.md
      system-design-index.md
      agent-architecture-index.md
      evals-security-observability.md
    templates/
      daily-session-note.md
      exercise-memory-capsule.md
      system-design-note.md
      adr-template.md
      postmortem-template.md
    adr/
    postmortems/
    eval-reports/
    benchmark-results/
  exercises/
    leetcode/
    production-labs/
    system-design/
    english/
  capstone/
    skill-registry/
    execution-harness/
    agent-runtime/
    eval-platform/
    observability/
    security/
```

## Data Flow

1. Sheet schedules a session.
2. Session produces evidence.
3. Evidence is saved as code, note, test output, or memory capsule.
4. Sheet stores status, score, and evidence URL.
5. GitHub stores long-form knowledge and reusable templates.

## File Naming

- LeetCode notes: `exercises/leetcode/lc-0001-two-sum.md`
- Production labs: `exercises/production-labs/lab-01-defensive-json-ingestion.md`
- System design notes: `exercises/system-design/sd-01-rate-limiter.md`
- English drills: `exercises/english/e-001-coding-explanation.md`
- ADRs: `docs/adr/adr-0001-title.md`
- Postmortems: `docs/postmortems/YYYY-MM-DD-topic.md`
