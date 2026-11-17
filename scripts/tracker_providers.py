"""Provider implementations for a confirmed, explicitly mapped tracker container."""

import base64
import http.client
import json
import os
import re
import time
from urllib.error import HTTPError
from urllib.parse import quote, unquote, urlencode
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener

from contextlib import closing


MARKER = re.compile(r"\[codex-agents:[0-9a-f]{64}\]")
RECEIPT = re.compile(r"[A-Za-z0-9_.:-]{1,160}")
SAFE_ALIAS = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,159}")
UUID = re.compile(r"[0-9a-f]{8}(?:-[0-9a-f]{4}){3}-[0-9a-f]{12}")
OBJECT_ID = re.compile(r"[0-9a-f]{24}")
NUMBER = re.compile(r"[1-9][0-9]{0,18}")
MAX_BYTES = 8 * 1024 * 1024
MAX_PAGES = 30
PAGE = 50


class ProviderError(ValueError):
    """A provider failure. An uncertain mutation must be reconciled before retry."""

    def __init__(self, code, *, uncertain=False, status=None):
        self.code = code
        self.uncertain = uncertain
        self.status = status
        super().__init__(code)


def need(check, code):
    if not check:
        raise ProviderError(code)


def dictionary(value):
    need(isinstance(value, dict), "invalid-provider-object")
    return value


def array(value):
    need(isinstance(value, list), "invalid-provider-list")
    return value


def matches(value, pattern, code="invalid-provider-id"):
    if type(value) is int and pattern is NUMBER:
        value = str(value)
    need(isinstance(value, str) and pattern.fullmatch(value), code)
    if pattern is NUMBER:
        need(int(value) <= 2**63 - 1, code)
    return value


def item_text(value, *, limit=100000):
    need(isinstance(value, str) and 0 < len(value) <= limit and value.strip() and
         "\x00" not in value and not any("\ud800" <= c <= "\udfff" for c in value),
         "invalid-provider-text")
    return value


def ids(value, pattern):
    values = [matches(v, pattern) for v in array(value)]
    need(len(values) == len(set(values)), "duplicate-provider-id")
    return sorted(values)


def no_unknown(obj, fields, code):
    need(isinstance(obj, dict) and set(obj) <= fields, code)


def body_marker(body):
    if body is None:
        return None
    need(isinstance(body, str), "invalid-provider-body")
    values = [line for line in body.splitlines() if MARKER.fullmatch(line)]
    need(len(values) <= 1, "ambiguous-ticket-marker")
    return values[0] if values else None


def marker_body(marker, description=None):
    matches(marker, MARKER, "invalid-ticket-marker")
    if description is None:
        return marker
    item_text(description)
    need(body_marker(description) is None, "description-already-contains-marker")
    return description.rstrip() + "\n\n" + marker


def strict_pairs(pairs):
    output = {}
    for key, value in pairs:
        if key in output:
            raise ValueError("duplicate JSON key")
        output[key] = value
    return output


def invalid_constant(value):
    raise ValueError("invalid JSON constant")


class RejectRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class TrackerProvider:
    name = None
    origin = None
    id_pattern = None
    container_id_pattern = None
    option_keys = set()
    auth_keys = {"token_env"}
    optional_auth = False
    capabilities = frozenset({"read", "list", "create", "update:title", "update:status"})
    receipt_headers = ("x-request-id", "request-id")

    def __init__(self, config, transport, environ):
        no_unknown(config, {"provider", "container", "auth", "options"}, "invalid-provider-config")
        self.options = config.get("options", {})
        no_unknown(self.options, self.option_keys, "unknown-provider-option")
        auth = config.get("auth", {})
        no_unknown(auth, self.auth_keys, "unknown-provider-auth")
        container = config.get("container")
        no_unknown(container, {"id", "key"}, "invalid-provider-container")
        self.container_id = matches(container.get("id"), self.container_id_pattern or self.id_pattern,
                                    "invalid-container-id")
        self.container_key = container.get("key", self.container_id)
        self.configured_key = self.container_key
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "Codex-Agent-System-tracker-sync/1",
        }
        self.receipts = []
        self.deadline = time.monotonic() + 120
        self._verified = None
        self._open = transport or build_opener(ProxyHandler({}), RejectRedirect())
        self.configure(auth, environ)
        self.authenticated = bool(self.headers.get("Authorization"))

    def secret(self, auth, key, environ, optional=False):
        name = auth.get(key)
        if name is None and optional:
            return None
        names = {
            "github": r"(?:GH|GITHUB)(?:_[A-Z0-9]+)*",
            "linear": r"LINEAR(?:_[A-Z0-9]+)*",
            "jira": r"(?:JIRA|ATLASSIAN)(?:_[A-Z0-9]+)*",
            "notion": r"NOTION(?:_[A-Z0-9]+)*",
            "trello": r"TRELLO(?:_[A-Z0-9]+)*",
        }
        need(isinstance(name, str) and 1 <= len(name) <= 100 and re.fullmatch(names[self.name], name),
             "invalid-credential-environment-reference")
        suffixes = {
            "token_env": ("_TOKEN", "_API_KEY"),
            "key_env": ("_KEY",),
            "email_env": ("_EMAIL",),
        }
        need(name.endswith(suffixes[key]), "invalid-credential-environment-reference")
        value = environ.get(name)
        need(isinstance(value, str) and re.fullmatch(r"[!-~]{1,2048}", value),
             "credential-unavailable-or-invalid")
        return value

    def configure(self, auth, environ):
        token = self.secret(auth, "token_env", environ, self.optional_auth)
        if token:
            self.headers["Authorization"] = "Bearer " + token
        matches(self.container_key, SAFE_ALIAS, "invalid-container-key")

    def _request(self, method, path, operation, *, body=None, query=None, write=False, success=(200,)):
        if write:
            need(self.authenticated, "tracker-write-authentication-required")
        remaining = self.deadline - time.monotonic()
        need(remaining > 0, "tracker-deadline-exceeded")
        need(path.startswith("/") and not path.startswith("//") and "?" not in path and
             "#" not in path and "\\" not in path, "invalid-provider-path")
        suffix = "?" + urlencode(query) if query else ""
        data = None if body is None else json.dumps(body, ensure_ascii=False, allow_nan=False).encode()
        request = Request(self.origin + path + suffix, method=method, headers=self.headers, data=data)
        opener = self._open.open if hasattr(self._open, "open") else self._open
        try:
            with opener(request, timeout=min(10, remaining)) as response:
                status = response.status
                self._receipt(operation, status, response.headers)
                if status not in success:
                    raise ProviderError("unexpected-provider-status", uncertain=write, status=status)
                raw = response.read(MAX_BYTES + 1)
                headers = response.headers
        except HTTPError as error:
            with closing(error):
                status = error.code
                self._receipt(operation, status, error.headers)
            codes = {
                400: "provider-rejected-request", 401: "provider-authentication-required",
                403: "provider-forbidden", 404: "provider-not-found-or-no-access",
                409: "provider-conflict", 429: "provider-rate-limited",
            }
            code = "provider-redirect-blocked" if 300 <= status < 400 else codes.get(status, "provider-http-error")
            raise ProviderError(code, uncertain=write and (status >= 500 or status in {408, 409}),
                                status=status) from None
        except (OSError, http.client.HTTPException):
            self._receipt(operation, None, {})
            raise ProviderError("provider-network-error", uncertain=write) from None
        if len(raw) > MAX_BYTES:
            raise ProviderError("provider-response-too-large", uncertain=write)
        if not raw or status == 204:
            return None, headers
        try:
            return json.loads(raw.decode("utf-8"), object_pairs_hook=strict_pairs,
                              parse_constant=invalid_constant), headers
        except (ValueError, RecursionError):
            raise ProviderError("invalid-provider-json", uncertain=write) from None

    def _receipt(self, operation, status, headers):
        receipt = next((headers.get(key) for key in self.receipt_headers if headers.get(key)), "")
        self.receipts.append({"operation": operation, "http_status": status,
                              "request_id": receipt if isinstance(receipt, str) and RECEIPT.fullmatch(receipt)
                              else None})

    def _value(self, *args, **kwargs):
        return self._request(*args, **kwargs)[0]

    def verify_container(self):
        observed = self.read_container()
        need(observed["id"] == self.container_id and observed["key"] == self.container_key,
             "tracker-container-identity-mismatch")
        self._verified = observed
        return {"id": observed["id"], "key": self.configured_key}

    def _ensure_container(self):
        if self._verified is None:
            self.verify_container()

    def _normalized(self, *, id, key, title, status, parent_id=None, marker=None,
                    blocker_ids=None, assignee_ids=None, description=None):
        matches(id, self.id_pattern)
        if parent_id is not None:
            matches(parent_id, self.id_pattern)
        item = {"id": id, "key": key, "container_id": self.container_id,
                "title": item_text(title), "status": item_text(status, limit=256),
                "parent_id": parent_id, "marker": marker, "blocker_ids": blocker_ids}
        if assignee_ids is not None:
            item["assignee_ids"] = assignee_ids
        if description is not None:
            item["description"] = description
        return item

    def list_items(self):
        self._ensure_container()
        items = []
        seen = set()
        for row in self.raw_list():
            item = self.normalize(row, detail=False)
            need(item["id"] not in seen, "ambiguous-tracker-pagination")
            seen.add(item["id"])
            items.append(item)
        return items

    def read_item(self, id, key=None):
        self._ensure_container()
        id = matches(id, self.id_pattern)
        item = self.normalize(self.raw_item(id, key), detail=True)
        need(item["id"] == id and (key is None or item["key"] == key), "tracker-item-identity-mismatch")
        return item

    def find_marker(self, marker):
        matches(marker, MARKER, "invalid-ticket-marker")
        return [item for item in self.list_items() if item["marker"] == marker]

    def create_item(self, spec):
        need("create" in self.capabilities, "tracker-create-unavailable")
        no_unknown(spec, {"title", "marker", "description", "status", "parent_id", "kind", "assignee_ids"},
                   "invalid-create-specification")
        item_text(spec.get("title"), limit=250)
        matches(spec.get("marker"), MARKER, "invalid-ticket-marker")
        self.verify_container()
        need(self.authenticated, "tracker-write-authentication-required")
        need(not self.find_marker(spec["marker"]), "existing-ticket-marker")
        parent = spec.get("parent_id")
        if parent is not None:
            self.read_item(parent)
        start = len(self.receipts)
        try:
            item = self.do_create(spec)
            need(item["marker"] == spec["marker"], "created-ticket-marker-mismatch")
            return item
        except ProviderError as error:
            self._rethrow_after_mutation(error, start)

    def update_item(self, item, changes):
        need(isinstance(item, dict) and {"id", "key", "container_id"} <= set(item), "invalid-target-item")
        need(isinstance(changes, dict) and bool(changes) and
             all("update:" + field in self.capabilities for field in changes),
             "unsupported-tracker-change")
        if "title" in changes:
            item_text(changes["title"], limit=250)
        if "status" in changes:
            item_text(changes["status"], limit=256)
        if "parent_id" in changes and changes["parent_id"] is not None:
            matches(changes["parent_id"], self.id_pattern)
        if "blocker_ids" in changes:
            ids(changes["blocker_ids"], self.id_pattern)
        need(self.authenticated, "tracker-write-authentication-required")
        self.verify_container()
        need(item.get("container_id") == self.container_id, "tracker-item-container-mismatch")
        current = self.read_item(item["id"], item["key"])
        pinned = {"id", "key", "container_id", "title", "status", "parent_id",
                  "marker", "blocker_ids", "assignee_ids", "description"}
        need(set(changes) <= set(item), "tracker-change-precondition-missing")
        need(all(current.get(key) == item[key] for key in pinned if key in item), "tracker-item-changed")
        if "parent_id" in changes and changes["parent_id"] is not None:
            need(changes["parent_id"] != current["id"], "self-relation")
            self.read_item(changes["parent_id"])
        if "blocker_ids" in changes:
            need(current["id"] not in changes["blocker_ids"], "self-relation")
            for related_id in sorted(set(changes["blocker_ids"]) ^ set(current["blocker_ids"] or [])):
                self.read_item(related_id)
        start = len(self.receipts)
        try:
            self.do_update(current, {key: value for key, value in changes.items()
                                     if value != current.get(key)})
        except ProviderError as error:
            self._rethrow_after_mutation(error, start)

    def _rethrow_after_mutation(self, error, start):
        if error.uncertain or any(receipt["operation"].startswith("write:")
                                  and receipt["http_status"] in (200, 201, 202, 204)
                                  for receipt in self.receipts[start:]):
            raise ProviderError(error.code, uncertain=True, status=error.status) from None
        raise error


