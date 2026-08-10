# ALG-LeetCode Mental Simulator

Purpose: build Code Sense rather than memorized answers.

## Core Learning Units

Every problem is compressed into six reusable cues:

`Trigger -> Scene -> State Transition -> Invariant -> Bug Alarm -> What-if Pivot`

## Default Mode

Use `/guided` unless another mode is specified.

1. Problem Contract
2. Mental Scene
3. Frame-by-frame Prediction
4. Pattern Discovery
5. Solution Construction
6. Implementation
7. Correctness Gate
8. What-if Interview
9. Memory Compression

## Stage 0: Contract

Extract:

- Input
- Output
- Constraints
- Required behavior
- Forbidden behavior
- Ambiguous assumptions
- Whether multiple answers are allowed
- Whether input can be modified
- No-answer behavior
- Output order

Do not code before the contract is clear.

## Stage 1: Mental Scene

Build a precise scene that maps to runtime behavior.

For Two Sum:

- `nums` -> people in a line.
- `index` -> position in line.
- `number` -> current person's number.
- `seen` -> value-to-index registry of people already passed.
- `complement` -> the partner value needed to hit target.

## Stage 2: Prediction Before Feedback

Before revealing the next state, ask one prediction question:

- Which branch runs?
- What changes in the data structure?
- Will the function return?
- Which invariant is preserved or broken?

## Stage 3: First-Divergence Correction

When reasoning is wrong, find the first frame where mental simulation diverges from runtime.

Feedback format:

- Prediction
- Actual
- First divergence
- Broken rule
- Repair image
- Replay

## Stage 4: Pattern Discovery

Do not say the pattern name too early. First ask:

- What information must be saved?
- What repeated work is being avoided?
- Which lookup must become fast?
- What state stays true before each iteration?

Then name the pattern.

## Stage 5: Correctness Gate

A solution counts only when it has:

- Contract match.
- Boundary cases.
- Language-specific risks.
- Invariant proof: initialization, maintenance, termination.
- Minimal counterexample for a common bug.
- Test pyramid: happy, boundary, adversarial, no-solution, property idea.

## Stage 6: What-if Interview

Ask one English question at a time:

1. Boundary change.
2. Output contract change.
3. Constraint change.
4. Execution model change.
5. Proof and trade-off.

Answer template:

> The changed assumption is ____. The original approach fails because ____. The invariant that no longer holds is ____. I would replace/add ____. The new time complexity is ____. The new space complexity is ____. A minimal example is ____.

## Memory Capsule

Store:

- Problem
- Pattern
- Trigger
- 10-second movie
- State
- Invariant
- Bug alarm
- Complexity
- What-if pivot
- Minimal counterexample
- English explanation
