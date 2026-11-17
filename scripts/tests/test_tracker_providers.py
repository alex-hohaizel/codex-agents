"""Contract fixtures derived from the providers' documented HTTP operations."""

from copy import deepcopy
from email.message import Message
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from io import BytesIO
import json
from pathlib import Path
import socket
import sys
from threading import Thread
import unittest
from urllib.error import HTTPError
from urllib.parse import parse_qs, urlsplit
from urllib.request import ProxyHandler, Request, build_opener

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tracker_providers as providers


MARKER = "[codex-agents:" + "a" * 64 + "]"


class Response(BytesIO):
    def __init__(self, status, body):
        super().__init__(json.dumps(body).encode() if body is not None else b"")
        self.status = status
        self.headers = Message()
        self.headers["X-Request-Id"] = "fixture-1"


class MockServer:
    def __init__(self, fn):
        self.fn = fn
        self.requests = []

    def open(self, request, timeout):
        url = urlsplit(request.full_url)
        method = request.get_method()
        payload = json.loads(request.data) if request.data is not None else None
        call = {"method": method, "url": url, "payload": payload,
                "headers": {key.lower(): value for key, value in request.header_items()},
                "query": parse_qs(url.query, keep_blank_values=True)}
        self.requests.append(call)
        status, value = self.fn(call)
        response = Response(status, value)
        if status >= 300:
            raise HTTPError(request.full_url, status, "fixture", response.headers, response)
        return response


def uuid(n):
    return f"00000000-0000-0000-0000-{n:012x}"


def object_id(n):
    return f"{n:024x}"