class GitHubProvider(TrackerProvider):
    name = "github"
    origin = "https://api.github.com"
    container_id_pattern = NUMBER
    id_pattern = re.compile(r"(?:milestone:)?[1-9][0-9]{0,18}")
    option_keys = {"initiatives"}
    optional_auth = True
    repo_pattern = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}/[A-Za-z0-9_.-]{1,100}")
    login_pattern = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}")
    states = {"open": {"state": "open"},
              "closed:completed": {"state": "closed", "state_reason": "completed"},
              "closed:not_planned": {"state": "closed", "state_reason": "not_planned"}}
    capabilities = TrackerProvider.capabilities | {
        "update:parent_id", "update:blocker_ids", "update:assignee_ids",
    }
    receipt_headers = ("x-github-request-id",)

    def configure(self, auth, environ):
        token = self.secret(auth, "token_env", environ, optional=True)
        matches(self.container_key, self.repo_pattern, "invalid-github-repository")
        short = self.container_key.split("/")[1].lower()
        need(short not in {".", ".."} and not short.endswith(".git"), "invalid-github-repository")
        self.container_key = self.container_key.lower()
        self.repo = "/repos/" + self.container_key
        representation = self.options.get("initiatives", "issues")
        need(representation in ("issues", "milestones"), "invalid-github-initiative-representation")
        self.milestones = representation == "milestones"
        self.headers.update({"Accept": "application/vnd.github+json",
                             "X-GitHub-Api-Version": "2026-03-10"})
        if token:
            self.headers["Authorization"] = "Bearer " + token

    def read_container(self):
        row = dictionary(self._value("GET", self.repo, "read:container"))
        need(row.get("has_issues") is True, "github-issues-unavailable")
        return {"id": matches(row.get("id"), NUMBER),
                "key": matches(row.get("full_name"), self.repo_pattern).lower()}

    def paginate(self, path, operation, **params):
        for page in range(1, MAX_PAGES + 1):
            rows, headers = self._request("GET", path, operation,
                                          query={**params, "per_page": 100, "page": page})
            rows = array(rows)
            need(len(rows) <= 100, "invalid-pagination-size")
            yield from rows
            link = headers.get("Link")
            if not link:
                return
            parts = re.split(r",\s*(?=<)", link)
            rel = [re.fullmatch(r'\s*<[^<>]+>;\s*rel="([a-z_-]+)"\s*', value) for value in parts]
            need(None not in rel, "invalid-pagination-link")
            next_count = sum(value.group(1) == "next" for value in rel)
            if next_count == 0:
                return
            need(next_count == 1 and rows, "invalid-pagination-link")
        raise ProviderError("tracker-pagination-limit")

    def raw_list(self):
        for row in self.paginate(self.repo + "/issues", "read:items", state="all"):
            if "pull_request" not in dictionary(row):
                yield row
        if self.milestones:
            for row in self.paginate(self.repo + "/milestones", "read:milestones", state="all"):
                yield {"milestone_item": dictionary(row)}

    def raw_item(self, id, key):
        if key is None:
            found = [item for item in self.list_items() if item["id"] == id]
            need(len(found) == 1, "tracker-item-not-in-container")
            key = found[0]["key"]
        if id.startswith("milestone:"):
            need(self.milestones and isinstance(key, str) and key.startswith("milestone:"),
                 "invalid-github-milestone-route")
            number = matches(key.removeprefix("milestone:"), NUMBER)
            row = self._value("GET", self.repo + "/milestones/" + number, "read:milestone")
            return {"milestone_item": dictionary(row)}
        key = matches(key, NUMBER, "invalid-github-issue-number")
        return self._value("GET", self.repo + "/issues/" + key, "read:item")

    def relation(self, row):
        row = dictionary(row)
        need("pull_request" not in row, "github-object-is-pull-request")
        return matches(row.get("id"), NUMBER)

    def read_parent(self, path, has_parent=False):
        try:
            return self.relation(self._value("GET", path + "/parent", "read:parent"))
        except ProviderError as error:
            if error.status == 404 and not has_parent:
                return None
            raise

    def normalize(self, value, *, detail):
        row = dictionary(value)
        if "milestone_item" in row:
            return self.normalize_milestone(row["milestone_item"])
        identity = self.relation(row)
        key = matches(row.get("number"), NUMBER)
        repository_url = row.get("repository_url")
        need(isinstance(repository_url, str) and repository_url.lower() == self.origin + self.repo,
             "tracker-item-container-mismatch")
        state = row.get("state")
        reason = row.get("state_reason")
        need(state in {"open", "closed"} and
             reason in {None, "completed", "reopened", "not_planned", "duplicate"},
             "invalid-github-state")
        parent_url = row.get("parent_issue_url")
        path = self.repo + "/issues/" + key
        # May be absent in list responses. Detail reads both exact relation surfaces.
        parent = self.read_parent(path, bool(parent_url)) if detail or parent_url else None
        if self.milestones and parent is None and row.get("milestone") is not None:
            parent = "milestone:" + matches(dictionary(row["milestone"]).get("id"), NUMBER)
        blockers = None
        if detail:
            blockers = ids([self.relation(v) for v in self.paginate(path + "/dependencies/blocked_by",
                                                                  "read:blockers")], NUMBER)
            summary = row.get("issue_dependencies_summary") or {}
            count = dictionary(summary).get("total_blocked_by")
            need(count is None or (type(count) is int and count == len(blockers)),
                 "github-blockers-incomplete")
        body = row.get("body")
        people = [dictionary(value).get("login") for value in array(row.get("assignees"))]
        return self._normalized(id=identity, key=key, title=row.get("title"),
                                status=state + (":" + reason if state == "closed" and reason else ""),
                                marker=body_marker(body), parent_id=parent, blocker_ids=blockers,
                                assignee_ids=ids(people, self.login_pattern), description=body)

    def normalize_milestone(self, row):
        need(self.milestones, "github-milestone-representation-unavailable")
        identity = matches(row.get("id"), NUMBER)
        key = matches(row.get("number"), NUMBER)
        path = self.origin + self.repo + "/milestones/" + key
        need(isinstance(row.get("url"), str) and row["url"].lower() == path,
             "tracker-item-container-mismatch")
        state = row.get("state")
        need(state in ("open", "closed"), "invalid-github-milestone-state")
        body = row.get("description")
        return self._normalized(id="milestone:" + identity, key="milestone:" + key,
                                title=row.get("title"), status="closed:completed" if state == "closed" else state,
                                description=body, marker=body_marker(body))

    def do_create(self, spec):
        need(spec.get("status") in {None, "open"} and spec.get("parent_id") is None,
             "github-create-needs-separate-status-or-parent-step")
        description = marker_body(spec["marker"], spec.get("description"))
        if self.milestones and spec.get("kind") == "initiative":
            need("assignee_ids" not in spec, "github-milestone-assignees-unsupported")
            row = self._value("POST", self.repo + "/milestones", "write:create-milestone",
                              body={"title": spec["title"], "description": description}, write=True, success=(201,))
            return self.normalize_milestone(dictionary(row))
        payload = {"title": spec["title"], "body": description}
        if "assignee_ids" in spec:
            payload["assignees"] = ids(spec["assignee_ids"], self.login_pattern)
        row = self._value("POST", self.repo + "/issues", "write:create", body=payload,
                          write=True, success=(201,))
        return self.normalize(row, detail=False)

    def do_update(self, current, changes):
        if current["id"].startswith("milestone:"):
            self.update_milestone(current, changes)
            return
        path = self.repo + "/issues/" + current["key"]
        payload = {}
        if "title" in changes:
            payload["title"] = changes["title"]
        if "status" in changes:
            need(changes["status"] in self.states, "unsupported-github-status")
            payload.update(self.states[changes["status"]])
        if "assignee_ids" in changes:
            payload["assignees"] = ids(changes["assignee_ids"], self.login_pattern)
        if payload:
            self._value("PATCH", path, "write:update", body=payload, write=True)
        if "parent_id" in changes:
            self.update_issue_parent(path, current, changes["parent_id"])
        if "blocker_ids" in changes:
            target = set(changes["blocker_ids"])
            old = set(current["blocker_ids"])
            path += "/dependencies/blocked_by"
            need(all(NUMBER.fullmatch(key) for key in target | old), "github-blocker-must-be-an-issue")
            for identity in sorted(target - old):
                self._value("POST", path, "write:add-blocker", body={"issue_id": int(identity)},
                            write=True, success=(201,))
            for identity in sorted(old - target):
                self._value("DELETE", path + "/" + identity, "write:remove-blocker",
                            write=True, success=(200, 204))

    def update_milestone(self, current, changes):
        need(set(changes) <= {"title", "status"}, "github-milestone-field-unsupported")
        payload = changes.copy()
        if "status" in changes:
            status = payload.pop("status")
            need(status in ("open", "closed:completed"), "github-milestone-status-unsupported")
            payload["state"] = "closed" if status == "closed:completed" else status
        if payload:
            number = current["key"].removeprefix("milestone:")
            self._value("PATCH", self.repo + "/milestones/" + number, "write:update-milestone",
                        body=payload, write=True)

    def update_issue_parent(self, path, current, target):
        old = current["parent_id"]
        target_milestone = target is not None and target.startswith("milestone:")
        old_milestone = old is not None and old.startswith("milestone:")
        if old and not old_milestone and (target is None or target_milestone):
            old_parent = self.read_item(old)
            self._value("DELETE", f"{self.repo}/issues/{old_parent['key']}/sub_issue",
                        "write:remove-parent", body={"sub_issue_id": int(current["id"])},
                        write=True, success=(200, 204))
        if target_milestone or (target is None and old_milestone):
            number = None if target is None else int(self.read_item(target)["key"].removeprefix("milestone:"))
            self._value("PATCH", path, "write:set-milestone", body={"milestone": number}, write=True)
        elif target is not None:
            parent = self.read_item(target)
            self._value("POST", f"{self.repo}/issues/{parent['key']}/sub_issues", "write:add-parent",
                        body={"sub_issue_id": int(current["id"]), "replace_parent": old is not None
                              and not old_milestone}, write=True, success=(201,))


