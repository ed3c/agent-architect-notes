import unittest
from dataclasses import replace

from durable_agent import (
    create_snapshot,
    DurableRunner,
    Event,
    InMemoryEventStore,
    RunController,
    RunTerminated,
    replay_with_snapshot,
    SimulatedCrash,
    replay,
)


class RecordingIdempotentEffectPort:
    def __init__(self):
        self._results = {}
        self.calls = 0
        self.applications = 0

    def execute(self, idempotency_key, payload):
        self.calls += 1
        if idempotency_key not in self._results:
            self.applications += 1
            self._results[idempotency_key] = {"accepted": payload["message"]}
        return self._results[idempotency_key]


class ReplayContractTests(unittest.TestCase):
    def test_duplicate_event_id_is_applied_once(self):
        events = [
            Event("event-1", "run_started", {"run_id": "run-1"}),
            Event("event-2", "iteration_recorded", {"cost": 3}),
            Event("event-2", "iteration_recorded", {"cost": 3}),
        ]

        result = replay(events)

        self.assertEqual(result.state.run_id, "run-1")
        self.assertEqual(result.state.iteration, 1)
        self.assertEqual(result.state.spent, 3)
        self.assertEqual(result.applied_events, 2)

    def test_snapshot_plus_tail_matches_full_replay_with_less_replay_work(self):
        events = [
            Event("event-1", "run_started", {"run_id": "run-1"}),
            Event("event-2", "iteration_recorded", {"cost": 2}),
            Event("event-3", "iteration_recorded", {"cost": 3}),
            Event("event-4", "iteration_recorded", {"cost": 5}),
            Event("event-5", "iteration_recorded", {"cost": 8}),
        ]
        snapshot = create_snapshot(events[:3])

        full_replay = replay(events)
        snapshot_replay = replay_with_snapshot(events, snapshot)

        self.assertEqual(snapshot_replay.state, full_replay.state)
        self.assertEqual(full_replay.applied_events, 5)
        self.assertEqual(snapshot_replay.applied_events, 2)

    def test_corrupt_snapshot_falls_back_to_full_replay(self):
        events = [
            Event("event-1", "run_started", {"run_id": "run-1"}),
            Event("event-2", "iteration_recorded", {"cost": 2}),
            Event("event-3", "iteration_recorded", {"cost": 3}),
        ]
        snapshot = create_snapshot(events[:2])
        corrupt_snapshot = replace(
            snapshot,
            state_json=snapshot.state_json.replace('"spent":2', '"spent":999'),
        )

        result = replay_with_snapshot(events, corrupt_snapshot)

        self.assertEqual(result.state, replay(events).state)
        self.assertEqual(result.applied_events, 3)

    def test_missing_snapshot_falls_back_to_full_replay(self):
        events = [
            Event("event-1", "run_started", {"run_id": "run-1"}),
            Event("event-2", "iteration_recorded", {"cost": 2}),
        ]

        result = replay_with_snapshot(events, None)

        self.assertEqual(result.state, replay(events).state)
        self.assertEqual(result.applied_events, 2)

    def test_unknown_snapshot_schema_falls_back_to_full_replay(self):
        events = [
            Event("event-1", "run_started", {"run_id": "run-1"}),
            Event("event-2", "iteration_recorded", {"cost": 2}),
            Event("event-3", "iteration_recorded", {"cost": 3}),
        ]
        future_snapshot = replace(create_snapshot(events[:2]), schema_version=2)

        result = replay_with_snapshot(events, future_snapshot)

        self.assertEqual(result.state, replay(events).state)
        self.assertEqual(result.applied_events, 3)


class EffectBoundaryContractTests(unittest.TestCase):
    def test_resume_deduplicates_effect_after_crash_before_completion_record(self):
        store = InMemoryEventStore()
        effect_port = RecordingIdempotentEffectPort()
        runner = DurableRunner(store, effect_port)

        with self.assertRaises(SimulatedCrash):
            runner.execute_effect(
                effect_id="effect-1",
                payload={"message": "send once"},
                crash_after_effect=True,
            )

        DurableRunner(store, effect_port).resume_pending_effects()
        state = replay(store.read_all()).state

        self.assertEqual(effect_port.calls, 2)
        self.assertEqual(effect_port.applications, 1)
        self.assertEqual(state.pending_effects, {})
        self.assertEqual(
            state.completed_effects["effect-1"], {"accepted": "send once"}
        )


class TerminationContractTests(unittest.TestCase):
    def test_max_iteration_limit_persists_terminal_state(self):
        store = InMemoryEventStore()
        controller = RunController.start(
            store,
            run_id="run-1",
            max_iterations=2,
            max_budget=100,
        )
        controller.record_iteration(cost=1)
        controller.record_iteration(cost=1)

        with self.assertRaisesRegex(RunTerminated, "max_iterations"):
            RunController(store).record_iteration(cost=1)

        state = replay(store.read_all()).state
        self.assertEqual(state.iteration, 2)
        self.assertTrue(state.terminated)
        self.assertEqual(state.termination_reason, "max_iterations")

    def test_budget_limit_rejects_iteration_before_overspend(self):
        store = InMemoryEventStore()
        controller = RunController.start(
            store,
            run_id="run-1",
            max_iterations=10,
            max_budget=5,
        )
        controller.record_iteration(cost=4)

        with self.assertRaisesRegex(RunTerminated, "max_budget"):
            RunController(store).record_iteration(cost=2)

        state = replay(store.read_all()).state
        self.assertEqual(state.iteration, 1)
        self.assertEqual(state.spent, 4)
        self.assertTrue(state.terminated)
        self.assertEqual(state.termination_reason, "max_budget")


if __name__ == "__main__":
    unittest.main()
