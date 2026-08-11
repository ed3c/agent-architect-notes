"""Minimal durable-agent state machine used by the learning lab."""

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Iterable, Mapping, Protocol


SNAPSHOT_SCHEMA_VERSION = 1


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
    max_iterations: int | None = None
    max_budget: int | None = None
    terminated: bool = False
    termination_reason: str | None = None
    pending_effects: dict[str, dict[str, Any]] = field(default_factory=dict)
    completed_effects: dict[str, Any] = field(default_factory=dict)
    seen_event_ids: set[str] = field(default_factory=set)


@dataclass(frozen=True)
class ReplayResult:
    state: AgentState
    applied_events: int


@dataclass(frozen=True)
class Snapshot:
    schema_version: int
    last_event_offset: int
    state_json: str
    checksum: str


def replay(events: Iterable[Event]) -> ReplayResult:
    return _replay_from(AgentState(), events)


def _replay_from(state: AgentState, events: Iterable[Event]) -> ReplayResult:
    applied_events = 0

    for event in events:
        if event.event_id in state.seen_event_ids:
            continue

        if event.kind == "run_started":
            state.run_id = str(event.data["run_id"])
            if "max_iterations" in event.data:
                state.max_iterations = int(event.data["max_iterations"])
            if "max_budget" in event.data:
                state.max_budget = int(event.data["max_budget"])
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
        elif event.kind == "run_terminated":
            state.terminated = True
            state.termination_reason = str(event.data["reason"])
        else:
            raise ValueError(f"unsupported event kind: {event.kind}")

        state.seen_event_ids.add(event.event_id)
        applied_events += 1

    return ReplayResult(state=state, applied_events=applied_events)


def create_snapshot(events: Iterable[Event]) -> Snapshot:
    event_list = list(events)
    state_json = _serialize_state(replay(event_list).state)
    return Snapshot(
        schema_version=SNAPSHOT_SCHEMA_VERSION,
        last_event_offset=len(event_list),
        state_json=state_json,
        checksum=hashlib.sha256(state_json.encode("utf-8")).hexdigest(),
    )


def replay_with_snapshot(
    events: Iterable[Event], snapshot: Snapshot | None
) -> ReplayResult:
    event_list = list(events)
    if snapshot is None:
        return replay(event_list)
    if snapshot.schema_version != SNAPSHOT_SCHEMA_VERSION:
        return replay(event_list)
    actual_checksum = hashlib.sha256(snapshot.state_json.encode("utf-8")).hexdigest()
    if actual_checksum != snapshot.checksum:
        return replay(event_list)
    state = _deserialize_state(snapshot.state_json)
    return _replay_from(state, event_list[snapshot.last_event_offset :])


def _serialize_state(state: AgentState) -> str:
    payload = {
        "completed_effects": state.completed_effects,
        "iteration": state.iteration,
        "max_budget": state.max_budget,
        "max_iterations": state.max_iterations,
        "pending_effects": state.pending_effects,
        "run_id": state.run_id,
        "seen_event_ids": sorted(state.seen_event_ids),
        "spent": state.spent,
        "terminated": state.terminated,
        "termination_reason": state.termination_reason,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"))


def _deserialize_state(state_json: str) -> AgentState:
    payload = json.loads(state_json)
    return AgentState(
        run_id=payload["run_id"],
        iteration=int(payload["iteration"]),
        spent=int(payload["spent"]),
        max_iterations=payload["max_iterations"],
        max_budget=payload["max_budget"],
        terminated=bool(payload["terminated"]),
        termination_reason=payload["termination_reason"],
        pending_effects=dict(payload["pending_effects"]),
        completed_effects=dict(payload["completed_effects"]),
        seen_event_ids=set(payload["seen_event_ids"]),
    )


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


class RunTerminated(RuntimeError):
    """Raised when a persisted run limit prevents another iteration."""


class RunController:
    def __init__(self, store: InMemoryEventStore) -> None:
        self._store = store

    @classmethod
    def start(
        cls,
        store: InMemoryEventStore,
        *,
        run_id: str,
        max_iterations: int,
        max_budget: int,
    ) -> "RunController":
        store.append(
            Event(
                event_id=f"run:{run_id}:started",
                kind="run_started",
                data={
                    "run_id": run_id,
                    "max_iterations": max_iterations,
                    "max_budget": max_budget,
                },
            )
        )
        return cls(store)

    def record_iteration(self, *, cost: int) -> None:
        state = replay(self._store.read_all()).state
        if state.terminated:
            raise RunTerminated(str(state.termination_reason))
        if state.max_iterations is not None and state.iteration >= state.max_iterations:
            self._terminate(state, "max_iterations")
        if state.max_budget is not None and state.spent + cost > state.max_budget:
            self._terminate(state, "max_budget")

        self._store.append(
            Event(
                event_id=f"run:{state.run_id}:iteration:{state.iteration + 1}",
                kind="iteration_recorded",
                data={"cost": cost},
            )
        )

    def _terminate(self, state: AgentState, reason: str) -> None:
        self._store.append(
            Event(
                event_id=f"run:{state.run_id}:terminated:{reason}",
                kind="run_terminated",
                data={"reason": reason},
            )
        )
        raise RunTerminated(reason)


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