class LinearProvider(TrackerProvider):
    name = "linear"
    origin = "https://api.linear.app"
    id_pattern = UUID
    option_keys = {"team_id", "auth_mode"}
    capabilities = GitHubProvider.capabilities
    item_fields = "id identifier title description state { id } project { id } parent { id } assignee { id }"

    def configure(self, auth, environ):
        token = self.secret(auth, "token_env", environ)
        mode = self.options.get("auth_mode", "api-key")
        need(mode in {"api-key", "oauth"}, "invalid-linear-auth-mode")
        self.headers["Authorization"] = token if mode == "api-key" else "Bearer " + token
        matches(self.container_key, SAFE_ALIAS, "invalid-container-key")
        self.team_id = self.options.get("team_id")
        if self.team_id is not None:
            matches(self.team_id, UUID, "invalid-linear-team-id")
        else:
            self.capabilities = self.capabilities - {"create"}

    def gql(self, query, variables, operation, *, write=False):
        row = self._value("POST", "/graphql", operation, body={"query": query, "variables": variables},
                          write=write)
        need(isinstance(row, dict), "invalid-linear-envelope")
        if row.get("errors"):
            # Linear can return partial data alongside an error. Do not use that snapshot.
            raise ProviderError("linear-graphql-error", uncertain=write)
        return dictionary(row.get("data"))

    def read_container(self):
        query = ("query CurrentProject($id:String!) { project(id:$id) { id slugId "
                 "teams(first:50) { nodes { id } pageInfo { hasNextPage } } } }")
        row = dictionary(self.gql(query, {"id": self.container_id}, "read:container").get("project"))
        identity = matches(row.get("id"), UUID)
        key = identity if self.container_key == self.container_id else matches(row.get("slugId"), SAFE_ALIAS)
        if self.team_id is not None:
            teams = dictionary(row.get("teams"))
            known = [dictionary(team).get("id") for team in array(teams.get("nodes"))]
            need(self.team_id in known, "linear-team-not-in-project")
        return {"id": identity, "key": key}

    def connection(self, query, variables, root, field, operation, expected_id):
        seen = set()
        cursor = None
        for _ in range(MAX_PAGES):
            row = dictionary(self.gql(query, {**variables, "cursor": cursor}, operation).get(root))
            need(matches(row.get("id"), UUID) == expected_id, "tracker-paginated-identity-mismatch")
            page = dictionary(row.get(field))
            nodes, info = array(page.get("nodes")), dictionary(page.get("pageInfo"))
            need(len(nodes) <= PAGE and type(info.get("hasNextPage")) is bool, "invalid-linear-page")
            yield from nodes
            if not info["hasNextPage"]:
                return
            cursor = item_text(info.get("endCursor"), limit=4096)
            need(cursor not in seen and bool(nodes), "invalid-linear-cursor")
            seen.add(cursor)
        raise ProviderError("tracker-pagination-limit")

    def raw_list(self):
        query = ("query ProjectIssues($id:String!,$cursor:String) { project(id:$id) { id "
                 "issues(first:50,after:$cursor,includeArchived:true) { nodes { " + self.item_fields +
                 " } pageInfo { hasNextPage endCursor } } } }")
        yield from self.connection(query, {"id": self.container_id}, "project", "issues",
                                   "read:items", self.container_id)

    def raw_item(self, id, key):
        query = "query ExactIssue($id:String!) { issue(id:$id) { " + self.item_fields + " } }"
        return self.gql(query, {"id": id}, "read:item").get("issue")

    def relation_rows(self, id):
        query = ("query BlockingIssues($id:String!,$cursor:String) { issue(id:$id) { id "
                 "inverseRelations(first:50,after:$cursor) { nodes { id type issue { id } "
                 "relatedIssue { id } } pageInfo { hasNextPage endCursor } } } }")
        result = {}
        for row in self.connection(query, {"id": id}, "issue", "inverseRelations", "read:blockers", id):
            row = dictionary(row)
            if row.get("type") != "blocks":
                continue
            source = matches(dictionary(row.get("issue")).get("id"), UUID)
            target = matches(dictionary(row.get("relatedIssue")).get("id"), UUID)
            need(target == id and source not in result, "invalid-linear-blocker")
            result[source] = matches(row.get("id"), UUID)
        return result

    def normalize(self, value, *, detail):
        row = dictionary(value)
        identity = matches(row.get("id"), UUID)
        key = matches(row.get("identifier"), SAFE_ALIAS)
        need(matches(dictionary(row.get("project")).get("id"), UUID) == self.container_id,
             "tracker-item-container-mismatch")
        state = matches(dictionary(row.get("state")).get("id"), UUID)
        parent = row.get("parent")
        assignee = row.get("assignee")
        body = row.get("description")
        return self._normalized(id=identity, key=key, title=row.get("title"), status=state,
                                parent_id=matches(dictionary(parent).get("id"), UUID) if parent else None,
                                assignee_ids=[matches(dictionary(assignee).get("id"), UUID)] if assignee else [],
                                blocker_ids=sorted(self.relation_rows(identity)) if detail else None,
                                marker=body_marker(body), description=body)

    def single_assignee(self, value):
        people = ids(value, UUID)
        need(len(people) <= 1, "linear-allows-one-assignee")
        return people[0] if people else None

    def do_create(self, spec):
        need(self.team_id is not None, "linear-team-required-for-create")
        payload = {"teamId": self.team_id, "projectId": self.container_id, "title": spec["title"],
                   "description": marker_body(spec["marker"], spec.get("description"))}
        if spec.get("status") is not None:
            payload["stateId"] = matches(spec["status"], UUID, "invalid-linear-state")
        if spec.get("parent_id") is not None:
            payload["parentId"] = spec["parent_id"]
        if "assignee_ids" in spec:
            payload["assigneeId"] = self.single_assignee(spec["assignee_ids"])
        query = ("mutation CreateTicket($input:IssueCreateInput!) { issueCreate(input:$input) "
                 "{ success issue { " + self.item_fields + " } } }")
        result = dictionary(self.gql(query, {"input": payload}, "write:create", write=True).get("issueCreate"))
        need(result.get("success") is True, "linear-create-failed")
        return self.normalize(result.get("issue"), detail=False)

    def do_update(self, current, changes):
        payload = {}
        if "title" in changes:
            payload["title"] = changes["title"]
        if "status" in changes:
            payload["stateId"] = matches(changes["status"], UUID, "invalid-linear-state")
        if "parent_id" in changes:
            payload["parentId"] = changes["parent_id"]
        if "assignee_ids" in changes:
            payload["assigneeId"] = self.single_assignee(changes["assignee_ids"])
        if payload:
            query = ("mutation EditTicket($id:String!,$input:IssueUpdateInput!) "
                     "{ issueUpdate(id:$id,input:$input) { success issue { id project { id } } } }")
            result = dictionary(self.gql(query, {"id": current["id"], "input": payload},
                                         "write:update", write=True).get("issueUpdate"))
            result_issue = dictionary(result.get("issue"))
            need(result.get("success") is True and result_issue.get("id") == current["id"]
                 and dictionary(result_issue.get("project")).get("id") == self.container_id,
                 "linear-update-not-confirmed")
        if "blocker_ids" in changes:
            old = self.relation_rows(current["id"])
            need(set(old) == set(current["blocker_ids"]), "tracker-blockers-changed")
            target = set(changes["blocker_ids"])
            for blocker in sorted(target - set(old)):
                query = ("mutation AddBlocker($input:IssueRelationCreateInput!) { "
                         "issueRelationCreate(input:$input) { success } }")
                result = dictionary(self.gql(query, {"input": {"issueId": blocker,
                                                               "relatedIssueId": current["id"], "type": "blocks"}},
                                             "write:add-blocker", write=True).get("issueRelationCreate"))
                need(result.get("success") is True, "linear-add-blocker-not-confirmed")
            for blocker in sorted(set(old) - target):
                query = "mutation RemoveBlocker($id:String!) { issueRelationDelete(id:$id) { success } }"
                result = dictionary(self.gql(query, {"id": old[blocker]}, "write:remove-blocker",
                                             write=True).get("issueRelationDelete"))
                need(result.get("success") is True, "linear-remove-blocker-not-confirmed")


