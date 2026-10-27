"""Exercise the portable installer through its public command line."""
from pathlib import Path
import re
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
INSTALLER = ROOT / "scripts/install-skills.py"


class InstallSkillsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.dest = Path(self.temp.name) / "project/.agents/skills"

    def install(self, *args):
        return subprocess.run(
            [sys.executable, str(INSTALLER), "--dest", str(self.dest), *args],
            capture_output=True, text=True, timeout=30,
        )

    def test_core_and_ai_include_complete_resources(self):
        result = self.install("--packs", "fde-core", "fde-ai")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(list(self.dest.glob("*/SKILL.md"))), 36)
        self.assertTrue((self.dest / "_shared/agent-context.md").is_file())
        self.assertTrue((self.dest / "repo-recon/references/entry-points-by-stack.md").is_file())
        self.assertEqual(
            (self.dest / "repo-recon/SKILL.md").read_bytes(),
            (ROOT / "fde-core/skills/repo-recon/SKILL.md").read_bytes(),
        )

    def test_all_seven_packs_install_fifty_skills(self):
        result = self.install("--packs", "fde-core", "fde-ai", "fde-product", "fde-data",
                              "fde-migration", "fde-operate", "fde-platform")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(list(self.dest.glob("*/SKILL.md"))), 50)
        self.assertTrue((self.dest / "db-change-management/references/engine-notes.md").is_file())
        # A complete copy must keep references usable from their installed paths.
        for skill in self.dest.glob("*/SKILL.md"):
            for ref in re.findall(r"(?:\.\./[A-Za-z0-9_-]+/(?:references/)?|references/)[A-Za-z0-9_./-]+\.md",
                                  skill.read_text()):
                self.assertTrue((skill.parent / ref).is_file(), f"{skill.parent.name}: {ref}")

    def test_adding_optional_pack_keeps_existing_core(self):
        self.assertEqual(self.install().returncode, 0)
        before = (self.dest / "repo-recon/SKILL.md").read_bytes()
        result = self.install("--packs", "fde-core", "fde-ai")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual((self.dest / "repo-recon/SKILL.md").read_bytes(), before)
        self.assertTrue((self.dest / "ai-evaluation/SKILL.md").is_file())

    def test_identical_repeat_preserves_unrelated_skills(self):
        self.assertEqual(self.install().returncode, 0)
        unrelated = self.dest / "team-skill/SKILL.md"
        unrelated.parent.mkdir()
        unrelated.write_text("Team-owned instructions\n")
        self.assertEqual(self.install().returncode, 0)
        self.assertEqual(unrelated.read_text(), "Team-owned instructions\n")

    def test_conflict_stops_before_installing_anything(self):
        existing = self.dest / "repo-recon/SKILL.md"
        existing.parent.mkdir(parents=True)
        existing.write_text("Do not replace team instructions\n")
        result = self.install()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("repo-recon", result.stderr)
        self.assertFalse((self.dest / "fde-orient").exists())
        self.assertEqual(existing.read_text(), "Do not replace team instructions\n")

    def test_symlink_conflict_is_not_followed(self):
        outside = Path(self.temp.name) / "team-owned"
        outside.mkdir()
        marker = outside / "marker"
        marker.write_text("preserve\n")
        self.dest.mkdir(parents=True)
        (self.dest / "_shared").symlink_to(outside, target_is_directory=True)
        result = self.install()
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertIn("symlink", result.stderr)
        self.assertEqual(list(outside.iterdir()), [marker])

    def test_invalid_pack_does_not_create_destination(self):
        result = self.install("--packs", "../unknown")
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(self.dest.exists())


if __name__ == "__main__":
    unittest.main()
