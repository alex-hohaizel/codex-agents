"""Exercise approved GitHub writes, durable attempt recovery and conflict checks."""

from contextlib import redirect_stderr, redirect_stdout
from email.message import Message
import hashlib
import io
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ticket_github as github
import ticket_github_update as update

REPO = "/repos/atelier-example/booking"
I = f"{REPO}/issues/1"
B = f"{REPO}/issues/2"
S = f"{REPO}/issues/3"
C = f"{REPO}/issues/4"
DEPS = "/dependencies/blocked_by"


class IssueServer:
    def __init__(self):
        self.repo = {"full_name": "atelier-example/booking", "id": 410, "has_issues": True}
        self.issues = {
            I: self.issue(1, "Door access"),
            B: self.issue(2, "Original buggy door"),
            S: self.issue(3, "Book a room"),
            C: self.issue(4, "Remote-only prerequisite"),
        }
        self.children = {I: [], B: [], S: [], C: []}
        self.blockers = {I: [], B: [], S: [C], C: []}
        self.write_calls = []
        self.read_calls = []
        self.fail = None

    def issue(self, number, title):
        return {
            "id": 100 + number, "number": number, "repository_url": github.API + REPO,
            "state": "open", "state_reason": None, "title": title, "body": "Keep this body.",
        }

    def response(self, request, status, payload):
        body = io.BytesIO(json.dumps(payload).encode())
        headers = Message()
        headers["X-GitHub-Request-Id"] = f"fixture:{len(self.read_calls) + len(self.write_calls)}"
        if status >= 400:
            raise HTTPError(request.full_url, status, "fixture error", headers, body)
        body.status = status
        body.headers = headers
        return body

    def open(self, request, timeout):
        url = urlsplit(request.full_url)
        assert (url.scheme, url.netloc) == ("https", "api.github.com")
        assert request.get_header("X-github-api-version") == github.API_VERSION
        method, endpoint = request.get_method(), url.path
        if method == "GET":
            self.read_calls.append(endpoint)
            if endpoint == REPO:
                value = self.repo
            elif endpoint.endswith("/sub_issues"):
                value = [self.issues[name] for name in self.children[endpoint.removesuffix("/sub_issues")]]
            elif endpoint.endswith(DEPS):
                value = [self.issues[name] for name in self.blockers[endpoint.removesuffix(DEPS)]]
            else:
                value = self.issues[endpoint]
            return self.response(request, 200, value)

        assert request.get_header("Authorization") == "Bearer fixture-token"
        body = json.loads(request.data) if request.data else None
        self.write_calls.append((method, endpoint, body))
        if self.fail == "interrupted":
            raise KeyboardInterrupt
        if self.fail == "lost-before":
            raise URLError("unknown whether the provider received the write")
        if self.fail == "rejected":
            return self.response(request, 403, {})
        if self.fail == "rate-limited":
            return self.response(request, 429, {})
        if method == "PATCH":
            self.issues[endpoint].update(body)
            if body.get("state") == "open":
                self.issues[endpoint]["state_reason"] = "reopened"
            status = 200
        elif method == "POST":
            if endpoint.endswith("/sub_issues"):
                owner = endpoint.removesuffix("/sub_issues")
                related = self.related(body["sub_issue_id"])
                assert body["replace_parent"] is False
                if any(related in rows for rows in self.children.values()):
                    return self.response(request, 422, {})
                self.children[owner].append(related)
            else:
                owner = endpoint.removesuffix(DEPS)
                self.blockers[owner].append(self.related(body["issue_id"]))
            status = 201
        else:
            assert method == "DELETE"
            if endpoint.endswith("/sub_issue"):
                owner = endpoint.removesuffix("/sub_issue")
                self.children[owner].remove(self.related(body["sub_issue_id"]))
            else:
                owner, _, ident = endpoint.partition(DEPS + "/")
                self.blockers[owner].remove(self.related(int(ident)))
            status = 200
        if self.fail == "applied-disconnected":
            raise URLError("provider response lost after applying")
        return self.response(request, status, {})

    def related(self, issue_id):
        return next(key for key, issue in self.issues.items() if issue["id"] == issue_id)


