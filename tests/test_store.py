import unittest

from causal import build_graph
from store import slug


class StoreTests(unittest.TestCase):
    def test_slug_is_stable_and_safe(self):
        self.assertEqual(slug("Capture DUT Trigger!"), "capture-dut-trigger")
        self.assertEqual(slug("___"), "untitled-task")

    def test_causal_graph_uses_counterfactual_counts(self):
        observations = ([{"causes": ["scope.armed"], "actions": ["dut.start"], "effects": ["trigger.captured"]}] * 8
                        + [{"causes": [], "actions": ["dut.start"], "effects": ["trigger.missed"]}] * 4)
        graph = build_graph("capture", observations)
        relation = graph["relations"][0]
        self.assertEqual(relation["cause"], "scope.armed")
        self.assertEqual(relation["statistics"]["p_effect_given_cause"], 1.0)
        self.assertEqual(relation["statistics"]["p_effect_given_no_cause"], 0.0)
        self.assertEqual(relation["status"], "candidate_cause")


if __name__ == "__main__":
    unittest.main()
