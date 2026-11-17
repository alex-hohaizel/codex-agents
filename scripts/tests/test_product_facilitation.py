"""Exercise exact document preview, blocking questions, and independent review."""

from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "product_facilitation.py"


class ProductFacilitationTest(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name).resolve()
        self.text = "A operator: Show item detail on the shared screen.\nB owner: Keep details private.\n"
        self.write("requirements.json", {"requirements": [
            {"id": "SCOPE", "text": "Protect detail by recipient.", "priority": "must",
             "acceptance": "A signed-in recipient sees only their detail."},
            {"id": "ALERT", "text": "Display a pending transfer.", "priority": "must",
             "dependencies": ["SCOPE"], "acceptance": "Show pending after relaunch."},
        ]})
        self.decisions = {"decisions": [{"id": "D-STORAGE", "text": "Use existing storage."}]}
        self.questions = [{
            "id": "Q-DETAIL", "prompt": "Where should the transfer detail appear?",
            "owner": "Depot operations", "needed_by": "prototype review", "positions": ["N1", "N2"],
            "blocks": ["SCOPE"],
        }]

    def write(self, path, record):
        (self.root/path).write_text(json.dumps(record, ensure_ascii=False), encoding="utf-8")

    def pin(self, name):
        return {"path": name, "sha256": sha256((self.root/name).read_bytes()).hexdigest()}

    def prepare(self, route, *, omit=()):
        (self.root/"field-notes.md").write_text(self.text, encoding="utf-8")
        self.write("decisions.json", self.decisions)
        self.write("tickets.json", {
            "schema_version": "atelier.ticket-projection/1", "project_id": "fixture",
            "native_revision": "r1", "requirement_sources": [self.pin("requirements.json")],
            "tickets": [{"id": "T-ALERT", "kind": "bug", "status": "planned", "title": "Queue",
                         "requirement_ids": ["ALERT"], "acceptance": "Restore alert."}],
        })
        sections = {
            "brief": ("need", "current", "outcome", "bounds"),
            "prfaq": ("release", "customer", "stakeholder"),
            "ux": ("visual", "components", "journey", "states", "accessibility", "acceptance"),
        }[route]
        self.write("facilitation.json", {
            "schema_version": "atelier.product-facilitation/1", "project_id": "fixture",
            "native_revision": "r1", "projection_sha256": self.pin("tickets.json")["sha256"],
            "author": "product", "route": route, "title": "Depot queue",
            "sources": [self.pin("field-notes.md")],
            "decision_sources": [self.pin("decisions.json")], "requirement_ids": ["ALERT"],
            "notes": [{"id": "N1", "source_path": "field-notes.md", "speaker": "Operator",
                       "excerpt": "Show item detail on the shared screen."},
                      {"id": "N2", "source_path": "field-notes.md", "speaker": "Owner",
                       "excerpt": "Keep details private."}],
            "questions": self.questions,
            "sections": {key: [{"heading": "Candidate response", "body": "Read detail in a safe <panel>.",
                                "source_notes": ["N1", "N2"]}]
                         for key in sections if key not in omit},
        })

    def run_case(self, action, *args, code=0, as_json=True):
        proc = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), action, "--root", str(self.root),
             "--input", "facilitation.json", "--projection", "tickets.json", *args],
            text=True, capture_output=True, check=False, timeout=10,
        )
        self.assertEqual(proc.returncode, code, proc.stdout or proc.stderr)
        output = proc.stdout or proc.stderr
        return json.loads(output) if as_json else output

    def review(self, report, *, reviewer="qa", code=0):
        self.write("review.json", {
            "schema_version": "atelier.product-facilitation-review/1",
            "bundle_sha256": report["bundle_sha256"], "reviewer": reviewer,
            "verdict": "approve", "summary": "Checked each section against its source.",
            "checks": [{"id": ident, "outcome": "matches", "observation": "Matched both sources."}
                       for ident in report["section_ids"]],
        })
        return self.run_case("review", "--review", "review.json", "--review-sha256",
                             self.pin("review.json")["sha256"], code=code)

    def test_routes_keep_document_types_and_reference_exact_lines(self):
        for route, documents in (("brief", ["BRIEF"]), ("prfaq", ["PRFAQ"]),
                                 ("ux", ["DESIGN", "EXPERIENCE"])):
            with self.subTest(route=route):
                self.prepare(route)
                report = self.run_case("draft")
                self.assertEqual(list(report["documents"]), documents)
                self.assertEqual(report["notes"]["N1"]["first_line"], 1)
                self.assertEqual(report["notes"]["N2"]["first_line"], 2)
                self.assertEqual(set(report["requirements"]), {"ALERT", "SCOPE"})
                self.assertEqual(report["questions"][0]["affected_ticket_ids"], ["T-ALERT"])

    def test_prfaq_has_distinct_faqs_safe_html_and_required_sections(self):
        self.prepare("prfaq")
        markdown = self.run_case("draft", "--format", "markdown", as_json=False)
        self.assertIn("## Customer FAQ", markdown)
        self.assertIn("## Stakeholder FAQ", markdown)
        html = self.run_case("draft", "--format", "html", as_json=False)
        self.assertIn("<h2>Customer FAQ</h2>", html)
        self.assertIn("safe &lt;panel&gt;", html)
        self.assertNotIn("<panel>", html)
        self.prepare("prfaq", omit=["stakeholder"])
        self.assertIn("missing or unknown route section", self.run_case("draft", code=2)["error"])

    def test_blocking_contradiction_holds_ready_and_review(self):
        self.prepare("ux")
        draft = self.run_case("draft", "--require-ready", code=3)
        self.assertEqual(draft["blocking_question_ids"], ["Q-DETAIL"])
        self.assertEqual(self.review(draft, code=3)["status"], "awaiting-decision")
        self.assertIn("reviewer must differ", self.review(draft, reviewer="PRODUCT", code=2)["error"])

    def test_resolve_exact_evidence_then_refuse_drift_and_prior_review(self):
        self.prepare("brief")
        prior = self.run_case("draft")
        self.decisions["decisions"].append({
            "id": "D-DETAIL", "question_id": "Q-DETAIL", "selected_note_id": "N2",
            "question_sha256": prior["questions"][0]["question_sha256"],
            "position_sha256": {key: note["binding_sha256"] for key, note in prior["notes"].items()},
        })
        self.prepare("brief")
        resolved = self.run_case("draft", "--require-ready")
        self.assertEqual(resolved["status"], "draft-for-review")
        self.assertEqual(resolved["questions"][0]["resolution"]["selected_note_id"], "N2")
        self.assertEqual(self.review(resolved)["status"], "reviewed")
        self.assertIn("different facilitation bundle", self.review(prior, code=2)["error"])
        (self.root/"field-notes.md").write_text(self.text + "C observer: New evidence.\n")
        self.assertIn("SOURCE_DRIFT", self.run_case("draft", code=2)["error"])
        self.text += "C observer: New evidence.\n"
        self.prepare("brief")
        self.assertIn("changed question or evidence", self.run_case("draft", code=2)["error"])


if __name__ == "__main__":
    unittest.main()
