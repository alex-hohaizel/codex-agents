#!/usr/bin/env python3
"""Run a real two-transport feed comparison with isolated local output and receipts."""

import argparse
import csv
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import io
import json
from pathlib import Path
import platform
import statistics
import subprocess
import sys
from threading import Event, Thread
from time import perf_counter

ROOT = Path(__file__).resolve().parent
SOURCES = ("README.md", "feed_import.py", "run_case.py", "samples.json")
FIELDS = ("event_id", "title", "remaining_seats")


def sha256(content):
    return hashlib.sha256(content).hexdigest()


def encode(samples):
    output = io.StringIO(newline="")
    writer = csv.DictWriter(output, FIELDS)
    writer.writeheader()
    writer.writerows(samples)
    return output.getvalue().encode("utf-8")


class Supplier:
    """Real loopback HTTP supplier. Its cases are set between client processes."""

    def __init__(self):
        self.calls = []
        self.release_timeout = Event()
        self.set_response(503)
        supplier = self

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                status, body, declared_extra = supplier.response
                supplier.calls.append({"method": "GET", "path": self.path, "planned_status": status})
                if self.path != "/events.csv":
                    self.send_error(404)
                    return
                if status is None:
                    supplier.release_timeout.wait(timeout=3)
                    return
                self.send_response(status)
                self.send_header("Content-Type", "text/csv; charset=utf-8")
                self.send_header("Content-Length", str(len(body) + declared_extra))
                self.end_headers()
                self.wfile.write(body)

            def log_message(self, format, *args):
                pass

        self.server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        self.thread = Thread(target=self.server.serve_forever, kwargs={"poll_interval": 0.025}, daemon=True)

    def set_response(self, status, body=b"", declared_extra=0):
        self.response = (status, body, declared_extra)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *args):
        self.release_timeout.set()
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=1)


def exercise(output, samples, supplier):
    base, recovery = samples["base"], samples["after_recovery"]
    cases = []
    timings = {}
    snapshots = {}
    for route in ("export", "loopback"):
        live = output / f"{route}-snapshot.json"
        export = output / "supplier-export.csv"
        transport = ["--export", str(export)] if route == "export" else ["--loopback-port", str(supplier.server.server_port)]

        def invoke(name, expected, role="publisher", timeout="1.0"):
            before = live.read_bytes() if live.exists() else None
            request_count = len(supplier.calls)
            started = perf_counter()
            completed = subprocess.run(
                [sys.executable, str(ROOT / "feed_import.py"), "--role", role, "--snapshot", str(live),
                 *transport, "--socket-timeout", timeout], capture_output=True, text=True, timeout=8,
            )
            elapsed = (perf_counter() - started) * 1000
            success = expected in {"published", "already_current"}
            assert completed.returncode == (0 if success else 1), completed
            result = json.loads(completed.stdout if success else completed.stderr)
            assert result["code"] == expected, (name, result)
            after = live.read_bytes() if live.exists() else None
            if expected == "published":
                assert after is not None and before != after and sha256(after) == result["snapshot_sha256"]
            else:
                assert after == before, name
            reached = supplier.calls[request_count:]
            if route == "loopback" and role == "publisher":
                assert len(reached) == 1 and reached[0]["path"] == "/events.csv" and reached[0]["method"] == "GET"
            else:
                assert not reached, name
            cases.append({"route": route, "case": name, "result": result, "elapsed_ms": round(elapsed, 3),
                          "requests": reached, "before_sha256": sha256(before) if before else None,
                          "after_sha256": sha256(after) if after else None})
            return elapsed

        def deliver(content):
            if route == "export":
                export.write_bytes(content)
            else:
                supplier.set_response(200, content)

        deliver(encode(base))
        invoke("authorized base import", "published")
        assert json.loads(live.read_text(encoding="utf-8")) == sorted(base, key=lambda row: row["event_id"])
        snapshots[route] = {"base": sha256(live.read_bytes())}
        original_mtime = live.stat().st_mtime_ns
        timings[route] = [invoke(f"same input repeat {index + 1}", "already_current") for index in range(5)]
        assert live.stat().st_mtime_ns == original_mtime
        deliver(encode(recovery))
        invoke("viewer denied while valid changed input exists", "permission_denied", "viewer")
        deliver(encode([recovery[0], dict(recovery[1], remaining_seats=-1)]))
        invoke("invalid row after valid changed row", "invalid_feed")
        if route == "export":
            export.unlink()
            invoke("source file missing", "source_unavailable")
        else:
            supplier.set_response(403)
            invoke("upstream denies requested export", "provider_denied")
            supplier.set_response(503)
            invoke("upstream unavailable", "source_unavailable")
            supplier.set_response(200, encode(recovery[:1]), declared_extra=20)
            invoke("upstream closes before sending declared complete feed", "source_unavailable")
            supplier.set_response(None)
            invoke("real socket read timeout", "source_timeout", timeout="0.15")
            supplier.release_timeout.set()
        deliver(encode(recovery))
        invoke("explicit recovery after fixing source", "published")
        assert json.loads(live.read_text(encoding="utf-8")) == sorted(recovery, key=lambda row: row["event_id"])
        snapshots[route]["after_recovery"] = sha256(live.read_bytes())
    assert snapshots["export"] == snapshots["loopback"]
    return cases, timings, snapshots["export"]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="a new or empty evidence directory")
    output = parser.parse_args().output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    if any(output.iterdir()):
        parser.error("output directory must be empty")
    samples = json.loads((ROOT / "samples.json").read_text(encoding="utf-8"))
    with Supplier() as supplier:
        cases, timings, parity = exercise(output, samples, supplier)
    receipt = {
        "case": "A10 real local supplier feed integration",
        "runtime": {"python": sys.version.split()[0], "os": platform.system(), "machine": platform.machine()},
        "sources": [{"path": name, "sha256": sha256((ROOT / name).read_bytes())} for name in SOURCES],
        "transport_scope": {"export": "UTF-8 CSV from regular local file", "loopback": "HTTP on 127.0.0.1 only"},
        "external_cost_usd": 0,
        "cost_scope": "No purchased service, model, license, or external traffic. Host resource costs were not measured.",
        "timing_scope": "End-to-end process and source read time for five unchanged imports per transport on this host.",
        "unchanged_import_median_ms": {route: round(statistics.median(values), 3) for route, values in timings.items()},
        "exact_output_parity": parity,
        "cases": cases,
    }
    evidence = output / "integration-receipt.json"
    evidence.write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Passed {len(cases)} real CLI cases; {evidence}")


if __name__ == "__main__":
    main()
