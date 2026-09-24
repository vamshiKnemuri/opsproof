import unittest

from opsproof.agent import MockAgent
from opsproof.cli import attack_check
from opsproof.evaluation import benchmark, trial
from opsproof.incidents import INCIDENTS
from opsproof.models import Action, ValidationError
from opsproof.policy import PolicyContext, evaluate
from opsproof.report import change_patch
from opsproof.simulation import collect, context, fixture, rehearse


class ActionValidationTests(unittest.TestCase):
    def setUp(self):
        self.raw = {"kind": "set_memory_limit", "namespace": "opsproof-lab", "deployment": "opsproof-app",
                    "reason": "OOMKilled at a low memory limit", "evidence_ids": ["events-1", "metrics-1"], "memory_mib": 128}

    def test_rejects_unknown_action_and_shell_field(self):
        for candidate in ({**self.raw, "kind": "delete_namespace"}, {**self.raw, "command": "rm -rf /"}):
            with self.assertRaises(ValidationError):
                Action.parse(candidate)

    def test_rejects_bool_and_wrong_parameter(self):
        for candidate in ({**self.raw, "memory_mib": True}, {**self.raw, "target_replicas": 2}):
            with self.assertRaises(ValidationError):
                Action.parse(candidate)

    def test_bounds_scope_and_evidence(self):
        evidence = collect(fixture("oom"))
        action = Action.parse(self.raw)
        self.assertTrue(evaluate(action, evidence, context(fixture("oom"))).allowed)
        self.assertFalse(evaluate(action, evidence, PolicyContext(production=True)).allowed)
        self.assertFalse(evaluate(Action.parse({**self.raw, "namespace": "production"}), evidence,
                                  context(fixture("oom"))).allowed)
        self.assertFalse(evaluate(Action.parse({**self.raw, "memory_mib": 4096}), evidence,
                                  context(fixture("oom"))).allowed)
        self.assertFalse(evaluate(Action.parse({**self.raw, "evidence_ids": ["logs-1"]}), evidence,
                                  context(fixture("oom"))).allowed)

    def test_replica_disruption(self):
        evidence = collect(fixture("crash"))
        base = {"kind": "set_replicas", "namespace": "opsproof-lab", "deployment": "opsproof-app",
                "reason": "Increase capacity after failed readiness", "evidence_ids": ["health-1"]}
        self.assertFalse(evaluate(Action.parse({**base, "target_replicas": 0}), evidence,
                                  context(fixture("crash"))).allowed)
        self.assertFalse(evaluate(Action.parse({**base, "target_replicas": 3}), evidence,
                                  context(fixture("crash"))).allowed)


class WorkflowTests(unittest.TestCase):
    def test_all_incidents_recover_and_rollback(self):
        for name in INCIDENTS:
            with self.subTest(name=name):
                state = fixture(name)
                evidence = collect(state)
                decision = MockAgent().decide(evidence)
                self.assertTrue(evaluate(decision.action, evidence, context(state)).allowed)
                result = rehearse(state, decision.action)
                self.assertTrue(result["recovery"])
                self.assertTrue(result["rollback"]["succeeded"])
                self.assertTrue(result["rollback"]["reapplied_recovery"])

    def test_injection_boundaries(self):
        self.assertTrue(all(attack_check().values()))

    def test_comparators_use_same_incident_evidence(self):
        rows = [trial("prompt-injection", approach) for approach in
                ("scripted-runbook", "ungated-agent", "guarded-agent")]
        self.assertEqual(rows[0]["evidence"], rows[1]["evidence"])
        self.assertEqual(rows[1]["evidence"], rows[2]["evidence"])
        self.assertEqual(rows[1]["unsafe_proposals"], 1)
        self.assertFalse(rows[1]["recovery"])
        self.assertTrue(rows[2]["recovery"])

    def test_benchmark_counts_and_model_boundary(self):
        result = benchmark(3)
        self.assertEqual(result["agent_type"], "mock")
        self.assertEqual(len(result["trials"]), 36)
        for row in result["summary"].values():
            self.assertEqual(row["trials"], 12)

    def test_patch_is_scoped_and_reviewable(self):
        report = trial("oom", "guarded-agent")
        patch = change_patch(report)
        self.assertEqual(patch["metadata"], {"name": "opsproof-app", "namespace": "opsproof-lab"})
        self.assertEqual(patch["spec"]["template"]["spec"]["containers"][0]["resources"]["limits"]["memory"], "128Mi")


if __name__ == "__main__":
    unittest.main()
