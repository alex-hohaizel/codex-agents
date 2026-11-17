#!/usr/bin/env python3
"""Compare a project ticket projection with explicitly mapped GitHub.com issues."""

import argparse
from datetime import datetime, timezone
import http.client
import json
import os
from pathlib import Path
import re
import sys
import time
from urllib.error import HTTPError
from urllib.request import HTTPRedirectHandler, Request, build_opener

sys.dont_write_bytecode = True
import ticket_tree as trees

context = trees.context
API = "https://api.github.com"
API_VERSION = "2022-11-28"
MAPPING = "atelier.ticket-github-map/1"
REPORT = "atelier.ticket-github-reconciliation/1"
REPOSITORY = re.compile(r"[A-Za-z0-9][A-Za-z0-9-]{0,38}/[A-Za-z0-9_.-]{1,100}")
REQUEST_ID = re.compile(r"[A-Za-z0-9:-]{1,100}")
LINK = re.compile(r'\s*<[^<>]+>;\s*rel="([^"]+)"\s*')
PAGE_SIZE = 100
MAX_PAGES = 30
MAX_RESPONSE = 8 * 1024 * 1024


class GitHubUnavailable(ValueError):
    def __init__(self, code):
        self.code = code


class RejectRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


class GitHubClient:
    """Read GitHub with a deadline and record receipt IDs without storing response bodies."""

    def __init__(self, token=None, *, opener=None):
        self.opener = build_opener(RejectRedirect) if opener is None else opener
        self.headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": API_VERSION,
            "User-Agent": "codex-agent-system-ticket-reconciliation",
        }
        if token:
            context.require(re.fullmatch(r"[A-Za-z0-9_.-]{1,1024}", token),
                            "invalid GitHub token format")
            self.headers["Authorization"] = "Bearer " + token
        self.deadline = time.monotonic() + 60
        self.reads = []
        self.stop_reason = None

    def record(self, endpoint, status, headers):
        receipt = headers.get("X-GitHub-Request-Id", "")
        self.reads.append({
            "endpoint": endpoint, "http_status": status,
            "request_id": receipt if REQUEST_ID.fullmatch(receipt) else None,
        })

    def get(self, endpoint):
        if self.stop_reason:
            raise GitHubUnavailable(self.stop_reason)
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise GitHubUnavailable("read-deadline")
        request = Request(API + endpoint, headers=self.headers, method="GET")
        try:
            with self.opener.open(request, timeout=min(10, remaining)) as response:
                self.record(endpoint, response.status, response.headers)
                if response.status != 200:
                    raise GitHubUnavailable("unexpected-http-status")
                raw = response.read(MAX_RESPONSE + 1)
                links = response.headers.get("Link")
        except HTTPError as error:
            with error:
                self.record(endpoint, error.code, error.headers)
                if error.code == 429 or (error.code == 403 and
                                          (error.headers.get("X-RateLimit-Remaining") == "0"
                                           or error.headers.get("Retry-After"))):
                    self.stop_reason = "rate-limited"
                    raise GitHubUnavailable(self.stop_reason) from None
                if 300 <= error.code < 400:
                    raise GitHubUnavailable("redirected") from None
                if error.code == 404:
                    raise GitHubUnavailable("not-found-or-no-access") from None
                raise GitHubUnavailable({
                    401: "authentication-required", 403: "forbidden", 410: "gone",
                }.get(error.code, "http-error")) from None
        except (OSError, http.client.HTTPException):
            self.record(endpoint, None, {})
            raise GitHubUnavailable("network-read-failed") from None
        if len(raw) > MAX_RESPONSE:
            raise GitHubUnavailable("response-too-large")
        try:
            return json.loads(raw.decode("utf-8"), object_pairs_hook=context.pairs,
                              parse_constant=context.constant, parse_float=context.finite_float), links
        except (ValueError, RecursionError):
            raise GitHubUnavailable("invalid-json-response") from None

    def listed(self, endpoint):
        for page in range(1, MAX_PAGES + 1):
            items, link = self.get(f"{endpoint}?per_page={PAGE_SIZE}&page={page}")
            if not isinstance(items, list) or len(items) > PAGE_SIZE:
                raise GitHubUnavailable("invalid-list-response")
            yield from items
            if not link:
                return
            entries = [LINK.fullmatch(entry) for entry in re.split(r",\s*(?=<)", link)]
            if None in entries:
                raise GitHubUnavailable("invalid-pagination")
            rels = [entry.group(1) for entry in entries]
            if "next" not in rels:
                return
            if not items or rels.count("next") != 1:
                raise GitHubUnavailable("invalid-pagination")
        raise GitHubUnavailable("pagination-limit")


def positive_int(value):
    return type(value) is int and 0 < value <= 2**63 - 1


def repo_name(value):
    return bool(isinstance(value, str) and REPOSITORY.fullmatch(value)
                and value.split("/")[1] not in {".", ".."}
                and not value.lower().endswith(".git"))


