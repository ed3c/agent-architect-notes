"""Minimal durable-agent state machine used by the learning lab."""

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping


@dataclass(frozen=True)
class Event:
    event_id: str
    kind: str
    data: Mapping[str, Any]


@dataclass
class AgentState:
    run_id: str | None = None
    iteration: int = 0
    spent: int = 0
    seen_event_ids: set[str] = field(default_factory=set)


@dataclass(frozen=True)
class ReplayResult:
    state: AgentState
    applied_events: int


def replay(events: Iterable[Event]) -> ReplayResult:
    state = AgentState()
    applied_events = 0

    for event in events:
        if event.event_id in state.seen_event_ids:
            continue

        if event.kind == "run_started":
            state.run_id = str(event.data["run_id"])
        elif event.kind == "iteration_recorded":
            state.iteration += 1
            state.spent += int(event.data["cost"])
        else:
            raise ValueError(f"unsupported event kind: {event.kind}")

        state.seen_event_ids.add(event.event_id)
        applied_events += 1

    return ReplayResult(state=state, applied_events=applied_events)