class JiraProvider(TrackerProvider):
    name = "jira"
    id_pattern = NUMBER
    option_keys = {"site", "cloud_id", "issue_types", "block_link_type_id", "block_link_inward"}
    auth_keys = {"token_env", "email_env"}
    project_key = re.compile(r"[A-Z][A-Z0-9_]{1,29}")
    issue_key = re.compile(r"[A-Z][A-Z0-9_]{1,29}-[1-9][0-9]{0,18}")
    account_id = re.compile(r"[A-Za-z0-9_.:-]{1,128}")
    label = re.compile(r"codex-agents-([0-9a-f]{64})")
    capabilities = GitHubProvider.capabilities
    fields = ["project", "summary", "status", "parent", "labels", "issuelinks", "assignee"]
    api = "/rest/api/3"

    def configure(self, auth, environ):
        site = matches(self.options.get("site"), re.compile(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?"),
                       "invalid-jira-cloud-site")
        self.origin = "https://" + site + ".atlassian.net"
        cloud_id = self.options.get("cloud_id")
        if cloud_id is not None:
            matches(cloud_id, UUID, "invalid-jira-cloud-id")
            self.origin = "https://api.atlassian.com"
            self.api = "/ex/jira/" + cloud_id + self.api
        if self.container_key != self.container_id:
            matches(self.container_key, self.project_key, "invalid-jira-project-key")
        token = self.secret(auth, "token_env", environ)
        email = self.secret(auth, "email_env", environ)
        need(re.fullmatch(r"[^:\s@]+@[^:\s@]+\.[^:\s@]+", email), "invalid-jira-account-reference")
        self.headers["Authorization"] = "Basic " + base64.b64encode((email + ":" + token).encode()).decode()
        self.issue_types = self.options.get("issue_types", {})
        no_unknown(self.issue_types, {"initiative", "epic", "story", "bug", "spike", "default"},
                   "invalid-jira-issue-type-mapping")
        self.issue_types = {key: matches(value, NUMBER, "invalid-jira-issue-type")
                            for key, value in self.issue_types.items()}
        if not self.issue_types:
            self.capabilities = self.capabilities - {"create"}
        self.link_type = self.options.get("block_link_type_id")
        self.link_inward = self.options.get("block_link_inward", "is blocked by")
        if self.link_type is not None:
            self.link_type = matches(self.link_type, NUMBER, "invalid-jira-block-link-type")
            item_text(self.link_inward, limit=200)
        else:
            self.capabilities = self.capabilities - {"update:blocker_ids"}

    def read_container(self):
        row = dictionary(self._value("GET", self.api + "/project/" + self.container_id, "read:container"))
        identity = matches(row.get("id"), NUMBER)
        key = identity if self.container_key == self.container_id else matches(row.get("key"), self.project_key)
        if self.link_type is not None:
            row = dictionary(self._value("GET", self.api + "/issueLinkType/" + self.link_type,
                                         "read:block-link-type"))
            need(matches(row.get("id"), NUMBER) == self.link_type and row.get("inward") == self.link_inward,
                 "jira-block-link-type-mismatch")
        return {"id": identity, "key": key}

    def raw_list(self):
        cursor = None
        seen = set()
        for _ in range(MAX_PAGES):
            payload = {"jql": "project = " + self.container_id + " ORDER BY id ASC",
                       "maxResults": PAGE, "fields": self.fields}
            if cursor is not None:
                payload["nextPageToken"] = cursor
            row = dictionary(self._value("POST", self.api + "/search/jql", "read:items", body=payload))
            issues = array(row.get("issues"))
            need(len(issues) <= PAGE and type(row.get("isLast")) is bool, "invalid-jira-search-page")
            yield from issues
            if row["isLast"]:
                return
            cursor = item_text(row.get("nextPageToken"), limit=8192)
            need(cursor not in seen and issues, "invalid-jira-search-cursor")
            seen.add(cursor)
        raise ProviderError("tracker-pagination-limit")

    def raw_item(self, id, key):
        return self._value("GET", self.api + "/issue/" + id, "read:item",
                           query={"fields": ",".join(self.fields)})

    def blockers(self, fields):
        if self.link_type is None:
            return None
        result = {}
        for link in array(fields.get("issuelinks")):
            link = dictionary(link)
            if matches(dictionary(link.get("type")).get("id"), NUMBER) != self.link_type:
                continue
            if "inwardIssue" in link:
                related = matches(dictionary(link["inwardIssue"]).get("id"), NUMBER)
                need(related not in result, "ambiguous-jira-blocker")
                result[related] = matches(link.get("id"), NUMBER)
        return result

    def normalize(self, value, *, detail):
        row = dictionary(value)
        fields = dictionary(row.get("fields"))
        identity = matches(row.get("id"), NUMBER)
        key = matches(row.get("key"), self.issue_key)
        project = dictionary(fields.get("project"))
        need(matches(project.get("id"), NUMBER) == self.container_id,
             "tracker-item-container-mismatch")
        labels = array(fields.get("labels"))
        markers = [match for label in labels if isinstance(label, str)
                   if (match := self.label.fullmatch(label))]
        need(len(markers) <= 1, "ambiguous-ticket-marker")
        marker = "[codex-agents:" + markers[0][1] + "]" if markers else None
        state = matches(dictionary(fields.get("status")).get("id"), NUMBER)
        parent, assignee = fields.get("parent"), fields.get("assignee")
        blockers = self.blockers(fields)
        return self._normalized(
            id=identity, key=key, title=fields.get("summary"), status=state, marker=marker,
            parent_id=matches(dictionary(parent).get("id"), NUMBER) if parent else None,
            assignee_ids=[matches(dictionary(assignee).get("accountId"), self.account_id)] if assignee else [],
            blocker_ids=sorted(blockers) if blockers is not None else None,
        )

    def assignee_value(self, value):
        people = ids(value, self.account_id)
        need(len(people) <= 1, "jira-allows-one-assignee")
        return {"accountId": people[0]} if people else None

    def do_create(self, spec):
        kind = spec.get("kind", "default")
        need(isinstance(kind, str), "invalid-jira-issue-type")
        issue_type = self.issue_types.get(kind, self.issue_types.get("default"))
        need(issue_type is not None, "jira-issue-type-required-for-create")
        need(spec.get("status") is None, "jira-create-status-requires-follow-up")
        fields = {"project": {"id": self.container_id}, "issuetype": {"id": issue_type},
                  "summary": spec["title"], "labels": ["codex-agents-" + spec["marker"][14:-1]]}
        if spec.get("parent_id") is not None:
            fields["parent"] = {"id": spec["parent_id"]}
        description = spec.get("description")
        if description is not None:
            item_text(description)
            fields["description"] = {"type": "doc", "version": 1, "content": [
                {"type": "paragraph", "content": [{"type": "text", "text": line}]}
                if line else {"type": "paragraph"} for line in description.splitlines()
            ]}
        if "assignee_ids" in spec:
            fields["assignee"] = self.assignee_value(spec["assignee_ids"])
        result = dictionary(self._value("POST", self.api + "/issue", "write:create", body={"fields": fields},
                                        write=True, success=(201,)))
        return self.read_item(matches(result.get("id"), NUMBER), matches(result.get("key"), self.issue_key))

    def do_update(self, current, changes):
        path = self.api + "/issue/" + current["id"]
        fields = {}
        if "title" in changes:
            fields["summary"] = changes["title"]
        if "parent_id" in changes:
            fields["parent"] = {"id": changes["parent_id"]} if changes["parent_id"] else None
        if "assignee_ids" in changes:
            fields["assignee"] = self.assignee_value(changes["assignee_ids"])
        transition = None
        if "status" in changes:
            status = matches(changes["status"], NUMBER, "invalid-jira-status")
            options = dictionary(self._value("GET", path + "/transitions", "read:transitions"))
            choices = [dictionary(row) for row in array(options.get("transitions"))]
            available = [row for row in choices
                         if dictionary(row.get("to")).get("id") == status
                         and row.get("isAvailable", True) is True]
            need(len(available) == 1, "jira-transition-unavailable-or-ambiguous")
            transition = matches(available[0].get("id"), NUMBER)
        if fields:
            self._value("PUT", path, "write:update", body={"fields": fields}, write=True, success=(204,))
        if transition is not None:
            self._value("POST", path + "/transitions", "write:transition",
                        body={"transition": {"id": transition}}, write=True, success=(204,))
        if "blocker_ids" in changes:
            raw = dictionary(self.raw_item(current["id"], None))
            old = self.blockers(dictionary(raw.get("fields")))
            need(old is not None and set(old) == set(current["blocker_ids"]), "tracker-blockers-changed")
            target = set(changes["blocker_ids"])
            for blocker in sorted(target - set(old)):
                self._value("POST", self.api + "/issueLink", "write:add-blocker",
                            body={"type": {"id": self.link_type}, "inwardIssue": {"id": blocker},
                                  "outwardIssue": {"id": current["id"]}}, write=True, success=(201,))
            for blocker in sorted(set(old) - target):
                self._value("DELETE", self.api + "/issueLink/" + old[blocker], "write:remove-blocker",
                            write=True, success=(204,))


class NotionProvider(TrackerProvider):
    name = "notion"
    origin = "https://api.notion.com"
    id_pattern = UUID
    option_keys = {"properties", "status_type"}
    capability_properties = {
        "parent_id": "parent", "blocker_ids": "blockers", "assignee_ids": "assignees",
    }
    receipt_headers = ("x-request-id", "request-id")

    def configure(self, auth, environ):
        super().configure(auth, environ)
        self.headers["Notion-Version"] = "2025-09-03"
        matches(self.container_key, UUID, "invalid-notion-database-id")
        self.selectors = self.options.get("properties")
        keys = {"title", "status", "marker", "parent", "blockers", "assignees", "kind", "description"}
        no_unknown(self.selectors, keys, "invalid-notion-property-map")
        need({"title", "status", "marker"} <= set(self.selectors), "missing-notion-property-map")
        declared = [item_text(value, limit=200) for value in self.selectors.values()]
        need(len(declared) == len(set(declared)), "ambiguous-notion-property-map")
        status_type = self.options.get("status_type", "status")
        need(status_type in {"status", "select"}, "invalid-notion-status-type")
        self.property_types = {"title": "title", "status": status_type, "marker": "rich_text",
                               "parent": "relation", "blockers": "relation", "assignees": "people",
                               "kind": "select", "description": "rich_text"}
        self.capabilities = self.capabilities | {
            "update:" + key for key, field in self.capability_properties.items() if field in self.selectors
        }
        self.properties = {}
        self.property_options = {}

    def from_properties(self, props, selector):
        candidates = [dictionary(value) for key, value in dictionary(props).items()
                      if key == selector or (isinstance(value, dict) and value.get("id") == selector)]
        need(len(candidates) == 1, "notion-property-missing-or-ambiguous")
        return candidates[0]

    def read_container(self):
        row = dictionary(self._value("GET", "/v1/data_sources/" + self.container_id, "read:container"))
        need(row.get("object") == "data_source", "invalid-notion-data-source")
        identity = matches(row.get("id"), UUID)
        parent = dictionary(row.get("parent"))
        need(parent.get("type") == "database_id", "invalid-notion-data-source-parent")
        database = matches(parent.get("database_id"), UUID)
        key = identity if self.container_key == self.container_id else database
        fields = {}
        property_options = {}
        for logical, selector in self.selectors.items():
            property_schema = self.from_properties(row.get("properties"), selector)
            kind = self.property_types[logical]
            need(property_schema.get("type") == kind, "notion-property-type-mismatch")
            property_id = item_text(property_schema.get("id"), limit=200)
            fields[logical] = property_id
            if kind == "relation":
                relation = dictionary(property_schema.get("relation"))
                relation_target = relation.get("data_source_id")
                if relation_target is not None:
                    need(relation_target == self.container_id, "notion-cross-source-relation")
                else:
                    # A single database can have multiple data sources. Require the exact relation source.
                    raise ProviderError("notion-relation-data-source-unavailable")
            if kind in {"status", "select"}:
                options = array(dictionary(property_schema.get(kind)).get("options"))
                observed = {}
                for raw in options:
                    raw = dictionary(raw)
                    label = item_text(raw.get("name"), limit=256)
                    need(label not in observed, "ambiguous-notion-option")
                    observed[label] = item_text(raw.get("id"), limit=100)
                property_options[logical] = observed
        need(len(set(fields.values())) == len(fields), "ambiguous-notion-property-map")
        self.properties, self.property_options = fields, property_options
        return {"id": identity, "key": key}

    def raw_list(self):
        cursor = None
        seen = set()
        for _ in range(MAX_PAGES):
            payload = {"page_size": PAGE}
            if cursor is not None:
                payload["start_cursor"] = cursor
            row = dictionary(self._value("POST", "/v1/data_sources/" + self.container_id + "/query",
                                        "read:items", body=payload))
            results = array(row.get("results"))
            need(len(results) <= PAGE and type(row.get("has_more")) is bool, "invalid-notion-page")
            yield from results
            if not row["has_more"]:
                return
            cursor = item_text(row.get("next_cursor"), limit=4096)
            need(cursor not in seen and bool(results), "invalid-notion-cursor")
            seen.add(cursor)
        raise ProviderError("tracker-pagination-limit")

    def raw_item(self, id, key):
        return self._value("GET", "/v1/pages/" + id, "read:item")

    def prop(self, page, logical):
        kind = self.property_types[logical]
        prop = self.from_properties(page.get("properties"), self.properties[logical])
        need(prop.get("type") == kind, "invalid-notion-page-property")
        return prop

    def text_value(self, page, logical):
        prop = self.prop(page, logical)
        values = array(prop.get(self.property_types[logical]))
        texts = [dictionary(value).get("plain_text") for value in values]
        need(all(isinstance(text, str) for text in texts), "invalid-notion-rich-text")
        return "".join(texts)

    def relation(self, page, logical, detail):
        if logical not in self.properties:
            return None
        value = self.prop(page, logical)
        property_id = self.properties[logical]
        inline = array(value.get("relation"))
        need(type(value.get("has_more", False)) is bool, "invalid-notion-relation-page")
        if not value.get("has_more"):
            return ids([dictionary(node).get("id") for node in inline], UUID)
        if not detail:
            return None
        seen = set()
        cursor = None
        found = []
        for _ in range(MAX_PAGES):
            qs = {"page_size": PAGE}
            if cursor is not None:
                qs["start_cursor"] = cursor
            path = "/v1/pages/" + page["id"] + "/properties/" + quote(unquote(property_id), safe="")
            result = dictionary(self._value("GET", path, "read:relation", query=qs))
            results = array(result.get("results"))
            need(len(results) <= PAGE and type(result.get("has_more")) is bool, "invalid-notion-relation-page")
            for raw in results:
                entry = dictionary(raw)
                need(entry.get("type") == "relation", "invalid-notion-relation-item")
                found.append(dictionary(entry.get("relation")).get("id"))
            if not result["has_more"]:
                return ids(found, UUID)
            cursor = item_text(result.get("next_cursor"), limit=4096)
            need(cursor not in seen and bool(results), "invalid-notion-cursor")
            seen.add(cursor)
        raise ProviderError("tracker-pagination-limit")

    def normalize(self, value, *, detail):
        row = dictionary(value)
        need(row.get("object") == "page", "invalid-notion-page-kind")
        identity = matches(row.get("id"), UUID)
        parent = dictionary(row.get("parent"))
        need(parent.get("type") == "data_source_id" and parent.get("data_source_id") == self.container_id,
             "tracker-item-container-mismatch")
        status_type = self.property_types["status"]
        state = self.prop(row, "status").get(status_type)
        marker = self.text_value(row, "marker")
        # Ordinary pages can contain a different marker property value, but never claim it for this system.
        if not MARKER.fullmatch(marker):
            marker = None
        parents = self.relation(row, "parent", detail)
        need(not parents or len(parents) == 1, "multiple-notion-parent-pages")
        people = None
        if "assignees" in self.properties:
            people = ids([dictionary(person).get("id")
                          for person in array(self.prop(row, "assignees").get("people"))], UUID)
        return self._normalized(id=identity, key=identity, title=self.text_value(row, "title"),
                                status=dictionary(state).get("name") if state is not None else "unset",
                                marker=marker, parent_id=parents[0] if parents else None,
                                assignee_ids=people, blocker_ids=self.relation(row, "blockers", detail),
                                description=self.text_value(row, "description")
                                if "description" in self.properties else None)

    def rich_text(self, content):
        return [{"type": "text", "text": {"content": content[i:i + 2000]}}
                for i in range(0, len(content), 2000)]

    def option_value(self, logical, label):
        item_text(label, limit=256)
        options = self.property_options[logical]
        need(label in options, "notion-option-must-exist")
        return {self.property_types[logical]: {"id": options[label]}}

    def people_value(self, people):
        return {"people": [{"object": "user", "id": person} for person in ids(people, UUID)]}

    def rel_value(self, values):
        related = ids(values, UUID)
        need(len(related) <= 100, "notion-relation-write-limit")
        return {"relation": [{"id": value} for value in related]}

    def do_create(self, spec):
        keys = self.properties
        fields = {keys["title"]: {"title": self.rich_text(spec["title"])},
                  keys["marker"]: {"rich_text": self.rich_text(spec["marker"])}}
        if spec.get("status") is not None:
            fields[keys["status"]] = self.option_value("status", spec["status"])
        if spec.get("parent_id") is not None:
            need("parent" in keys, "notion-parent-property-unavailable")
            fields[keys["parent"]] = self.rel_value([spec["parent_id"]])
        if spec.get("kind") is not None and "kind" in keys:
            fields[keys["kind"]] = self.option_value("kind", spec["kind"])
        if spec.get("description") is not None:
            need("description" in keys, "notion-description-property-unavailable")
            fields[keys["description"]] = {"rich_text": self.rich_text(item_text(spec["description"]))}
        if "assignee_ids" in spec:
            need("assignees" in keys, "notion-assignee-property-unavailable")
            fields[keys["assignees"]] = self.people_value(spec["assignee_ids"])
        response = self._value("POST", "/v1/pages", "write:create", body={
            "parent": {"type": "data_source_id", "data_source_id": self.container_id}, "properties": fields,
        }, write=True, success=(200,))
        return self.normalize(response, detail=False)

    def do_update(self, current, changes):
        keys = self.properties
        fields = {}
        if "title" in changes:
            fields[keys["title"]] = {"title": self.rich_text(changes["title"])}
        if "status" in changes:
            fields[keys["status"]] = self.option_value("status", changes["status"])
        if "parent_id" in changes:
            fields[keys["parent"]] = self.rel_value([changes["parent_id"]] if changes["parent_id"] else [])
        if "blocker_ids" in changes:
            fields[keys["blockers"]] = self.rel_value(changes["blocker_ids"])
        if "assignee_ids" in changes:
            fields[keys["assignees"]] = self.people_value(changes["assignee_ids"])
        if fields:
            self._value("PATCH", "/v1/pages/" + current["id"], "write:update",
                        body={"properties": fields}, write=True)


class TrelloProvider(TrackerProvider):
    name = "trello"
    origin = "https://api.trello.com"
    id_pattern = OBJECT_ID
    auth_keys = {"token_env", "key_env"}
    option_keys = {"default_list_id", "lists_by_kind", "auth_mode"}
    short_link = re.compile(r"[A-Za-z0-9]{6,24}")
    card_fields = "id,idBoard,idList,shortLink,name,desc,closed,idMembers"
    capabilities = GitHubProvider.capabilities
    relations_start = "<!-- codex-agents:trello-relations:v1 -->"
    relations_end = "<!-- /codex-agents:trello-relations:v1 -->"
    relation_line = re.compile(
        r"(Parent|Blocked by): \[Open card\]\(https://trello\.com/c/([A-Za-z0-9]{6,24})\) "
        r"<!-- ([0-9a-f]{24}) -->"
    )
    receipt_headers = ("x-trello-request-id", "x-request-id", "atl-traceid")

    def configure(self, auth, environ):
        token = self.secret(auth, "token_env", environ)
        mode = self.options.get("auth_mode", "api-key")
        need(mode in {"api-key", "oauth"}, "invalid-trello-auth-mode")
        if mode == "api-key":
            key = self.secret(auth, "key_env", environ)
            need(re.fullmatch(r"[A-Za-z0-9_.-]{1,2048}", key) and
                 re.fullmatch(r"[A-Za-z0-9_.-]{1,2048}", token), "invalid-trello-credentials")
            self.headers["Authorization"] = f'OAuth oauth_consumer_key="{key}", oauth_token="{token}"'
        else:
            need("key_env" not in auth, "trello-oauth-does-not-use-api-key")
            self.headers["Authorization"] = "Bearer " + token
        matches(self.container_key, self.short_link, "invalid-trello-board-key")
        self.default_list = self.options.get("default_list_id")
        if self.default_list is not None:
            matches(self.default_list, OBJECT_ID, "invalid-trello-list-id")
        self.kind_lists = self.options.get("lists_by_kind", {})
        no_unknown(self.kind_lists, {"initiative", "epic", "story", "bug", "spike"},
                   "invalid-trello-kind-mapping")
        for value in self.kind_lists.values():
            matches(value, OBJECT_ID, "invalid-trello-list-id")
        if self.default_list is None and not self.kind_lists:
            self.capabilities = self.capabilities - {"create"}

    def read_container(self):
        row = dictionary(self._value("GET", "/1/boards/" + self.container_id, "read:container",
                                     query={"fields": "id,shortLink"}))
        identity = matches(row.get("id"), OBJECT_ID)
        key = identity if self.container_key == self.container_id else matches(row.get("shortLink"), self.short_link)
        return {"id": identity, "key": key}

    def read_list(self, identity):
        identity = matches(identity, OBJECT_ID, "invalid-trello-list-id")
        row = dictionary(self._value("GET", "/1/lists/" + identity, "read:list",
                                     query={"fields": "id,idBoard,closed"}))
        need(row.get("id") == identity and row.get("idBoard") == self.container_id and row.get("closed") is False,
             "trello-list-not-active-in-board")
        return identity

    def raw_list(self):
        cursor = None
        seen = set()
        for _ in range(MAX_PAGES):
            query = {"fields": self.card_fields, "limit": 1000}
            if cursor is not None:
                query["before"] = cursor
            rows = array(self._value("GET", "/1/boards/" + self.container_id + "/cards/all",
                                     "read:items", query=query))
            need(len(rows) <= 1000, "invalid-trello-page")
            yield from rows
            if len(rows) < 1000:
                return
            cursor = matches(dictionary(rows[-1]).get("id"), OBJECT_ID)
            need(cursor not in seen, "invalid-trello-cursor")
            seen.add(cursor)
        raise ProviderError("tracker-pagination-limit")

    def raw_item(self, id, key):
        return self._value("GET", "/1/cards/" + id, "read:item", query={"fields": self.card_fields})

    def description_relations(self, description):
        need(isinstance(description, str), "invalid-trello-description")
        if self.relations_start not in description and self.relations_end not in description:
            return description, None, []
        separator = "\n\n" + self.relations_start + "\n"
        prefix, boundary, suffix = description.partition(separator)
        need(bool(boundary) and suffix.endswith("\n" + self.relations_end) and
             self.relations_start not in prefix and self.relations_end not in prefix,
             "malformed-trello-managed-relations")
        parent = None
        blockers = []
        for line in suffix[:-(1 + len(self.relations_end))].split("\n"):
            match = self.relation_line.fullmatch(line)
            need(match is not None, "malformed-trello-managed-relations")
            if match[1] == "Parent":
                need(parent is None, "multiple-trello-parents")
                parent = match[3]
            else:
                blockers.append(match[3])
        return prefix, parent, ids(blockers, OBJECT_ID)

    def patched_description(self, prefix, parent, blockers):
        lines = []
        relations = ([("Parent", parent)] if parent else []) + [("Blocked by", value) for value in blockers]
        for label, identity in relations:
            related = self.read_item(identity)
            lines.append(f"{label}: [Open card](https://trello.com/c/{related['key']}) <!-- {identity} -->")
        if not lines:
            return prefix
        return prefix + "\n\n" + self.relations_start + "\n" + "\n".join(lines) + "\n" + self.relations_end

    def normalize(self, value, *, detail):
        row = dictionary(value)
        identity = matches(row.get("id"), OBJECT_ID)
        key = matches(row.get("shortLink"), self.short_link)
        need(row.get("idBoard") == self.container_id, "tracker-item-container-mismatch")
        list_id = matches(row.get("idList"), OBJECT_ID)
        need(type(row.get("closed")) is bool, "invalid-trello-card-archive-status")
        body = row.get("desc")
        prefix, parent, blockers = self.description_relations(body)
        return self._normalized(id=identity, key=key, title=row.get("name"),
                                status="archived" if row["closed"] else list_id,
                                marker=body_marker(prefix), parent_id=parent, blocker_ids=blockers,
                                assignee_ids=ids(row.get("idMembers"), OBJECT_ID), description=body)

    def do_create(self, spec):
        kind = spec.get("kind")
        need(kind is None or isinstance(kind, str), "invalid-trello-kind")
        requested = spec.get("status") or self.kind_lists.get(kind, self.default_list)
        need(requested is not None, "trello-list-required-for-create")
        list_id = self.read_list(requested)
        prefix = marker_body(spec["marker"], spec.get("description"))
        self.description_relations(prefix)
        payload = {"name": spec["title"], "idList": list_id,
                   "desc": self.patched_description(prefix, spec.get("parent_id"), [])}
        if "assignee_ids" in spec:
            payload["idMembers"] = ids(spec["assignee_ids"], OBJECT_ID)
        row = dictionary(self._value("POST", "/1/cards", "write:create", body=payload, write=True,
                                     success=(200, 201)))
        return self.read_item(matches(row.get("id"), OBJECT_ID))

    def do_update(self, current, changes):
        payload = {}
        if "title" in changes:
            payload["name"] = changes["title"]
        if "status" in changes:
            value = changes["status"]
            if value == "archived":
                payload["closed"] = True
            else:
                payload["idList"] = self.read_list(value)
                payload["closed"] = False
        if "assignee_ids" in changes:
            payload["idMembers"] = ",".join(ids(changes["assignee_ids"], OBJECT_ID))
        if "parent_id" in changes or "blocker_ids" in changes:
            prefix, parent, blockers = self.description_relations(current["description"])
            payload["desc"] = self.patched_description(prefix, changes.get("parent_id", parent),
                                                       sorted(changes.get("blocker_ids", blockers)))
        if payload:
            self._value("PUT", "/1/cards/" + current["id"], "write:update", body=payload, write=True)


PROVIDERS = {
    "github": GitHubProvider,
    "linear": LinearProvider,
    "jira": JiraProvider,
    "notion": NotionProvider,
    "trello": TrelloProvider,
}


def build_provider(config, *, transport=None, environ=None):
    """Validate an explicit provider binding and supply a bounded client."""
    need(isinstance(config, dict), "invalid-provider-config")
    name = config.get("provider")
    need(isinstance(name, str) and name in PROVIDERS, "unsupported-tracker-provider")
    return PROVIDERS[name](config, transport, os.environ if environ is None else environ)
