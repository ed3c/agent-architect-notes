# Two Sum First Task

Do this before any full mock interview.

## Function

```python
def two_sum(nums: list[int], target: int) -> tuple[int, int] | None:
    """
    Return the indices of two distinct elements whose values add up to target.
    Return None when no valid pair exists.
    """
```

## Required Tests

| nums | target | Expected |
| --- | ---: | --- |
| `[2, 7, 11, 15]` | 9 | `(0, 1)` |
| `[3, 3]` | 6 | `(0, 1)` |
| `[-3, 4, 3, 90]` | 0 | `(0, 2)` |
| `[]` | 10 | `None` |
| `[1]` | 1 | `None` |
| `[1, 2, 3]` | 100 | `None` |

## Mental Scene

`seen` is a registry of values already passed. For each current number, compute the partner value needed to reach `target`. If the partner is already in the registry, return the stored index and the current index.

## Core Invariant

Before processing `nums[index]`, `seen` contains only values from indices `< index`.

This invariant prevents using the same element twice.

## Bug Alarm

If the code writes `seen[number] = index` before checking the complement, duplicate/self-pair bugs can appear in variants.

## English Explanation Prompt

Keep it under two minutes:

1. My approach.
2. The invariant.
3. Time complexity.
4. Space complexity.
5. Edge cases.

## Completion Checklist

- Implementation completed.
- Six required tests pass.
- At least one duplicate-value case explained.
- No-answer behavior returns `None`.
- English explanation recorded or written.
- Sheet `Session Log` row marked `Done` and scored.