class GitHubProviderTest(unittest.TestCase):
    def setUp(self):
        self.issue = None
        self.base = "/repos/sandbox/booking"
        self.writes = []

        def handle(call):
            path, method, payload = call["url"].path, call["method"], call["payload"]
            self.assertEqual(call["url"].netloc, "api.github.com")
            if path == self.base:
                return 200, {"id": 700, "full_name": "Sandbox/Booking", "has_issues": True}
            if path == self.base + "/issues" and method == "GET":
                self.assertEqual(call["query"]["state"], ["all"])
                return 200, [deepcopy(self.issue)] if self.issue else []
            if path == self.base + "/issues" and method == "POST":
                self.writes.append(("create", payload))
                self.issue = {"id": 701, "number": 7, "repository_url": "https://api.github.com" + self.base,
                              "title": payload["title"], "body": payload["body"], "state": "open",
                              "state_reason": None, "assignees": []}
                raise ConnectionResetError("fixture closed response after applying")
            if path == self.base + "/issues/7" and method == "GET":
                return 200, deepcopy(self.issue)
            if path == self.base + "/issues/7/parent":
                return 404, {}
            if path == self.base + "/issues/7/dependencies/blocked_by":
                return 200, []
            if path == self.base + "/issues/7" and method == "PATCH":
                self.writes.append(("update", payload))
                self.issue.update(payload)
                return 200, deepcopy(self.issue)
            self.fail(f"unexpected GitHub request: {method} {path}")

        self.config = {"provider": "github", "container": {"id": "700", "key": "Sandbox/Booking"},
                       "auth": {"token_env": "GITHUB_TOKEN"}}
        self.server = MockServer(handle)
        self.client = providers.build_provider(self.config, transport=self.server,
                                               environ={"GITHUB_TOKEN": "fixture-secret"})

    def test_lost_create_reply_and_marker_reconciliation_then_transition(self):
        with self.assertRaises(providers.ProviderError) as failed:
            self.client.create_item({"title": "Reserve loading dock", "marker": MARKER})
        self.assertTrue(failed.exception.uncertain)
        [found] = self.client.find_marker(MARKER)
        self.assertEqual(found["id"], "701")
        self.assertEqual(len(self.writes), 1)
        with self.assertRaisesRegex(providers.ProviderError, "existing-ticket-marker"):
            self.client.create_item({"title": "Reserve loading dock", "marker": MARKER})
        self.assertEqual(len(self.writes), 1)

        state = self.client.read_item("701", "7")
        self.assertEqual(state["blocker_ids"], [])
        self.client.update_item(state, {"status": "closed:completed"})
        self.assertEqual(self.client.read_item("701", "7")["status"], "closed:completed")
        self.assertEqual(self.writes[-1], ("update", {"state": "closed", "state_reason": "completed"}))
        self.assertNotIn("fixture-secret", json.dumps(self.client.receipts))

    def test_rejects_repo_identity_drift_and_redirect_before_user_data(self):
        calls = []
        for status, raw in ((200, {"id": 999, "full_name": "Sandbox/Booking", "has_issues": True}),
                            (302, {})):
            server = MockServer(lambda call: (status, raw))
            client = providers.build_provider(self.config, transport=server,
                                              environ={"GITHUB_TOKEN": "scoped"})
            with self.assertRaises(providers.ProviderError) as error:
                client.create_item({"title": "Reserve loading dock", "marker": MARKER})
            calls.append(error.exception.code)
            self.assertEqual(len(server.requests), 1)
            self.assertEqual(server.requests[0]["method"], "GET")
        self.assertEqual(calls, ["tracker-container-identity-mismatch", "provider-redirect-blocked"])

    def test_opt_in_native_milestone_and_exact_child_assignment(self):
        initiative = {}
        child = {"id": 701, "number": 7, "repository_url": "https://api.github.com" + self.base,
                 "title": "Mirror the sprint work", "body": None, "state": "open",
                 "state_reason": None, "assignees": [], "milestone": None}

        def serve(call):
            method, path, payload = call["method"], call["url"].path, call["payload"]
            if path == self.base:
                return 200, {"id": 700, "full_name": "Sandbox/Booking", "has_issues": True}
            if path == self.base + "/issues" and method == "GET":
                return 200, [child]
            if path == self.base + "/milestones" and method == "GET":
                return 200, [initiative] if initiative else []
            if path == self.base + "/milestones" and method == "POST":
                initiative.update({"id": 701, "number": 7, "state": "open",
                                   "url": "https://api.github.com" + self.base + "/milestones/7", **payload})
                return 201, initiative
            if path == self.base + "/milestones/7" and method == "GET":
                return 200, initiative
            if path == self.base + "/issues/7" and method == "GET":
                return 200, child
            if path == self.base + "/issues/7" and method == "PATCH":
                self.assertEqual(payload, {"milestone": 7})
                child["milestone"] = initiative
                return 200, child
            if path == self.base + "/issues/7/parent":
                return 404, {}
            if path == self.base + "/issues/7/dependencies/blocked_by":
                return 200, []
            self.fail(f"unexpected GitHub request: {method} {path}")

        self.config["options"] = {"initiatives": "milestones"}
        client = providers.build_provider(self.config, transport=MockServer(serve),
                                          environ={"GITHUB_TOKEN": "scoped"})
        self.assertEqual(client.verify_container(), self.config["container"])
        created = client.create_item({"title": "Release recovery work", "kind": "initiative", "marker": MARKER})
        self.assertEqual((created["id"], created["key"]), ("milestone:701", "milestone:7"))
        self.assertEqual({item["id"] for item in client.list_items()}, {"701", "milestone:701"})
        current = client.read_item("701", "7")
        client.update_item(current, {"parent_id": created["id"]})
        self.assertEqual(client.read_item("701", "7")["parent_id"], created["id"])


