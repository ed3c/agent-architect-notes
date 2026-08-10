# Dashboard Scoring

The Dashboard turns learning into observable behavior. Do not score by hours alone.

## Session Score Formula

`Weighted Score = (Correctness*0.30 + Independence*0.20 + Tests*0.15 + Explanation*0.15 + Review*0.10 + Energy*0.10) / 5 * 100`

| Dimension | Weight | 5 = Strong | 3 = Acceptable | 1 = Needs Repair |
| --- | ---: | --- | --- | --- |
| Correctness | 30% | Contract matched, edge cases handled, no known counterexample. | Main cases pass, minor risk. | Contract breaks or wrong output. |
| Independence | 20% | No hints or copied answer; can reconstruct from state. | Small hints used. | Depends on solution/template. |
| Tests | 15% | Happy, boundary, adversarial, no-solution, property idea. | Main + one edge. | No meaningful tests. |
| Explanation | 15% | Clear English approach, invariant, complexity, edge cases. | Understandable but incomplete. | Cannot explain reasoning. |
| Review | 10% | Memory capsule and active recall completed. | Partial review. | Only rereads answer. |
| Energy | 10% | Sustainable focus and clean next action. | Moderate. | Burnout or no next action. |

## Dashboard KPIs

- Total planned sessions.
- Done sessions.
- Completion rate.
- Average weighted score.
- Total minutes.
- 7-day completion rate.
- LeetCode Independent+ count.
- LeetCode Correctness Gate+ count.
- Production labs done.
- System design notes done.
- English drills done.

## Gate Interpretation

`Foundation Gate On Track` requires strong completion and quality indicators. A low score is not failure; it is a repair signal. The next session should attack the first broken dimension rather than repeat the whole topic.

## Correctness Wording

Never claim absolute BugFree. Use:

> Correct under the stated contract and assumptions.

Then list the contract, invariant, edge cases, and known limits.
