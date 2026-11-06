"""Checks for the skill pack, the fictional preview, and the installer."""

from __future__ import annotations

import io
import json
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from empack.cli import main  # noqa: E402
from empack.contract import DISCLAIMER, ROOT as PACK_ROOT, SKILL_NAMES  # noqa: E402
from empack.frontmatter import FrontmatterError, parse_frontmatter  # noqa: E402
from empack.preview import build_index  # noqa: E402
from empack.render import as_bullets, load_example, render_skill  # noqa: E402
from empack.validate import (  # noqa: E402
    format_report,
    release_decision_errors,
    validate_example,
    validate_name,
    validate_pack,
)


class PackTests(unittest.TestCase):
    def test_pack_matches_the_contract(self) -> None:
        self.assertEqual(validate_pack(), [])

    def test_examples_share_one_fictional_story(self) -> None:
        weekly = load_example("weekly-update")
        incident = load_example("incident-postmortem")
        meeting = load_example("one-on-one")
        release = load_example("release-checklist")
        for data in (weekly, incident, meeting, release):
            self.assertEqual(data["disclaimer"], DISCLAIMER)
            self.assertTrue(data["meta"]["fictional"])
        self.assertEqual(weekly["organization"], "Fictional Harbor Labs")
        self.assertTrue(any("DR-44" in row["event"] for row in incident["timeline"]))
        self.assertIn("2026.03.04.1", json.dumps(weekly))
        self.assertIn("2026.03.04.1", json.dumps(release))
        self.assertIn("2026.02.18.2", json.dumps(release))
        self.assertIn("Jordan Lee (fictional support lead)", json.dumps(weekly))
        self.assertIn("Jordan Lee (fictional support lead)", json.dumps(release))
        self.assertEqual(meeting["date"], "2026-03-04")
        self.assertIn("2026-03-04", json.dumps(release))
        rendered = render_skill("incident-postmortem", incident)
        self.assertTrue(rendered.startswith("> " + DISCLAIMER))
        self.assertIn("Hypothesis", rendered)
        self.assertNotIn("Not provided", rendered)

    def test_go_with_a_gap_needs_an_accepted_risk(self) -> None:
        data = json.loads(json.dumps(load_example("release-checklist")))
        data["checks"][0]["status"] = "Not ready"
        data["accepted_risk"] = ""
        errors = release_decision_errors(data)
        self.assertTrue(errors)
        self.assertTrue(validate_example("release-checklist", data))
        data["accepted_risk"] = "The fictional manager accepts this named gap for this window."
        self.assertEqual(release_decision_errors(data), [])

    def test_ready_check_requires_evidence(self) -> None:
        data = json.loads(json.dumps(load_example("release-checklist")))
        data["checks"][0]["evidence"] = "Not provided"
        errors = validate_example("release-checklist", data)
        self.assertTrue(any("without evidence" in error for error in errors))

    def test_empty_list_is_explicit(self) -> None:
        self.assertEqual(as_bullets([]), "Not provided")

    def test_name_rules(self) -> None:
        self.assertIsNone(validate_name("weekly-update"))
        self.assertIsNotNone(validate_name("Weekly-Update"))
        self.assertIsNotNone(validate_name("-weekly"))
        self.assertIsNotNone(validate_name("weekly--update"))
        self.assertIsNotNone(validate_name("claude-helper"))

    def test_frontmatter_rejects_a_missing_open(self) -> None:
        with self.assertRaises(FrontmatterError):
            parse_frontmatter("# no frontmatter\n")

    def test_preview_contains_the_check_report_and_fixture_facts(self) -> None:
        documents = [
            (name, render_skill(name, load_example(name))) for name in SKILL_NAMES
        ]
        report = format_report([])
        page = build_index(report, documents, "2026-11-06T01:00:00Z")
        self.assertIn("pass weekly-update", page)
        self.assertIn("2026-11-06T01:00:00Z", page)
        self.assertIn("FICTIONAL EXAMPLE", page)
        self.assertIn("The export fix is in staging", page)
        self.assertIn("Staging export worker restart loop", page)
        self.assertIn("python3 -m empack demo", page)
        self.assertNotIn("stars", page.lower())
        self.assertNotRegex(page.lower(), r"\d+\s+downloads")

    def test_install_dry_run_writes_nothing_and_real_install_copies(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "skills"
            with redirect_stdout(io.StringIO()):
                dry_run = main(["install", "--dest", str(dest), "--dry-run"])
            self.assertEqual(dry_run, 0)
            self.assertFalse(dest.exists())
            with redirect_stdout(io.StringIO()):
                installed = main(["install", "--dest", str(dest)])
            self.assertEqual(installed, 0)
            self.assertTrue((dest / "weekly-update" / "SKILL.md").is_file())
            copied = (dest / "one-on-one" / "assets" / "example-input.json").read_text(
                encoding="utf-8"
            )
            self.assertIn("FICTIONAL EXAMPLE", copied)
        with redirect_stdout(io.StringIO()):
            blocked = main(["install", "--dest", str(PACK_ROOT / "skills")])
        self.assertEqual(blocked, 1)

    def test_cli_check_and_demo(self) -> None:
        check = subprocess.run(
            [sys.executable, "-m", "empack", "check"],
            cwd=PACK_ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
        self.assertIn("pass release-checklist", check.stdout)
        with tempfile.TemporaryDirectory() as tmp:
            demo = subprocess.run(
                [sys.executable, "-m", "empack", "demo", "--out", tmp],
                cwd=PACK_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(demo.returncode, 0, demo.stdout + demo.stderr)
            index = Path(tmp) / "index.html"
            self.assertTrue(index.is_file())
            text = index.read_text(encoding="utf-8")
            self.assertIn("empack check passed", text)
            for name in SKILL_NAMES:
                draft = Path(tmp) / f"{name}.md"
                self.assertTrue(draft.is_file())
                self.assertGreater(draft.stat().st_size, 400)


if __name__ == "__main__":
    unittest.main()