class LinearProviderTest(unittest.TestCase):
    def test_project_pagination_team_scope_and_native_mutations(self):
        project, team, pending, done, other_project = map(uuid, range(1, 6))
        item = {"id": uuid(12), "identifier": "OPS-12", "title": "Verify cancellation rules",
                "description": MARKER, "project": {"id": project}, "state": {"id": pending},
                "parent": None, "assignee": None}
        rows = {}

        def serve(call):
            self.assertEqual(call["url"].netloc, "api.linear.app")
            self.assertEqual(call["headers"]["authorization"], "scoped-linear-key")
            query, variables = call["payload"]["query"], call["payload"]["variables"]
            if "query CurrentProject" in query:
                self.assertEqual(variables["id"], project)
                return 200, {"data": {"project": {"id": project, "slugId": "project-x",
                            "teams": {"nodes": [{"id": team}], "pageInfo": {"hasNextPage": False}}}}}
            if "query ProjectIssues" in query:
                self.assertIn("includeArchived:true", query)
                cursor = variables["cursor"]
                if cursor is None and rows:
                    return 200, {"data": {"project": {"id": project, "issues": {
                        "nodes": list(rows.values()), "pageInfo": {"hasNextPage": True, "endCursor": "next"}}}}}
                self.assertIn(cursor, (None, "next"))
                return 200, {"data": {"project": {"id": project, "issues": {
                    "nodes": [], "pageInfo": {"hasNextPage": False, "endCursor": None}}}}}
            if "mutation CreateTicket" in query:
                self.assertEqual(variables["input"],
                                 {"teamId": team, "projectId": project, "title": item["title"],
                                  "stateId": pending, "description": MARKER})
                rows[item["id"]] = item
                return 200, {"data": {"issueCreate": {"success": True, "issue": item}}}
            if "query ExactIssue" in query:
                return 200, {"data": {"issue": item}}
            if "query BlockingIssues" in query:
                return 200, {"data": {"issue": {"id": item["id"], "inverseRelations": {
                    "nodes": [], "pageInfo": {"hasNextPage": False}}}}}
            if "mutation EditTicket" in query:
                self.assertEqual(variables, {"id": item["id"], "input": {"stateId": done}})
                item["state"]["id"] = done
                return 200, {"data": {"issueUpdate": {"success": True, "issue": item}}}
            self.fail(f"unexpected Linear query: {query}")

        server = MockServer(serve)
        client = providers.build_provider({"provider": "linear", "container": {"id": project},
                                           "auth": {"token_env": "LINEAR_API_KEY"},
                                           "options": {"team_id": team}},
                                          transport=server, environ={"LINEAR_API_KEY": "scoped-linear-key"})
        created = client.create_item({"title": item["title"], "marker": MARKER, "status": pending})
        self.assertEqual(created["id"], item["id"])
        [found] = client.find_marker(MARKER)
        current = client.read_item(found["id"], found["key"])
        client.update_item(current, {"status": done})
        self.assertEqual(client.read_item(item["id"])["status"], done)
        item["project"]["id"] = other_project
        with self.assertRaisesRegex(providers.ProviderError, "tracker-item-container-mismatch"):
            client.read_item(item["id"])


