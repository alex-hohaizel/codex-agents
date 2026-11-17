"""Exercise the read-only tracker command with GitHub issue identity and graph responses."""

from contextlib import redirect_stderr, redirect_stdout
from email.message import Message
import hashlib
import io
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, build_opener

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import ticket_github as github

REPO = "/repos/atelier-example/room-booking"
PAGE_ONE = "?per_page=100&page=1"
PAGE_TWO = "?per_page=100&page=2"


def pin(root, filename):
    return {"path": filename, "sha256": hashlib.sha256((root / filename).read_bytes()).hexdigest()}


class FixtureOpener:
    def __init__(self, routes, on_read=None):
        self.routes = routes
        self.calls = []
        self.on_read = on_read

    def open(self, request, timeout):
        path = urlsplit(request.full_url)
        endpoint = path.path + ("?" + path.query if path.query else "")
        assert path.scheme == "https" and path.netloc == "api.github.com"
        assert request.get_method() == "GET" and request.data is None
        assert request.get_header("X-github-api-version") == github.API_VERSION
        assert 0 < timeout <= 10
        self.calls.append(endpoint)
        if self.on_read:
            self.on_read(endpoint)
        status, payload, extra = self.routes[endpoint]
        headers = Message()
        headers["X-GitHub-Request-Id"] = f"TEST:{len(self.calls)}"
        for key, value in extra.items():
            headers[key] = value
        response = io.BytesIO(json.dumps(payload).encode())
        if status != 200:
            raise HTTPError(request.full_url, status, "test provider response", headers, response)
        response.status = status
        response.headers = headers
        return response


