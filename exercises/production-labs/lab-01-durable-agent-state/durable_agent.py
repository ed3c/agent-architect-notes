"""Minimal durable-agent state machine used by the learning lab."""

from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Protocol


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
    pending_effects: dict[str, dict[str, Any]] = field(default_factory=dict)
    completed_effects: dict[str, Any] = field(default_factory=dict)
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
        elif event.kind == "effect_planned":
            effect_id = str(event.data["effect_id"])
            state.pending_effects[effect_id] = dict(event.data["payload"])
        elif event.kind == "effect_completed":
            effect_id = str(event.data["effect_id"])
            state.pending_effects.pop(effect_id, None)
            state.completed_effects[effect_id] = event.data["result"]
        else:
            raise ValueError(f"unsupported event kind: {event.kind}")

        state.seen_event_ids.add(event.event_id)
        applied_events += 1

    return ReplayResult(state=state, applied_events=applied_events)


class EffectPort(Protocol):
    def execute(self, idempotency_key: str, payload: Mapping[str, Any]) -> Any: ...


class InMemoryEventStore:
    def __init__(self) -> None:
        self._events: list[Event] = []

    def append(self, event: Event) -> None:
        self._events.append(event)

    def read_all(self) -> tuple[Event, ...]:
        return tuple(self._events)


class SimulatedCrash(RuntimeError):
    """Raised by the lab at a deliberate crash boundary."""


class DurableRunner:
    def __init__(self, store: InMemoryEventStore, effect_port: EffectPort) -> None:
        self._store = store
        self._effect_port = effect_port

    def execute_effect(
        self,
        effect_id: str,
        payload: Mapping[str, Any],
        *,
        crash_after_effect: bool = False,
    ) -> Any:
        self._store.append(
            Event(
                event_id=f"plan:{effect_id}",
                kind="effect_planned",
                data={"effect_id": effect_id, "payload": dict(payload)},
            )
        )
        result = self._effect_port.execute(effect_id, payload)
        if crash_after_effect:
            raise SimulatedCrash("crashed after effect and before completion record")
        self._record_completion(effect_id, result)
        return result

    def resume_pending_effects(self) -> None:
        pending = replay(self._store.read_all()).state.pending_effects
        for effect_id, payload in pending.items():
            result = self._effect_port.execute(effect_id, payload)
            self._record_completion(effect_id, result)

    def _record_completion(self, effect_id: str, result: Any) -> None:
        self._store.append(
            Event(
                event_id=f"complete:{effect_id}",
                kind="effect_completed",
                data={"effect_id": effect_id, "result": result},
            )
        )