class JiraProviderTest(unittest.TestCase):
    def test_project_identity_marker_and_transition_by_destination_status(self):
        root, item_id, title = "730", "731", "Preserve reservation notes"
        item = None
        transitions = [{"id": "42", "to": {"id": "2"}, "isAvailable": True},
                       {"id": "43", "to": {"id": "2"}, "isAvailable": True}]

        def serve(call):
            nonlocal item
            method, path, body = call["method"], call["url"].path, call["payload"]
            api = "/rest/api/3"
            self.assertEqual(call["url"].netloc, "booking.atlassian.net")
            self.assertTrue(call["headers"]["authorization"].startswith("Basic "))
            if path == api + "/project/" + root:
                return 200, {"id": root, "key": "OPS"}
            if path == api + "/search/jql":
                self.assertEqual(body["jql"], "project = 730 ORDER BY id ASC")
                return 200, {"issues": [item] if item else [], "isLast": True}
            if path == api + "/issue" and method == "POST":
                fields = body["fields"]
                self.assertEqual(fields["issuetype"], {"id": "88"})
                self.assertEqual(fields["labels"], ["codex-agents-" + "a" * 64])
                item = {"id": item_id, "key": "OPS-7", "fields": {
                    "project": {"id": root}, "summary": fields["summary"], "status": {"id": "1"},
                    "labels": fields["labels"], "assignee": None}}
                return 201, {"id": item_id, "key": "OPS-7"}
            if path == api + "/issue/" + item_id:
                return 200, item
            if path == api + "/issue/" + item_id + "/transitions" and method == "GET":
                return 200, {"transitions": transitions}
            if path == api + "/issue/" + item_id + "/transitions" and method == "POST":
                self.assertEqual(body, {"transition": {"id": "42"}})
                item["fields"]["status"]["id"] = "2"
                return 204, None
            self.fail(f"unexpected Jira call: {method} {path}")

        server = MockServer(serve)
        client = providers.build_provider({"provider": "jira", "container": {"id": root, "key": "OPS"},
                                           "auth": {"token_env": "JIRA_TOKEN", "email_env": "JIRA_EMAIL"},
                                           "options": {"site": "booking", "issue_types": {"story": "88"}}},
                                          transport=server, environ={"JIRA_TOKEN": "scoped-jira-token",
                                                                     "JIRA_EMAIL": "bot@example.com"})
        created = client.create_item({"title": title, "marker": MARKER, "kind": "story"})
        self.assertEqual(created["marker"], MARKER)
        self.assertNotIn("update:blocker_ids", client.capabilities)
        with self.assertRaisesRegex(providers.ProviderError, "jira-transition-unavailable-or-ambiguous") as error:
            client.update_item(created, {"status": "2"})
        self.assertFalse(error.exception.uncertain)
        transitions.pop()
        client.update_item(created, {"status": "2"})
        self.assertEqual(client.read_item(item_id)["status"], "2")


class NotionProviderTest(unittest.TestCase):
    def test_provisioned_properties_and_readback_through_data_source(self):
        source, database, page = map(uuid, (8, 9, 10))
        schemas = {
            "Name": {"id": "title", "type": "title"},
            "Workflow": {"id": "status%3A", "type": "status",
                         "status": {"options": [{"id": "queue", "name": "Queued"}, {"id": "done", "name": "Done"}]}},
            "Sync": {"id": "marker", "type": "rich_text"},
        }
        data = {}
        values = {
            "Name": {"id": "title", "type": "title", "title": [{"plain_text": "Prepare venue"}]},
            "Workflow": {"id": "status%3A", "type": "status", "status": {"id": "queue", "name": "Queued"}},
            "Sync": {"id": "marker", "type": "rich_text", "rich_text": [{"plain_text": MARKER}]},
        }
        row = {"object": "page", "id": page, "parent": {"type": "data_source_id", "data_source_id": source},
               "properties": values}

        def serve(call):
            method, path, body = call["method"], call["url"].path, call["payload"]
            self.assertEqual(call["url"].netloc, "api.notion.com")
            self.assertEqual(call["headers"]["notion-version"], "2025-09-03")
            if path == "/v1/data_sources/" + source:
                return 200, {"object": "data_source", "id": source,
                             "parent": {"type": "database_id", "database_id": database}, "properties": schemas}
            if path == "/v1/data_sources/" + source + "/query":
                return 200, {"results": list(data.values()), "has_more": False, "next_cursor": None}
            if path == "/v1/pages" and method == "POST":
                self.assertEqual(body["parent"], {"type": "data_source_id", "data_source_id": source})
                self.assertEqual(body["properties"]["marker"]["rich_text"][0]["text"]["content"], MARKER)
                self.assertEqual(body["properties"]["status%3A"], {"status": {"id": "queue"}})
                data[page] = row
                return 200, row
            if path == "/v1/pages/" + page and method == "GET":
                return 200, row
            if path == "/v1/pages/" + page and method == "PATCH":
                self.assertEqual(body, {"properties": {"status%3A": {"status": {"id": "done"}}}})
                row["properties"]["Workflow"]["status"] = {"id": "done", "name": "Done"}
                return 200, row
            self.fail(f"unexpected Notion request: {method} {path}")

        client = providers.build_provider(
            {"provider": "notion", "container": {"id": source, "key": database},
             "auth": {"token_env": "NOTION_TOKEN"},
             "options": {"properties": {"title": "title", "status": "Workflow", "marker": "Sync"}}},
            transport=MockServer(serve), environ={"NOTION_TOKEN": "scoped-notion-token"})
        created = client.create_item({"title": "Prepare venue", "status": "Queued", "marker": MARKER})
        self.assertEqual([item["id"] for item in client.find_marker(MARKER)], [page])
        with self.assertRaisesRegex(providers.ProviderError, "notion-option-must-exist"):
            client.update_item(created, {"status": "unprovisioned"})
        client.update_item(created, {"status": "Done"})
        self.assertEqual(client.read_item(page)["status"], "Done")
        self.assertNotIn("update:parent_id", client.capabilities)