class TicketGitHubTest(unittest.TestCase):
    def setUp(self):
        temp = TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name).resolve()
        self.write("requirements.json", {
            "requirements": [{"id": "R-1", "priority": "must", "text": "Open the reservation door."}],
        })
        self.projection = {
            "schema_version": "atelier.ticket-projection/1",
            "project_id": "booking", "native_revision": "rev-1",
            "requirement_sources": [pin(self.root, "requirements.json")],
            "tickets": [
                {"id": "I", "kind": "initiative", "title": "Door access", "status": "planned"},
                {"id": "B", "kind": "bug", "title": "Enable door", "status": "in-progress",
                 "requirement_ids": ["R-1"], "acceptance": "A reservation opens the door."},
                {"id": "S", "kind": "story", "title": "Place a booking", "status": "planned",
                 "parent": "I", "depends_on": ["B"], "requirement_ids": ["R-1"],
                 "acceptance": "Place a booking with a ready door."},
            ],
        }
        self.mapping = {
            "schema_version": github.MAPPING, "project_id": "booking",
            "repository": {"full_name": REPO.removeprefix("/repos/"), "id": 120},
            "tickets": [{"ticket_id": key, "number": number, "id": 900 + number}
                        for number, key in enumerate(("I", "B", "S"), start=1)],
        }
        self.issues = [self.issue(number, ticket["title"])
                       for number, ticket in enumerate(self.projection["tickets"], start=1)]
        self.routes = {REPO: (200, {**self.mapping["repository"], "has_issues": True}, {})}
        for issue in self.issues:
            endpoint = self.endpoint(issue["number"])
            self.routes[endpoint] = (200, issue, {})
            self.routes[endpoint + "/dependencies/blocked_by" + PAGE_ONE] = (200, [], {})
            self.routes[endpoint + "/sub_issues" + PAGE_ONE] = (200, [], {})
        self.routes[self.endpoint(1) + "/sub_issues" + PAGE_ONE] = (200, [self.issues[2]], {})
        self.routes[self.endpoint(3) + "/dependencies/blocked_by" + PAGE_ONE] = (200, [self.issues[1]], {})

    def issue(self, number, title, **overrides):
        return {
            "id": 900 + number, "number": number, "repository_url": github.API + REPO,
            "state": "open", "state_reason": None, "title": title,
            "body": "Untrusted response content must stay out of the report.",
            **overrides,
        }

    def endpoint(self, number):
        return f"{REPO}/issues/{number}"

    def write(self, name, document):
        (self.root / name).write_text(json.dumps(document), encoding="utf-8")

    def run_cli(self, *args, expected=0, on_read=None):
        self.write("tickets.json", self.projection)
        self.write("mapping.json", self.mapping)
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        stdout, stderr = io.StringIO(), io.StringIO()
        opener = FixtureOpener(self.routes, on_read=on_read)
        with redirect_stdout(stdout), redirect_stderr(stderr):
            status = github.main([
                "--root", str(self.root), "--projection", "tickets.json",
                "--mapping", "mapping.json", *args,
            ], client=github.GitHubClient(opener=opener))
        self.assertEqual(status, expected, stdout.getvalue() or stderr.getvalue())
        if on_read is None:
            self.assertEqual({p.name: p.read_bytes() for p in self.root.iterdir()}, before)
        return json.loads(stdout.getvalue() or stderr.getvalue()), opener.calls

    def test_match_preserves_local_readiness_and_receipts(self):
        report, calls = self.run_cli("--require-clean")
        self.assertEqual(report["status"], "match")
        self.assertEqual(report["projection"], pin(self.root, "tickets.json"))
        self.assertEqual(report["mapping"], pin(self.root, "mapping.json"))
        self.assertEqual(len(calls), 10)
        self.assertEqual(len(report["reads"]), len(calls))
        self.assertEqual(report["reads"][0]["request_id"], "TEST:1")
        initiative, bug, story = report["tickets"]
        self.assertEqual(initiative["remote"]["sub_issues"][0]["id"], 903)
        self.assertEqual(bug["local"]["recorded_status"], "in-progress")
        self.assertEqual(story["remote"]["blocked_by"][0]["id"], 902)
        self.assertEqual(story["local"]["board_state"], "blocked")
        self.assertEqual(story["local"]["effective_prerequisites"], ["B"])
        self.assertNotIn(self.issues[0]["body"], json.dumps(report))

    def test_provider_close_does_not_support_unverified_local_acceptance(self):
        self.projection["tickets"][1]["status"] = "accepted"
        self.issues[1].update(state="closed", state_reason="completed")
        report, _ = self.run_cli("--require-clean", expected=2)
        bug = report["tickets"][1]
        self.assertEqual(bug["remote"]["reason"], "completed")
        self.assertEqual(bug["local"]["acceptance_status"], "unsupported")
        self.assertEqual(report["unsupported_local_acceptance"], ["B"])
        self.assertEqual(report["tickets"][2]["local"]["board_state"], "blocked")
        self.assertEqual(report["status"], "diverged")

    def test_reports_title_close_reason_and_relationship_drift(self):
        self.issues[2].update(state="closed", state_reason="duplicate", title="Different title")
        relationship = self.endpoint(3) + "/dependencies/blocked_by" + PAGE_ONE
        self.routes[relationship] = (200, [
            self.issue(2, "Different repository", id=999,
                       repository_url=github.API + "/repos/other/room-booking"),
        ], {})
        report, _ = self.run_cli("--require-clean", expected=2)
        story = report["tickets"][2]
        difference = {row["field"]: row for row in story["differences"]}
        self.assertEqual(set(difference), {"status", "title", "blocked_by"})
        self.assertEqual(difference["blocked_by"]["missing_or_changed"][0]["id"], 902)
        self.assertEqual(difference["blocked_by"]["unexpected_or_changed"][0]["repository"],
                         "other/room-booking")
        self.assertNotIn("Different title", json.dumps(report))

    def test_wrong_project_and_ambiguous_mapping_fail_before_network(self):
        self.mapping["project_id"] = "other-project"
        report, calls = self.run_cli(expected=2)
        self.assertEqual(report["status"], "invalid-input")
        self.assertFalse(calls)
        self.mapping["project_id"] = "booking"
        self.mapping["tickets"][1]["id"] = self.mapping["tickets"][0]["id"]
        report, calls = self.run_cli(expected=2)
        self.assertIn("ambiguous", report["error"])
        self.assertFalse(calls)

    def test_wrong_repository_prevents_issue_requests(self):
        self.mapping["repository"]["id"] = 121
        report, calls = self.run_cli(expected=2)
        self.assertFalse(report["repository_verified"])
        self.assertEqual(report["unavailable"], "repository-identity-mismatch")
        self.assertEqual(calls, [REPO])

    def test_rejects_pull_request_and_reassigned_number(self):
        self.issues[0]["pull_request"] = {"id": 111}
        self.issues[1]["id"] += 1234
        report, calls = self.run_cli(expected=2)
        self.assertEqual(report["tickets"][0]["unavailable"], {"issue": "not-an-issue"})
        self.assertEqual(report["tickets"][1]["unavailable"], {"issue": "issue-identity-mismatch"})
        self.assertNotIn(self.endpoint(1) + "/sub_issues" + PAGE_ONE, calls)

    def test_distinguishes_hidden_or_missing_list_and_stops_at_rate_limit(self):
        self.routes[self.endpoint(1) + "/dependencies/blocked_by" + PAGE_ONE] = (404, {}, {})
        self.routes[self.endpoint(1) + "/sub_issues" + PAGE_ONE] = (403, {}, {"Retry-After": "10"})
        report, calls = self.run_cli(expected=2)
        self.assertEqual(report["status"], "incomplete")
        self.assertEqual(report["tickets"][0]["unavailable"], {
            "blocked_by": "not-found-or-no-access", "sub_issues": "rate-limited",
        })
        self.assertEqual(report["tickets"][2]["unavailable"], {"issue": "rate-limited"})
        self.assertEqual(len(calls), 4)

    def test_paginates_constructed_paths_and_rejects_duplicate_ids(self):
        endpoint = self.endpoint(3) + "/dependencies/blocked_by"
        self.routes[endpoint + PAGE_ONE] = (200, [
            self.issue(4, "Other prerequisite"),
        ], {"Link": '<https://different.test/wrong-target?page=77>; rel="next"'})
        self.routes[endpoint + PAGE_TWO] = (200, [self.issues[1]], {})
        report, calls = self.run_cli()
        self.assertIn(endpoint + PAGE_TWO, calls)
        self.assertEqual(len(report["tickets"][2]["remote"]["blocked_by"]), 2)
        self.routes[endpoint + PAGE_TWO] = (200, [self.issue(5, "Duplicated ID", id=904)], {})
        report, _ = self.run_cli(expected=2)
        self.assertEqual(report["tickets"][2]["unavailable"], {"blocked_by": "ambiguous-related-issue"})

    def test_reports_incomplete_when_returned_links_disagree_with_provider_summary(self):
        self.issues[2]["issue_dependencies_summary"] = {"total_blocked_by": 2}
        report, _ = self.run_cli(expected=2)
        story = report["tickets"][2]
        self.assertEqual(story["unavailable"], {"blocked_by": "relation-count-changed-or-incomplete"})
        self.assertNotIn("blocked_by", story["remote"])

    def test_rejects_source_change_during_provider_read(self):
        def change_mapping(endpoint):
            if endpoint == self.endpoint(3):
                (self.root / "mapping.json").write_text("{}")
        report, _ = self.run_cli(expected=2, on_read=change_mapping)
        self.assertEqual(report["status"], "invalid-input")
        self.assertIn("SOURCE_DRIFT: mapping.json", report["error"])

    def test_does_not_follow_repository_redirects(self):
        self.routes[REPO] = (301, {}, {"Location": "https://different.test/other"})
        report, calls = self.run_cli(expected=2)
        self.assertEqual(report["unavailable"], "redirected")
        self.assertEqual(calls, [REPO])
        handler = next(handler for handler in build_opener(github.RejectRedirect).handlers
                       if isinstance(handler, github.RejectRedirect))
        self.assertIsNone(handler.redirect_request(
            Request(github.API + REPO), None, 301, "Moved", Message(), "https://different.test/other",
        ))


if __name__ == "__main__":
    unittest.main()
