import copy
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

FILE = Path(__file__).resolve().parents[1] / "fulfillment.py"
SPEC = importlib.util.spec_from_file_location("commercial_fulfillment", FILE)
fulfillment = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(fulfillment)


class FulfillmentTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="agent-rights-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.artifact = self.root / "Agent-System-1.8.0-rc.1-solo.zip"
        self.artifact.write_bytes(b"controlled buyer artifact\n")
        self.offer = fulfillment.read_json(FILE.with_name("offer.json"))
        self.catalog = {"schema": "codex-agents.commercial-build/1",
            "product_id": "codex-agent-system", "product_version": "1.8.0-rc.1",
            "source_commit": "a" * 40,
            "files": [{"name": self.artifact.name, "path": str(self.artifact),
                "edition": "solo", **fulfillment.file_pin(self.artifact)}]}
        self.connection = fulfillment.private_db(self.root / "seller.sqlite")
        self.addCleanup(self.connection.close)

    def issue(self, **extra):
        values = {"edition": "solo", "artifact_name": self.artifact.name,
                  "order_id": "test-order-1", "buyer_ref": "test-user-1"}
        values.update(extra)
        return fulfillment.issue(self.connection, self.offer, self.catalog, **values)

    def test_exact_editions_prices_and_major_grant(self):
        solo, code = self.issue()
        self.assertEqual(solo["price_minor"], 4900)
        self.assertEqual(solo["named_seats"], 1)
        self.assertEqual(solo["purchased_product_major"], 1)
        self.assertTrue(fulfillment.CODE.fullmatch(code))
        self.assertEqual(solo["mode"], "test-not-a-purchase")
        self.assertEqual(self.offer["editions"]["team"]["price_minor"], 14900)
        self.assertEqual(self.offer["editions"]["team"]["named_seats"], 5)

    def test_order_and_redemption_are_idempotent(self):
        first, code = self.issue()
        second, again = self.issue()
        self.assertEqual((first, code), (second, again))
        a = fulfillment.redeem(self.connection, code)
        b = fulfillment.redeem(self.connection, code)
        self.assertEqual(a["confirmation"], b["confirmation"])
        self.assertEqual(self.connection.execute("SELECT count(*) FROM orders").fetchone()[0], 1)
        self.assertEqual(self.connection.execute("SELECT count(*) FROM deliveries").fetchone()[0], 1)
        self.assertEqual(self.connection.execute("SELECT opened_count FROM deliveries").fetchone()[0], 2)

    def test_existing_order_cannot_change_price_or_scope(self):
        first, _ = self.issue()
        self.offer["editions"]["solo"]["price_minor"] = 9999
        with self.assertRaisesRegex(ValueError, "another immutable purchase"):
            self.issue()
        stored = json.loads(self.connection.execute("SELECT entitlement FROM orders").fetchone()[0])
        self.assertEqual(first, stored)

    def test_offline_rights_separate_acquired_major_and_new_version(self):
        entitlement, _ = self.issue()
        before = copy.deepcopy(entitlement)
        same = fulfillment.inspect_entitlement(entitlement, "1.99.0")
        later = fulfillment.inspect_entitlement(entitlement, "2.0.0")
        self.assertTrue(same["acquired_use_persists_without_store"])
        self.assertTrue(same["target_major_included"])
        self.assertFalse(later["target_major_included"])
        self.assertFalse(later["signature_verified"])
        self.assertEqual(entitlement, before)

    def test_exact_digest_and_selected_edition_required(self):
        wrong = copy.deepcopy(self.catalog)
        wrong["files"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "bytes differ"):
            fulfillment.select_artifact(wrong, self.artifact.name, "solo")
        with self.assertRaisesRegex(ValueError, "purchased edition"):
            fulfillment.select_artifact(self.catalog, self.artifact.name, "team")
        entitlement, code = self.issue()
        self.artifact.write_bytes(b"changed after purchase\n")
        with self.assertRaisesRegex(ValueError, "recorded artifact bytes changed"):
            fulfillment.redeem(self.connection, code)

    def test_repeated_delivery_preserves_one_identity_and_exact_documents(self):
        entitlement, code = self.issue()
        destination = self.root / "Покупець з пробілами"
        result = fulfillment.deliver_to(self.connection, code, destination)
        again = fulfillment.deliver_to(self.connection, code, destination)
        self.assertEqual(result["delivery_id"], again["delivery_id"])
        self.assertEqual(fulfillment.file_pin(destination / self.artifact.name),
                         fulfillment.file_pin(self.artifact))
        self.assertEqual(fulfillment.read_json(destination / "entitlement.json"), entitlement)
        self.assertEqual((destination / "LICENSE.txt").read_bytes(),
                         (FILE.parent / "legal/LICENSE.txt").read_bytes())

    def test_unknown_code_does_not_deliver_and_no_customer_project_changes(self):
        self.issue()
        source = self.root / "client-project"
        source.mkdir()
        (source / "customer.txt").write_bytes(b"private work")
        with self.assertRaisesRegex(ValueError, "not found"):
            fulfillment.redeem(self.connection, "AS-" + "a" * 43)
        self.assertEqual((source / "customer.txt").read_bytes(), b"private work")
        self.assertEqual(self.connection.execute("SELECT count(*) FROM deliveries").fetchone()[0], 0)

    def test_team_replacement_requires_reviewed_prior_revision(self):
        item = self.catalog["files"][0]
        item["edition"] = "team"
        entitlement, _ = self.issue(edition="team", organization_ref="test-organization")
        result = fulfillment.replace_seat(self.connection, order_id=entitlement["order_id"],
            slot=1, expected_revision=0, retired_ref=None, next_ref="member-a", operation_id="seat-event-1")
        self.assertEqual(result["new_revision"], 1)
        again = fulfillment.replace_seat(self.connection, order_id=entitlement["order_id"],
            slot=1, expected_revision=0, retired_ref=None, next_ref="member-a", operation_id="seat-event-1")
        self.assertEqual(again["status"], "already-recorded")
        with self.assertRaisesRegex(ValueError, "seat changed"):
            fulfillment.replace_seat(self.connection, order_id=entitlement["order_id"],
                slot=1, expected_revision=0, retired_ref=None, next_ref="member-b", operation_id="seat-event-2")
        replacement = fulfillment.replace_seat(self.connection, order_id=entitlement["order_id"],
            slot=1, expected_revision=1, retired_ref="member-a", next_ref="member-b", operation_id="seat-event-3")
        self.assertEqual(replacement["new_revision"], 2)
        self.assertEqual(self.connection.execute("SELECT count(*) FROM seats").fetchone()[0], 5)

    def test_no_public_seller_database_and_no_production_issuance(self):
        with self.assertRaisesRegex(ValueError, "outside"):
            fulfillment.private_db(FILE.parent / "test.sqlite")
        with self.assertRaisesRegex(ValueError, "production issuance disabled"):
            self.issue(mode="production")
        self.assertEqual(os.stat(self.root / "seller.sqlite").st_mode & 0o077, 0)

    def test_terms_and_symlink_sources_cannot_be_substituted(self):
        self.offer["license_version"] = "9.0.0"
        with self.assertRaisesRegex(ValueError, "license text version"):
            self.issue()
        linked = self.root / "linked.zip"
        linked.symlink_to(self.artifact)
        self.catalog["files"][0]["path"] = str(linked)
        with self.assertRaisesRegex(ValueError, "linked path"):
            fulfillment.select_artifact(self.catalog, self.artifact.name, "solo")


if __name__ == "__main__":
    unittest.main()