class TrelloProviderTest(unittest.TestCase):
    def test_moves_card_and_preserves_description_with_clickable_relation(self):
        board, foreign_board, backlog, done, main, blocker = map(object_id, range(20, 26))
        human = "Confirm checklist with operations.\n\nExisting internal notes."

        def card(identity, short, title, description, column=backlog):
            return {"id": identity, "shortLink": short, "name": title, "desc": description,
                    "idBoard": board, "idList": column, "closed": False, "idMembers": []}

        rows = {blocker: card(blocker, "blocking", "Approve venue", "An unrelated card body.")}
        blocked_column = False

        def serve(call):
            method, path, body = call["method"], call["url"].path, call["payload"]
            self.assertEqual(call["url"].netloc, "api.trello.com")
            self.assertTrue(call["headers"]["authorization"].startswith("OAuth "))
            self.assertNotIn("token", call["query"])
            if path == "/1/boards/" + board:
                return 200, {"id": board, "shortLink": "boardlink"}
            if path == "/1/boards/" + board + "/cards/all":
                return 200, list(rows.values())
            if path == "/1/lists/" + backlog:
                return 200, {"id": backlog, "idBoard": board, "closed": False}
            if path == "/1/lists/" + done:
                return 200, {"id": done, "idBoard": foreign_board if blocked_column else board, "closed": False}
            if path == "/1/cards" and method == "POST":
                rows[main] = card(main, "maincard", body["name"], body["desc"], body["idList"])
                return 200, rows[main]
            if path.startswith("/1/cards/") and method == "GET":
                return 200, rows[path.rsplit("/", 1)[1]]
            if path == "/1/cards/" + main and method == "PUT":
                self.assertIn("https://trello.com/c/blocking", body["desc"])
                self.assertTrue(body["desc"].startswith(human))
                rows[main].update(body)
                return 200, rows[main]
            self.fail(f"unexpected Trello call: {method} {path}")

        client = providers.build_provider({"provider": "trello", "container": {"id": board},
                                           "auth": {"key_env": "TRELLO_KEY", "token_env": "TRELLO_TOKEN"},
                                           "options": {"default_list_id": backlog}},
                                          transport=MockServer(serve),
                                          environ={"TRELLO_KEY": "fixture-key", "TRELLO_TOKEN": "fixture-token"})
        created = client.create_item({"title": "Finalise booking", "marker": MARKER, "description": human})
        blocked_column = True
        with self.assertRaisesRegex(providers.ProviderError, "trello-list-not-active-in-board"):
            client.update_item(created, {"status": done, "blocker_ids": [blocker]})
        self.assertEqual(client.read_item(main)["status"], backlog)
        blocked_column = False
        client.update_item(created, {"status": done, "blocker_ids": [blocker]})
        item = client.read_item(main)
        self.assertEqual((item["status"], item["blocker_ids"]), (done, [blocker]))
        self.assertEqual(item["marker"], MARKER)


