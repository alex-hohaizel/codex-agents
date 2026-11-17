"""Surface conflicting registered requirements without selecting a false authority."""

import hashlib
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ticket_spec_review as spec


class SourceReviewTest(unittest.TestCase):
    def setUp(self):
        scratch = TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.root = Path(scratch.name).resolve()
        self.product = [
            {"id": "EXPORT", "text": "The export requires an account.",
             "dependencies": ["ACCESS"], "acceptance": "Only an authorized account can export."},
            {"id": "ACCESS", "text": "Users can export rows assigned to their account."},
        ]
        self.contract = [
            {"id": "EXPORT", "text": "The export requires an account.",
             "dependencies": ["ACCESS"], "acceptance": "Only an authorized account can export."},
            {"id": "ACCESS", "text": "The attached link grants access to all rows.",
             "dependencies": ["DECISION"]},
        ]

    def write(self, name, value):
        (self.root / name).write_text(json.dumps(value) + "\n")
        return {"path": name, "sha256": hashlib.sha256((self.root / name).read_bytes()).hexdigest()}

    def register(self):
        self.write("review.json", {"schema_version": spec.REQUEST, "project_id": "exports",
                  "native_revision": "r1", "requirement_ids": ["EXPORT"],
                  "sources": [self.write("product.json", {"requirements": self.product}),
                              self.write("api.json", {"requirements": self.contract})]})

    def test_disagreement_in_prerequisite_preserves_both_claims_and_missing_ref(self):
        self.register()
        result = spec.review(self.root, "review.json")
        self.assertEqual(result["status"], "decision-needed")
        self.assertEqual(result["missing_requirement_ids"], ["DECISION"])
        conflict = result["disagreements"][0]
        self.assertEqual(conflict["requirement_id"], "ACCESS")
        self.assertEqual([x["claim"]["verbatim"] for x in conflict["sources"]],
                         [self.product[1]["text"], self.contract[1]["text"]])
        self.assertFalse(result["authority_authenticated"])

    def test_matching_claims_do_not_certify_semantics_and_source_drift_refuses(self):
        self.contract = self.product
        self.register()
        result = spec.review(self.root, "review.json")
        self.assertEqual(result["status"], "compared")
        self.assertFalse(result["semantic_equivalence_certified"])
        self.write("api.json", {"requirements": []})
        with self.assertRaisesRegex(spec.context.ContextError, "SOURCE_DRIFT: api.json"):
            spec.review(self.root, "review.json")
