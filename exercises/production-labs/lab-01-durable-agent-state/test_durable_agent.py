import unittest

from durable_agent import Event, replay


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


if __name__ == "__main__":
    unittest.main()