def mapping_for(snapshot, ref, board):
    raw = snapshot.read(ref)
    data = context.json_object(raw)
    context.require(set(data) == {"schema_version", "project_id", "repository", "tickets"}
                    and data["schema_version"] == MAPPING,
                    "invalid GitHub issue mapping")
    context.require(data["project_id"] == board["project_id"],
                    "GitHub issue mapping belongs to a different project")
    repo = data["repository"]
    context.require(isinstance(repo, dict) and set(repo) == {"full_name", "id"}
                    and repo_name(repo["full_name"]) and positive_int(repo["id"]),
                    "expected GitHub owner/repository and stable positive repository ID")
    entries = data["tickets"]
    context.require(isinstance(entries, list) and 1 <= len(entries) <= context.MAX_IDS,
                    "expected a bounded nonempty GitHub issue mapping")
    known = {row["id"] for row in board["tickets"]}
    bindings, numbers, ids = {}, set(), set()
    for row in entries:
        context.require(isinstance(row, dict) and set(row) == {"ticket_id", "number", "id"}
                        and isinstance(row["ticket_id"], str) and positive_int(row["number"])
                        and positive_int(row["id"]), "invalid GitHub ticket binding")
        key = row["ticket_id"]
        context.require(key in known and key not in bindings
                        and row["number"] not in numbers and row["id"] not in ids,
                        "unknown ticket or ambiguous GitHub issue mapping")
        bindings[key] = {"repository": repo["full_name"].lower(), "number": row["number"], "id": row["id"]}
        numbers.add(row["number"])
        ids.add(row["id"])
    return repo, bindings, {"path": ref, "sha256": context.digest(raw)}


def issue_key(issue):
    if not isinstance(issue, dict) or "pull_request" in issue:
        raise GitHubUnavailable("not-an-issue")
    url, number, issue_id = (issue.get(key) for key in ("repository_url", "number", "id"))
    prefix = API + "/repos/"
    if not isinstance(url, str) or not url.startswith(prefix) or not repo_name(url[len(prefix):]):
        raise GitHubUnavailable("unrecognized-issue-repository")
    if not positive_int(number) or not positive_int(issue_id):
        raise GitHubUnavailable("invalid-issue-identity")
    return {"repository": url[len(prefix):].lower(), "number": number, "id": issue_id}


def issue_status(issue):
    state, reason = issue.get("state"), issue.get("state_reason")
    if state == "open" and reason in (None, "reopened"):
        return {"state": state}
    if state == "closed" and reason in (None, "completed", "not_planned", "duplicate"):
        return {"state": state, "reason": reason}
    raise GitHubUnavailable("unrecognized-issue-state")


def github_relations(client, endpoint):
    related = {}
    seen_ids = set()
    for row in client.listed(endpoint):
        issue = issue_key(row)
        number = issue["number"]
        namespace = issue["repository"], number
        if namespace in related or issue["id"] in seen_ids:
            raise GitHubUnavailable("ambiguous-related-issue")
        related[namespace] = {**issue, **issue_status(row)}
        seen_ids.add(issue["id"])
    return list(related.values())


def verify_repository(client, repo):
    path = f"/repos/{repo['full_name']}"
    observed, _ = client.get(path)
    if (not isinstance(observed, dict) or not positive_int(observed.get("id"))
            or observed["id"] != repo["id"] or not repo_name(observed.get("full_name"))
            or observed["full_name"].lower() != repo["full_name"].lower()):
        raise GitHubUnavailable("repository-identity-mismatch")
    return path, observed


def read_issue(client, repo_path, binding):
    endpoint = f"{repo_path}/issues/{binding['number']}"
    issue, _ = client.get(endpoint)
    if issue_key(issue) != binding:
        raise GitHubUnavailable("issue-identity-mismatch")
    return endpoint, issue


def expected_relation_count(issue, field):
    summary_name, count_name = {
        "blocked_by": ("issue_dependencies_summary", "total_blocked_by"),
        "sub_issues": ("sub_issues_summary", "total"),
    }[field]
    summary = issue.get(summary_name)
    return summary.get(count_name) if isinstance(summary, dict) else None


def relation_comparison(local, observed, bindings):
    ids = {item["id"]: item for item in observed}
    expected = {bindings[key]["id"]: bindings[key] for key in local if key in bindings}
    extra_or_changed = [
        item for item in observed
        if expected.get(item["id"]) != {key: item[key] for key in ("repository", "number", "id")}
    ]
    missing_or_changed = [
        item for issue_id, item in expected.items()
        if any(ids.get(issue_id, {}).get(key) != value for key, value in item.items())
    ]
    return {
        "observed": observed, "missing_or_changed": missing_or_changed,
        "unexpected_or_changed": extra_or_changed,
    }


