import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

module = Path(__file__).resolve().parents[2] / "kit/skills/app-atelier-experience/scripts/ux_prototype.py"
spec = importlib.util.spec_from_file_location("ux_prototype", module)
ux = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ux)


class PrototypeTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name).resolve()
        self.pins = []
        for kind, words in (("design", "Use the approved high-contrast layout"),
                            ("experience", "Check the journal before retrying")):
            path = self.root / (kind + ".md")
            path.write_text(words)
            self.pins.append({"id":kind,"kind":kind,"path":path.name,"sha256":ux.digest(path.read_bytes())})
        self.value = {"schema":ux.SCHEMA,"id":"runbook","title":"Recovery","summary":"Read the receipt",
           "locale":"en","start":"first","theme":{"background":"#EFF3FA","surface":"#FFFFFF","ink":"#12243A","accent":"#214D75","onAccent":"#FFFFFF"},
           "sources":self.pins,"screens":[
            {"id":"first","label":"Review","heading":"Check journal","body":"Validate first",
             "state":"normal","refs":[{"source":"experience","excerpt":"Check the journal"}],
             "fields":[{"id":"check","label":"Read it","type":"check"}],
             "actions":[{"id":"next","label":"Continue","to":"last","requires":["check"]}]},
            {"id":"last","label":"Read back","heading":"Done","body":"Keep the receipt",
             "state":"success","refs":[{"source":"design","excerpt":"approved high-contrast layout"}],"actions":[]}]}

    def build(self):
        (self.root/"flow.json").write_text(json.dumps(self.value))
        return ux.build(self.root,"flow.json")

    def test_changed_source_cannot_reuse_verified_html(self):
        html, review = self.build()
        self.assertEqual(review["html_sha256"], ux.digest(html))
        self.assertIn(b"Content-Security-Policy",html)
        (self.root/"experience.md").write_text("Different accepted requirement")
        with self.assertRaisesRegex(ValueError,"Stale source"):
            self.build()

    def test_action_cannot_leave_reviewed_graph(self):
        self.value["screens"][0]["actions"][0]["to"]="unknown"
        with self.assertRaisesRegex(ValueError,"nonexistent screen"):
            self.build()

    def test_pinned_copy_cannot_inject_a_script(self):
        self.value["screens"][0]["body"]='</script><script>globalThis.changed = true</script>'
        html, _ = self.build()
        self.assertNotIn(b"</script><script>globalThis.changed",html)
        self.assertIn(b"\\u003c/script>",html)

    def test_wrong_contrast_and_unsupported_fields_fail(self):
        self.value["theme"]["accent"]="#FAFAFA"
        with self.assertRaisesRegex(ValueError,"contrast"):
            self.build()


if __name__=="__main__":
    unittest.main()