class ProviderConfigurationTest(unittest.TestCase):
    def test_rejects_arbitrary_jira_origin_and_foreign_credential_references(self):
        config = {"provider": "jira", "container": {"id": "1"},
                  "auth": {"token_env": "JIRA_TOKEN", "email_env": "JIRA_EMAIL"},
                  "options": {"site": "custom.example.invalid"}}
        with self.assertRaisesRegex(providers.ProviderError, "invalid-jira-cloud-site"):
            providers.build_provider(config, environ={})
        config["options"]["site"] = "booking"
        config["auth"]["token_env"] = "GITHUB_TOKEN"
        with self.assertRaisesRegex(providers.ProviderError, "invalid-credential-environment-reference"):
            providers.build_provider(config, environ={"GITHUB_TOKEN": "must-not-be-used"})


class ProviderHttpRoundTripTest(unittest.TestCase):
    def test_socket_disconnect_after_create_leaves_one_visible_record(self):
        repo = "/repos/fixtures/atelier"
        state = {"writes": 0, "items": []}

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *args):
                pass

            def do_GET(self):
                path = urlsplit(self.path).path
                if path == repo:
                    data = {"id": 630, "full_name": "fixtures/atelier", "has_issues": True}
                elif path == repo + "/issues":
                    data = state["items"]
                else:
                    self.send_error(404)
                    return
                raw = json.dumps(data).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(raw)))
                self.end_headers()
                self.wfile.write(raw)

            def do_POST(self):
                if self.path != repo + "/issues" or self.headers.get("Authorization") != "Bearer fixture":
                    self.send_error(403)
                    return
                payload = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
                state["writes"] += 1
                state["items"].append({"id": 631, "number": state["writes"],
                                       "repository_url": "https://api.github.com" + repo,
                                       "title": payload["title"], "body": payload["body"],
                                       "state": "open", "state_reason": None, "assignees": []})
                self.connection.shutdown(socket.SHUT_RDWR)
                self.close_connection = True

        try:
            server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        except PermissionError:
            self.skipTest("loopback binds are unavailable in this environment")
        with server:
            worker = Thread(target=server.serve_forever, daemon=True)
            worker.start()
            client_transport = build_opener(ProxyHandler({}), providers.RejectRedirect())

            def loopback(request, *, timeout):
                supplied = urlsplit(request.full_url)
                self.assertEqual((supplied.scheme, supplied.netloc), ("https", "api.github.com"))
                origin = "http://127.0.0.1:" + str(server.server_port)
                wire = Request(supplied._replace(scheme="http", netloc=urlsplit(origin).netloc).geturl(),
                               data=request.data, headers=dict(request.header_items()),
                               method=request.get_method())
                return client_transport.open(wire, timeout=timeout)

            client = providers.build_provider({"provider": "github", "container": {
                "id": "630", "key": "fixtures/atelier"}, "auth": {"token_env": "GH_TOKEN"}},
                transport=loopback, environ={"GH_TOKEN": "fixture"})
            spec = {"title": "Record the recovery journal before updating the Codex suite", "marker": MARKER}
            try:
                with self.assertRaises(providers.ProviderError) as lost:
                    client.create_item(spec)
                self.assertTrue(lost.exception.uncertain)
                [observed] = client.find_marker(MARKER)
                self.assertEqual((observed["id"], observed["title"]), ("631", spec["title"]))
                with self.assertRaisesRegex(providers.ProviderError, "existing-ticket-marker"):
                    client.create_item(spec)
                self.assertEqual(state["writes"], 1)
            finally:
                server.shutdown()
                worker.join(timeout=2)


if __name__ == "__main__":
    unittest.main()
