"""Keep the real skill catalog and trigger fixtures consistent without model calls."""
import importlib.util
import json
from pathlib import Path
import unittest


SPEC = importlib.util.spec_from_file_location(
    "catalog_runner", Path(__file__).with_name("run-trigger-eval.py")
)
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class CatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        runner.load_skills()
        cls.names = set(runner.KNOWN)
        cls.spec = json.loads(runner.QUERIES.read_text())
        cls.rows = [row for group in ("positives", "negatives", "collisions", "regressions")
                    for row in cls.spec[group]]

    def test_every_skill_has_a_positive_trigger_case(self):
        targets = {name for row in self.spec["positives"] for name in row["expect"]}
        self.assertEqual(targets, self.names)

    def test_all_expected_and_acceptable_names_exist(self):
        for row in self.rows:
            with self.subTest(case=row["id"]):
                targets = set(row["expect"]) | set(row.get("accept_second", []))
                self.assertLessEqual(targets, self.names)

    def test_case_ids_are_unique(self):
        ids = [row["id"] for row in self.rows]
        self.assertEqual(len(ids), len(set(ids)))

    def test_procedure_scenarios_reference_skills_and_have_review_material(self):
        path = Path(__file__).with_name("procedure-scenarios.json")
        scenarios = json.loads(path.read_text())["scenarios"]
        ids = [scenario["id"] for scenario in scenarios]
        self.assertEqual(len(ids), len(set(ids)))
        for scenario in scenarios:
            with self.subTest(case=scenario["id"]):
                self.assertIn(scenario["skill"], self.names)
                self.assertTrue(scenario["request"].strip())
                self.assertTrue(scenario["context"])
                self.assertTrue(scenario["review_checks"])

    def test_cases_have_nonempty_queries_and_explicit_expectations(self):
        for row in self.rows:
            with self.subTest(case=row["id"]):
                self.assertIsInstance(row["query"], str)
                self.assertTrue(row["query"].strip())
                self.assertIsInstance(row["expect"], list)
        for row in self.spec["positives"]:
            self.assertTrue(row["expect"], row["id"])


if __name__ == "__main__":
    unittest.main()
