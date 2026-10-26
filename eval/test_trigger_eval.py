"""Offline regression tests for the trigger evaluator; no model calls."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest import mock


SPEC = importlib.util.spec_from_file_location(
    "trigger_eval", Path(__file__).with_name("run-trigger-eval.py")
)
runner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runner)


class ReplyTests(unittest.TestCase):
    def setUp(self):
        runner.KNOWN.clear()
        runner.KNOWN.update({"safe-change", "repo-recon"})

    def test_invalid_reply_is_an_error(self):
        for reply in (
            "", "authentication failed", "not safe-change", "unknown-skill",
            "NONE, safe-change", "safe-change, safe-change",
            "safe-change, repo-recon, safe-change",
        ):
            with self.subTest(reply=reply), self.assertRaises(ValueError):
                runner.parse_reply(reply)

    def test_valid_answers_preserve_order(self):
        self.assertEqual(runner.parse_reply("`repo-recon`, **safe-change**"),
                         ["repo-recon", "safe-change"])

    def test_only_explicit_none_means_no_skill(self):
        self.assertEqual(runner.parse_reply("NONE\n"), [])


class MetadataTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.path = self.root / "fde-test/skills/safe-change/SKILL.md"
        self.path.parent.mkdir(parents=True)
        self.patch = mock.patch.object(runner, "ROOT", self.root)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def test_quoted_yaml_is_decoded(self):
        self.path.write_text('---\nname: safe-change\ndescription: "Use when: changing code"\n---\n')
        self.assertEqual(runner.load_skills(), "- safe-change: Use when: changing code")

    def test_folded_yaml_is_loaded_in_full(self):
        self.path.write_text('---\nname: safe-change\ndescription: >-\n  Change code.\n  Keep evidence.\n---\n')
        self.assertEqual(runner.load_skills(), "- safe-change: Change code. Keep evidence.")

    def test_delimiter_inside_description_is_not_a_boundary(self):
        self.path.write_text('---\nname: safe-change\ndescription: "Before --- after"\n---\n')
        self.assertEqual(runner.load_skills(), "- safe-change: Before --- after")

    def test_non_string_description_fails(self):
        self.path.write_text('---\nname: safe-change\ndescription: true\n---\n')
        with self.assertRaisesRegex(ValueError, "description must be"):
            runner.load_skills()

    def test_invalid_yaml_fails_before_judging(self):
        self.path.write_text('---\nname: safe-change\ndescription: Use when: changing code\n---\n')
        with self.assertRaisesRegex(ValueError, "invalid YAML"):
            runner.load_skills()

    def test_mismatched_name_fails(self):
        self.path.write_text('---\nname: repo-recon\ndescription: Map a repository\n---\n')
        with self.assertRaisesRegex(ValueError, "name must match"):
            runner.load_skills()

    def test_missing_frontmatter_fails(self):
        self.path.write_text('# A skill without metadata\n')
        with self.assertRaisesRegex(ValueError, "missing YAML"):
            runner.load_skills()

    def test_empty_catalog_fails(self):
        with self.assertRaisesRegex(ValueError, "No skills found"):
            runner.load_skills()


class SuiteTests(unittest.TestCase):
    def run_suite(self, *, kind="positives", reply="safe-change", judge="grok", failure=None,
                  accept_second=None):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            skill = root / "fde-test/skills/safe-change/SKILL.md"
            skill.parent.mkdir(parents=True)
            skill.write_text('---\nname: safe-change\ndescription: Implement a specified change\n---\n')
            other = skill.parent.parent / "repo-recon/SKILL.md"
            other.parent.mkdir()
            other.write_text('---\nname: repo-recon\ndescription: Map a repository\n---\n')
            spec = {group: [] for group in ("positives", "negatives", "collisions", "regressions")}
            item = {"id": "TEST", "query": "A fixture query",
                    "expect": [] if kind == "negatives" else ["safe-change"]}
            if accept_second:
                item["accept_second"] = accept_second
            spec[kind] = [item]
            queries, output = root / "queries.json", root / "results.json"
            queries.write_text(json.dumps(spec))
            with (
                mock.patch.object(runner, "ROOT", root),
                mock.patch.object(runner, "QUERIES", queries),
                mock.patch("sys.argv", ["eval", "--judge", judge, "--out", str(output)]),
                mock.patch.object(runner.subprocess, "run", side_effect=failure,
                                  return_value=subprocess.CompletedProcess([], 0, reply, "")) as process,
                contextlib.redirect_stdout(io.StringIO()),
            ):
                code = runner.main()
            self.assertTrue(process.call_args.kwargs["check"])
            return code, json.loads(output.read_text())[0]

    def test_passing_suite_exits_zero(self):
        code, row = self.run_suite()
        self.assertEqual((code, row["verdict"]), (0, "pass"))

    def test_failed_case_exits_nonzero(self):
        code, row = self.run_suite(reply="repo-recon")
        self.assertEqual((code, row["verdict"]), (1, "fail"))

    def test_explicit_negative_passes(self):
        code, row = self.run_suite(kind="negatives", reply="NONE")
        self.assertEqual((code, row["verdict"]), (0, "pass"))

    def test_malformed_negative_is_error(self):
        code, row = self.run_suite(kind="negatives", reply="service unavailable")
        self.assertEqual((code, row["verdict"]), (1, "error"))

    def test_nonzero_process_is_error_for_both_judges(self):
        for judge in ("grok", "claude"):
            with self.subTest(judge=judge):
                failure = subprocess.CalledProcessError(2, [judge, "private prompt"],
                                                        stderr="private diagnostic")
                code, row = self.run_suite(kind="negatives", judge=judge, failure=failure)
                self.assertEqual((code, row["verdict"]), (1, "error"))
                self.assertEqual(row["note"], "Judge exited with status 2")
                self.assertEqual(row["raw"], "")

    def test_timeout_is_error_without_command_echo(self):
        code, row = self.run_suite(failure=subprocess.TimeoutExpired(["private prompt"], 180))
        self.assertEqual((code, row["verdict"]), (1, "error"))
        self.assertEqual(row["note"], "Judge timed out")

    def test_acceptable_collision_does_not_fail_suite(self):
        code, row = self.run_suite(kind="collisions", reply="repo-recon",
                                   accept_second=["repo-recon"])
        self.assertEqual((code, row["verdict"]), (0, "acceptable"))


if __name__ == "__main__":
    unittest.main()