class TrackerWriteTest(unittest.TestCase):
    def setUp(self):
        workspace = TemporaryDirectory()
        self.addCleanup(workspace.cleanup)
        self.root = Path(workspace.name).resolve()
        self.server = IssueServer()
        self.write("requirements.json", {
            "requirements": [{"id": "R-1", "priority": "must", "text": "The door opens for bookings."}],
        })
        self.projection = {
            "schema_version": "atelier.ticket-projection/1", "project_id": "booking",
            "native_revision": "rev-1", "requirement_sources": [self.pin("requirements.json")],
            "tickets": [
                {"id": "I", "kind": "initiative", "title": "Door access", "status": "planned"},
                {"id": "B", "kind": "bug", "title": "Fix the door", "status": "in-progress",
                 "requirement_ids": ["R-1"], "acceptance": "A holder opens the door once."},
                {"id": "S", "kind": "story", "title": "Book a room", "status": "planned",
                 "parent": "I", "depends_on": ["B"], "requirement_ids": ["R-1"],
                 "acceptance": "Book the date after the door opens."},
            ],
        }
        self.write_project()
        self.write("mapping.json", {
            "schema_version": github.MAPPING, "project_id": "booking",
            "repository": {key: self.server.repo[key] for key in ("full_name", "id")},
            "tickets": [{"ticket_id": key, "number": index, "id": 100 + index}
                        for index, key in enumerate(("I", "B", "S"), 1)],
        })

    def write(self, name, data):
        (self.root / name).write_text(json.dumps(data), encoding="utf-8")

    def write_project(self):
        self.write("tickets.json", self.projection)

    def pin(self, name):
        return {"path": name, "sha256": hashlib.sha256((self.root / name).read_bytes()).hexdigest()}

    def invoke(self, operation, *args, code=0, token="fixture-token"):
        stdout, stderr = io.StringIO(), io.StringIO()
        with redirect_stdout(stdout), redirect_stderr(stderr):
            result = update.main([operation, "--root", str(self.root), *args],
                                 client=update.WriteClient(token, opener=self.server))
        self.assertEqual(result, code, stdout.getvalue() or stderr.getvalue())
        return json.loads(stdout.getvalue() or stderr.getvalue())

    def preview(self, ticket, change, related=None, *, code=0, ref="approved.json"):
        options = ["--related", related] if related else []
        value = self.invoke("preview", "--projection", "tickets.json", "--mapping", "mapping.json",
                            "--ticket", ticket, "--change", change, *options, code=code)
        if code == 0:
            self.write(ref, value)
        self.assertFalse((self.root / ".atelier").exists() if not self.server.write_calls else False)
        return value

    def execute(self, operation="commit", *, path="approved.json", sha=None,
                code=0, token="fixture-token", retry_rejected=False):
        options = ["--retry-rejected"] if retry_rejected else []
        return self.invoke(operation, "--preview", path, "--sha256", sha or self.pin(path)["sha256"],
                           *options, code=code, token=token)

    def test_authorized_title_commit_and_repeat_after_project_change(self):
        before = self.preview("B", "title")
        self.assertEqual(before["request"]["body"], {"title": "Fix the door"})
        self.assertFalse(before["provider_atomic_guard"])
        self.assertFalse(self.server.write_calls)
        report = self.execute()
        self.assertEqual(report["status"], "desired-state-observed")
        self.assertEqual(report["prior_attempt"]["response"]["http_status"], 200)
        self.assertEqual(self.server.issues[B]["body"], "Keep this body.")
        self.projection["native_revision"] = "later"
        self.write_project()
        self.assertEqual(self.execute()["status"], "desired-state-observed")
        (self.root / "tickets.json").unlink()
        self.assertEqual(self.execute("read-back")["status"], "desired-state-observed")
        self.assertEqual(len(self.server.write_calls), 1)
        self.server.issues[B]["title"] = "Changed after receipt"
        self.assertEqual(self.execute("read-back", code=2)["status"], "drift-after-readback")
        self.assertEqual(len(self.server.write_calls), 1)

    def test_refuses_changed_preview_source_remote_precondition_and_no_credential(self):
        self.preview("B", "title")
        self.assertIn("preview bytes", self.execute(sha="0" * 64, code=2)["error"])
        self.assertIn("write credential", self.execute(code=2, token=None)["error"])
        self.server.issues[B]["title"] = "Edited externally"
        self.assertEqual(self.execute(code=2)["reason"], "github-state-changed")
        self.projection["native_revision"] = "rev-2"
        self.write_project()
        self.assertIn("SOURCE_DRIFT", self.execute(code=2)["error"])
        self.assertFalse(self.server.write_calls)
        self.assertFalse((self.root / ".atelier").exists())

    def test_lost_response_reconciles_applied_state(self):
        self.preview("B", "title")
        self.server.fail = "applied-disconnected"
        report = self.execute()
        self.assertEqual(report["status"], "desired-state-observed")
        self.assertEqual(report["prior_attempt"]["response"]["response"], "uncertain")
        self.assertEqual(self.execute("read-back")["status"], "desired-state-observed")
        self.assertEqual(len(self.server.write_calls), 1)

    def test_lost_attempt_without_observation_stays_pending(self):
        self.preview("B", "title")
        self.server.fail = "lost-before"
        self.assertEqual(self.execute(code=2)["status"], "pending")
        self.assertEqual(self.execute(code=2)["status"], "pending")
        self.assertEqual(self.execute(code=2, retry_rejected=True)["reason"],
                         "retry-requires-definite-rejection")
        self.assertEqual(len(self.server.write_calls), 1)
        self.assertEqual(self.server.issues[B]["title"], "Original buggy door")
        self.projection["native_revision"] = "rev-2"
        self.projection["tickets"][1]["title"] = "New title"
        self.write_project()
        self.preview("B", "title", ref="new.json")
        self.assertEqual(self.execute(path="new.json", code=2)["reason"], "unresolved-operation-on-mapped-issue")
        self.assertEqual(len(self.server.write_calls), 1)

    def test_approved_preview_cannot_override_another_checkouts_journal(self):
        self.preview("B", "title")
        self.server.fail = "lost-before"
        self.assertEqual(self.execute(code=2)["status"], "pending")
        original = self.root
        with TemporaryDirectory() as other:
            self.root = Path(other).resolve()
            for name in ("tickets.json", "requirements.json", "mapping.json", "approved.json"):
                (self.root / name).write_bytes((original / name).read_bytes())
            self.assertIn("different checkout", self.execute(code=2)["error"])
            self.assertIn("different checkout", self.execute("read-back", code=2)["error"])
            self.assertFalse((self.root / ".atelier").exists())
        self.assertEqual(len(self.server.write_calls), 1)

    def test_interruption_has_a_durable_attempt_before_provider_response(self):
        self.preview("B", "title")
        self.server.fail = "interrupted"
        with self.assertRaises(KeyboardInterrupt):
            self.execute()
        report = self.execute("read-back", code=2)
        self.assertEqual(report["status"], "pending")
        self.assertIsNone(report["prior_attempt"]["response"])
        self.assertEqual(len(self.server.write_calls), 1)

    def test_definite_rejection_surfaces_provider_status_without_resending(self):
        self.preview("B", "title")
        self.server.fail = "rejected"
        report = self.execute(code=2)
        self.assertEqual(report["status"], "rejected")
        self.assertEqual(report["prior_attempt"]["response"]["http_status"], 403)
        self.assertEqual(self.execute(code=2)["writes"], [])
        self.assertEqual(len(self.server.write_calls), 1)
        self.server.fail = None
        retry = self.execute(retry_rejected=True)
        self.assertEqual(retry["status"], "desired-state-observed")
        self.assertEqual(retry["prior_attempt"]["rejections"][0]["http_status"], 403)
        self.assertEqual(len(self.server.write_calls), 2)

    def test_write_rate_limit_stops_follow_up_reads_for_this_run(self):
        self.preview("B", "title")
        before = len(self.server.read_calls)
        self.server.fail = "rate-limited"
        report = self.execute(code=2)
        self.assertEqual(report["status"], "rejected")
        self.assertEqual(report["reason"], "rate-limited")
        self.assertEqual(report["prior_attempt"]["response"]["http_status"], 429)
        self.assertEqual(len(self.server.read_calls) - before, 2)

    def test_add_remove_blocker_preserves_unmapped_neighbor(self):
        self.preview("S", "add-blocker", "B")
        self.assertEqual(self.execute()["status"], "desired-state-observed")
        self.assertEqual(self.server.blockers[S], [C, B])
        self.assertEqual(self.server.write_calls[-1], ("POST", S + DEPS, {"issue_id": 102}))
        self.projection["tickets"][2]["depends_on"] = []
        self.write_project()
        self.preview("S", "remove-blocker", "B")
        self.assertEqual(self.execute()["status"], "desired-state-observed")
        self.assertEqual(self.server.blockers[S], [C])
        self.assertEqual(self.server.write_calls[-1], ("DELETE", S + DEPS + "/102", None))

    def test_add_remove_child_and_decline_implicit_reparent(self):
        self.server.children[B] = [S]
        self.preview("I", "add-child", "S")
        self.assertEqual(self.execute(code=2)["status"], "rejected")
        self.assertEqual(self.server.children[B], [S])
        self.assertEqual(self.server.write_calls[-1], (
            "POST", I + "/sub_issues", {"sub_issue_id": 103, "replace_parent": False},
        ))
        self.server.children[B].clear()
        self.projection["native_revision"] = "rev-2"
        self.write_project()
        self.preview("I", "add-child", "S")
        self.assertEqual(self.execute()["status"], "desired-state-observed")
        self.assertEqual(self.server.children[I], [S])
        self.projection["tickets"][2].update(kind="bug", parent=None)
        self.write_project()
        self.preview("I", "remove-child", "S")
        self.assertEqual(self.execute()["status"], "desired-state-observed")
        self.assertFalse(self.server.children[I])
        self.assertEqual(self.server.write_calls[-1], ("DELETE", I + "/sub_issue", {"sub_issue_id": 103}))

    def test_state_transition_uses_verified_acceptance_when_closing(self):
        bug = self.projection["tickets"][1]
        bug["status"] = "accepted"
        self.write_project()
        denied = self.preview("B", "state", code=2)
        self.assertIn("completion export requires checked", denied["error"])
        self.assertFalse(self.server.write_calls)
        (self.root / "result.txt").write_text("Reviewed door opening from a held reservation.")
        self.write("receipt.json", {
            "schema_version": github.trees.ACCEPTANCE, "project_id": self.projection["project_id"],
            "native_revision": self.projection["native_revision"], "ticket_id": "B",
            "criterion_sha256": hashlib.sha256(bug["acceptance"].encode()).hexdigest(),
            "subject": self.pin("result.txt"),
        })
        bug["evidence"] = [self.pin("receipt.json")]
        self.write_project()
        self.preview("B", "state")
        self.assertEqual(self.execute()["status"], "desired-state-observed")
        self.assertEqual(self.server.write_calls[-1], (
            "PATCH", B, {"state": "closed", "state_reason": "completed"},
        ))
        bug["status"] = "in-progress"
        self.write_project()
        self.preview("B", "state")
        self.assertEqual(self.execute()["status"], "desired-state-observed")
        self.assertEqual(self.server.write_calls[-1], ("PATCH", B, {"state": "open"}))

    def test_lookup_before_attempt_and_noop_have_no_provider_writes(self):
        self.preview("B", "title")
        self.assertEqual(self.execute("read-back", code=2)["status"], "unattempted")
        self.server.issues[B]["title"] = "Fix the door"
        self.assertEqual(self.execute()["status"], "already-current")
        self.assertFalse(self.server.write_calls)
        self.server.issues[B]["title"] = "Original buggy door"
        self.assertEqual(self.execute(code=2)["status"], "drift-after-readback")
        self.assertFalse(self.server.write_calls)

    def test_forbids_unsupported_close_reason_rewrite_and_conflicting_local_link(self):
        self.server.issues[B].update(state="closed", state_reason="completed")
        self.projection["tickets"][1]["status"] = "deferred"
        self.write_project()
        self.assertIn("close reason", self.preview("B", "state", code=2)["error"])
        self.assertIn("disagrees", self.preview("S", "remove-blocker", "B", code=2)["error"])
        self.assertFalse(self.server.write_calls)


if __name__ == "__main__":
    unittest.main()
