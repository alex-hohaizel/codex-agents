"""Owner-instance verification prevents a fake localhost listener receiving the key."""
import base64
import hashlib
import hmac
import http.server
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest

CLIENT = Path(__file__).resolve().parents[2] / 'optional-skills/atelier-orchestrator/scripts/atelier_client.py'

class OwnerClientTests(unittest.TestCase):
    def run_fixture(self, valid):
        key = base64.urlsafe_b64encode(os.urandom(32)).decode().rstrip('=')
        instance = 'instance_12345678-1234-1234-1234-123456789abc'
        received = []
        class Handler(http.server.BaseHTTPRequestHandler):
            def log_message(self, *args): pass
            def do_GET(self):
                received.append((self.path, self.headers.get('X-Atelier-Control')))
                if self.path.startswith('/health?owner_probe='):
                    nonce = self.path.split('=', 1)[1]
                    proof = base64.urlsafe_b64encode(hmac.new(base64.urlsafe_b64decode(key + '='), ('atelier.instance.' + instance + '.' + nonce).encode(), hashlib.sha256).digest()).decode().rstrip('=')
                    body = {'instance_id': instance, 'owner_proof': proof if valid else 'fake'}
                elif self.path == '/api/v1/session':
                    body = {'csrf_token': 'fixture'}
                else:
                    body = {'version': '0.1.0', 'projects': [], 'jobs': [], 'capabilities': {}}
                self.send_response(200)
                self.send_header('Content-Type', 'application/json')
                self.end_headers(); self.wfile.write(json.dumps(body).encode())
        server = http.server.ThreadingHTTPServer(('127.0.0.1', 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True); thread.start()
        try:
            with tempfile.TemporaryDirectory() as directory:
                root = Path(directory).resolve()
                runtime = {'origin': 'http://127.0.0.1:' + str(server.server_port), 'port': server.server_port, 'data_dir': str(root), 'instance_id': instance}
                for name, data in [('runtime.json', runtime), ('owner-credentials.json', {'instance_id': instance, 'control_key': key})]:
                    file = root / name; file.write_text(json.dumps(data)); file.chmod(0o600)
                result = subprocess.run([sys.executable, '-B', str(CLIENT), 'status', '--data-dir', str(root), '--port', str(server.server_port)], capture_output=True, text=True, timeout=5)
                self.assertNotIn(key, result.stdout + result.stderr)
                self.assertEqual(result.returncode, 0 if valid else 2)
                self.assertIsNone(received[0][1])
                if valid:
                    self.assertEqual(received[1], ('/api/v1/session', key))
                    self.assertTrue(all(value is None for _, value in received[2:]))
                else:
                    self.assertEqual(len(received), 1)
        finally:
            server.shutdown(); server.server_close(); thread.join()
    def test_verified_owner(self): self.run_fixture(True)
    def test_impostor_gets_no_key(self): self.run_fixture(False)

if __name__ == '__main__': unittest.main()
