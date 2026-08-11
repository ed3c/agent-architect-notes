import unittest

from durable_agent import (
    DurableRunner,
    Event,
    InMemoryEventStore,
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


if __name__ == "__main__":
    unittest.main()
