import contextlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import document_templates as templates


class DocumentTemplateTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name).resolve()
        self.write("source.md", "Approval flow and the fixed recovery location.")
        base = self.write("base.md", """---
template: recovery
version: 1.0.0
description: A recovery procedure.
paced: true
facilitation_order: [context, steps, rollback?]
view: view.html
html_view: always
---
<!-- companions: For a customer-visible incident include `{id}-{slug}-notice.md`. -->

# {title}

## Table of Contents

## Context

## Steps

## Rollback
<!-- include when: a write occurred. Verify the target and the required recovery actions. -->
""")
        overlay = self.write("overlay.md", """---
extends: recovery
---

## Communications
<!-- After Steps. Who owns the communication. -->
""")
        layout = self.write("view.html", """<!doctype html>
<html lang="en"><head><title data-field="title"></title></head>
<body><header><h1 data-field="title"></h1></header><main>
<section data-section="Steps"><h2>Steps</h2><div data-body></div></section>
<aside data-section="Rollback"><p>Omitted section marker</p></aside>
<section data-rest></section></main></body></html>""")
        self.registry = {"schema": templates.REGISTRY, "layers": [
            {"scope": "team", "templates": [overlay]},
            {"scope": "agent", "templates": [base], "resources": [layout]},
        ]}
        self.write("registry.json", self.registry)
        self.plan = self.ok("inspect", "--registry", "registry.json", "--template", "recovery")
        self.request = {
            "schema": templates.REQUEST, "id": "R-1", "title": "Recovery drill", "owner": "Maintainer",
            "sources": [self.pin("source.md")],
            "sections": {
                "context": {"include": True, "items": [self.item("OBS-1", "Recover an approved operation.")]},
                "steps": {"include": True, "items": [
                    self.item("STEP-1", "Read the **current journal**.\n\n<script>untrusted()</script>"),
                    self.item("STEP-2", "Follow the visible decision. [Open](javascript:alert(1))"),
                ]},
                "communications": {"include": True, "items": [self.item("OPS-1", "The shared owner coordinates.")]},
                "rollback": {"include": False, "reason": "This drill stops before any write."},
            },
            "companions": {
                "R-1-recovery-drill-notice.md": {"include": True, "reason": "Owner approved the exercise note.",
                                                 "items": [self.item("N-1", "No interruption of service occurred.")]},
            },
            "assumptions": [{"id": "A-1", "text": "Journal always available.", "status": "open"}],
        }
        self.write("request.json", self.request)

    def write(self, name, value):
        path = self.root / name
        if isinstance(value, str):
            path.write_text(value, encoding="utf-8")
        else:
            path.write_text(json.dumps(value), encoding="utf-8")
        return self.pin(name)

    def pin(self, name):
        return {"path": name, "sha256": templates.context.digest((self.root / name).read_bytes())}

    @staticmethod
    def item(ident, body):
        return {"id": ident, "body": body, "sources": ["source.md"]}

    def call(self, *args):
        out, error = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(error):
            code = templates.main(["--root", str(self.root), *args])
        return code, out.getvalue(), error.getvalue()

    def ok(self, *args):
        code, value, error = self.call(*args)
        self.assertEqual(code, 0, error)
        return json.loads(value)

    def draft(self, command="draft", output="v1", *extra):
        return self.ok(command, "--registry", "registry.json", "--template", "recovery",
                       "--request", "request.json", "--expect-template", self.plan["plan_sha256"],
                       "--output", output, *extra)

    def findings(self, sha):
        self.write("findings.json", {"schema": templates.DECISION, "draft_sha256": sha,
            "reviewer": "Recovery QA", "findings": {
                key: {"status": "pass", "note": "Verified against the recorded target and journal."}
                for key in ("context", "steps", "communications", "companion/R-1-recovery-drill-notice.md")
            }})

    def review_command(self, output, sha):
        return ("review", "--registry", "registry.json", "--template", "recovery",
                "--findings", "findings.json", "--draft", f"{output}/draft.json", "--expect-draft", sha)

    def test_overlay_pacing_and_repeat_slots_preserve_original(self):
        self.assertEqual(self.plan["coaching_order"], ["context", "steps", "communications", "rollback"])
        self.write("partial.json", {"sections": {"context": self.request["sections"]["context"]}})
        stage = self.ok("progress", "--registry", "registry.json", "--template", "recovery",
                        "--request", "partial.json")
        self.assertEqual([item["id"] for item in stage["next"]], ["steps"])
        self.assertEqual(stage["total"], 4)
        receipt = self.draft()
        rendered = (self.root / "v1/document.html").read_text()
        self.assertIn("<strong>current journal</strong>", rendered)
        self.assertIn("STEP-1", rendered)
        self.assertIn("STEP-2", rendered)
        self.assertIn("&lt;script&gt;", rendered)
        self.assertNotIn("href=\"javascript", rendered)
        self.assertNotIn("Omitted section marker", rendered)
        self.assertEqual(receipt["unplaced_html_sections"], [])
        markdown = (self.root / "v1/document.md").read_text()
        self.assertIn("This drill stops before any write.", markdown)
        self.assertIn("[ASSUMPTION: Journal always available.]", markdown)
        self.assertIn("R-1-recovery-drill-notice.md", receipt["artifacts_sha256"])
        self.assertIn("## Rollback", (self.root / "base.md").read_text())

    def test_revision_requires_exact_artifacts_and_current_review(self):
        first = self.draft()
        old = first["draft_sha256"]
        self.findings(old)
        self.assertEqual(self.ok(*self.review_command("v1", old))["status"], "revise")
        self.request["assumptions"][0].update(status="corrected", resolution="Check the explicit recovery root.",
                                             sources=["source.md"])
        self.request["change_reason"] = "Review required a durable fallback."
        self.request["sections"]["steps"]["items"][1]["body"] = "Read the durable recovery root."
        self.write("request.json", self.request)
        second = self.draft("update", "v2", "--draft", "v1/draft.json", "--expect-draft", old)
        current = second["draft_sha256"]
        self.assertEqual(second["revision"], 2)
        self.assertEqual(self.call(*self.review_command("v2", current))[0], 2)
        self.findings(current)
        self.assertEqual(self.ok(*self.review_command("v2", current))["status"], "reviewed")
        self.write("v2/document.md", "Manual edit that was never reviewed.")
        forged = json.loads((self.root / "v2/receipt.json").read_text())
        forged["artifacts_sha256"]["document.md"] = self.pin("v2/document.md")["sha256"]
        self.write("v2/receipt.json", forged)
        self.assertIn("hashes pinned in the reviewed draft", self.call(*self.review_command("v2", current))[2])

    def test_required_scope_and_active_layout_fail_before_output(self):
        self.request["sections"]["context"] = {"include": False, "reason": "skip scope"}
        self.write("request.json", self.request)
        args = ("draft", "--registry", "registry.json", "--template", "recovery", "--request", "request.json",
                "--expect-template", self.plan["plan_sha256"], "--output", "invalid")
        self.assertIn("required or filled section", self.call(*args)[2])
        self.assertFalse((self.root / "invalid").exists())
        self.request["sections"]["context"] = {"include": True, "items": [self.item("OBS-1", "Recover scope.")]}
        self.write("request.json", self.request)
        self.registry["layers"][1]["resources"] = [self.write("view.html",
            "<html><head><script src=\"https://example.invalid\"></script></head><body></body></html>")]
        self.write("registry.json", self.registry)
        self.plan = self.ok("inspect", "--registry", "registry.json", "--template", "recovery")
        self.assertIn("unsupported element", self.call(*args[:-3], self.plan["plan_sha256"], "--output", "invalid")[2])
        self.assertFalse((self.root / "invalid").exists())


if __name__ == "__main__":
    unittest.main()
