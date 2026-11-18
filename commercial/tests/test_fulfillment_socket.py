import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.error import HTTPError
from urllib.request import Request, build_opener, ProxyHandler

FILE = Path(__file__).resolve().parents[1] / "fulfillment.py"
SPEC = importlib.util.spec_from_file_location("commercial_fulfillment_socket", FILE)
module = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(module)


class DeliverySocketTest(unittest.TestCase):
    def test_http_redemption_redownload_and_original_entitlement(self):
        with tempfile.TemporaryDirectory(prefix="agent-delivery-socket-") as temporary:
            root = Path(temporary).resolve()
            artifact = root / "Agent-System-1.8.0-rc.1-solo.zip"
            artifact.write_bytes(b"isolated actual HTTP delivery bytes")
            database = root / "private" / "seller.sqlite"
            offer = module.read_json(FILE.with_name("offer.json"))
            catalog = {"schema": "codex-agents.commercial-build/1", "product_id": "codex-agent-system",
                "product_version": "1.8.0-rc.1", "source_commit": "b" * 40,
                "files": [{"name": artifact.name, "path": str(artifact),
                           "edition": "solo", **module.file_pin(artifact)}]}
            connection = module.private_db(database)
            try:
                entitlement, code = module.issue(connection, offer, catalog, edition="solo",
                    artifact_name=artifact.name, order_id="socket-test-1", buyer_ref="socket-user")
            finally:
                connection.close()
            ready = root / "ready.json"
            process = subprocess.Popen([sys.executable, "-B", str(FILE), "serve",
                "--database", str(database), "--listen", "127.0.0.1", "--port", "0", "--ready", str(ready)],
                stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            try:
                for _ in range(100):
                    if ready.exists():
                        break
                    if process.poll() is not None:
                        self.fail("delivery process stopped before ready: " + process.stderr.read().decode()[:250])
                    time.sleep(.05)
                self.assertTrue(ready.exists(), "delivery process did not report its target")
                origin = module.read_json(ready)["url"]
                opener = build_opener(ProxyHandler({}))
                with opener.open(origin + "/", timeout=4) as page:
                    self.assertEqual(page.headers.get("Referrer-Policy"), "no-referrer")
                    self.assertIn("sha256-", page.headers.get("Content-Security-Policy"))
                    html = page.read().decode()
                    self.assertIn("Приватний код отримання", html)
                    self.assertIn("Private redemption code", html)
                    self.assertIn('type="password"', html)
                    self.assertNotIn(code, html)
                def redeem(body):
                    request = Request(origin + "/redeem", data=module.encode(body), method="POST",
                                      headers={"Content-Type": "application/json"})
                    with opener.open(request, timeout=4) as reply:
                        return json.load(reply)
                first = redeem({"code": code})
                second = redeem({"code": code})
                self.assertEqual(first["confirmation"], second["confirmation"])
                self.assertEqual(first["confirmation"]["entitlement"], entitlement)
                self.assertFalse(first["confirmation"]["payment_processed"])
                self.assertNotIn(str(database), json.dumps(first))
                for received in (first, second):
                    with opener.open(received["download_url"], timeout=4) as reply:
                        self.assertEqual(reply.read(), artifact.read_bytes())
                    with opener.open(received["license_url"], timeout=4) as reply:
                        self.assertEqual(module.digest(reply.read()), entitlement["license_sha256"])
                    with opener.open(received["confirmation_url"], timeout=4) as reply:
                        self.assertEqual(json.load(reply), received["confirmation"])
                with self.assertRaises(HTTPError):
                    redeem({"code": "AS-" + "wrong" * 9})
                cross = Request(origin + "/redeem", data=module.encode({"code": code}), method="POST",
                                headers={"Content-Type": "application/json", "Origin": "https://unrelated.invalid"})
                with self.assertRaises(HTTPError):
                    opener.open(cross, timeout=4)
                self.assertEqual(module.inspect_entitlement(entitlement, "1.8.1")["target_major_included"], True)
            finally:
                process.terminate()
                process.wait(timeout=5)
                process.stderr.close()
            self.assertTrue(module.inspect_entitlement(entitlement)["acquired_use_persists_without_store"])


if __name__ == "__main__":
    unittest.main()