def compare_ticket(client, repo_path, ticket, bindings):
    binding = bindings[ticket["id"]]
    row = {
        "ticket_id": ticket["id"], "issue": binding,
        "local": {key: ticket[key] for key in (
            "recorded_status", "board_state", "acceptance_status",
            "effective_prerequisites", "execution_disposition",
        )},
        "remote": {}, "differences": [], "unavailable": {},
    }
    try:
        endpoint, issue = read_issue(client, repo_path, binding)
        status = issue_status(issue)
        if not isinstance(issue.get("title"), str) or not issue["title"].strip():
            raise GitHubUnavailable("invalid-issue-title")
        title_sha = context.digest(issue["title"].encode("utf-8"))
    except (GitHubUnavailable, UnicodeError) as error:
        row["unavailable"]["issue"] = error.code if isinstance(error, GitHubUnavailable) else "invalid-issue-title"
        return row

    expected_status = {
        "accepted": {"state": "closed", "reason": "completed"},
        "deferred": {"state": "closed", "reason": "not_planned"},
    }.get(ticket["recorded_status"], {"state": "open"})
    row["remote"] = {**status, "title_sha256": title_sha}
    if status != expected_status:
        row["differences"].append({"field": "status", "expected": expected_status})
    expected_hash = context.digest(ticket["title"].encode("utf-8"))
    if title_sha != expected_hash:
        row["differences"].append({"field": "title", "expected_sha256": expected_hash})

    parent = ticket["parent"]
    if parent is not None and parent not in bindings:
        row["differences"].append({"field": "parent", "unmapped_local_tickets": [parent]})

    for field, suffix, local in (
        ("blocked_by", "dependencies/blocked_by", ticket["depends_on"]),
        ("sub_issues", "sub_issues", ticket["children"]),
    ):
        unmapped = [key for key in local if key not in bindings]
        if unmapped:
            row["differences"].append({"field": field, "unmapped_local_tickets": unmapped})
        try:
            observed = github_relations(client, f"{endpoint}/{suffix}")
            count = expected_relation_count(issue, field)
            if count is not None and (type(count) is not int or count != len(observed)):
                raise GitHubUnavailable("relation-count-changed-or-incomplete")
            matched = relation_comparison(local, observed, bindings)
        except GitHubUnavailable as error:
            row["unavailable"][field] = error.code
            continue
        row["remote"][field] = matched.pop("observed")
        if any(matched.values()):
            row["differences"].append({"field": field, **matched})
    return row


def reconcile(root, projection, mapping, client):
    snapshot = trees.Snapshot(root)
    board = trees.project_board(root, projection, snapshot=snapshot)
    repo, bindings, mapping_pin = mapping_for(snapshot, mapping, board)
    report = {
        "schema_version": REPORT, "api_version": API_VERSION,
        "access": "read-only", "scope": "mapped-tickets",
        "repository": repo, "repository_verified": False,
        "project_id": board["project_id"], "native_revision": board["native_revision"],
        "projection": board["projection"], "mapping": mapping_pin,
        "unsupported_local_acceptance": [
            key for key in board["unsupported_acceptance_claims"] if key in bindings
        ],
        "started_at": datetime.now(timezone.utc).isoformat(),
        "reads": client.reads, "tickets": [],
    }
    try:
        repo_path, observed = verify_repository(client, repo)
        report["repository_verified"] = True
        if observed.get("has_issues") is False:
            raise GitHubUnavailable("issues-disabled")
    except GitHubUnavailable as error:
        report["unavailable"] = error.code
    else:
        report["tickets"] = [compare_ticket(client, repo_path, row, bindings)
                             for row in board["tickets"] if row["id"] in bindings]
    snapshot.verify_unchanged()
    report["completed_at"] = datetime.now(timezone.utc).isoformat()
    report["status"] = "match"
    if report["unsupported_local_acceptance"] or any(row["differences"] for row in report["tickets"]):
        report["status"] = "diverged"
    if report.get("unavailable") or any(row["unavailable"] for row in report["tickets"]):
        report["status"] = "incomplete"
    return report


def main(argv=None, *, client=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", required=True, type=Path, help="canonical absolute project root")
    parser.add_argument("--projection", required=True, help="ticket projection path inside the project")
    parser.add_argument("--mapping", required=True, help="GitHub issue mapping path inside the project")
    parser.add_argument("--require-clean", action="store_true", help="exit 2 if issues and tickets differ")
    args = parser.parse_args(argv)
    try:
        if client is None:
            client = GitHubClient(os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"))
        result = reconcile(args.root, args.projection, args.mapping, client)
    except (context.ContextError, OSError, UnicodeError) as error:
        print(json.dumps({"status": "invalid-input", "error": str(error)}), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 2 if (result["status"] == "incomplete" or
                 (args.require_clean and result["status"] != "match")) else 0


if __name__ == "__main__":
    sys.exit(main())
