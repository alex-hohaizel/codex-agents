#!/usr/bin/env python3
"""Preview, apply once, and read back an authorized change to mapped GitHub issues."""

import argparse
from datetime import datetime, timezone
import http.client
import json
import os
from pathlib import Path
import stat
import sys
from urllib.error import HTTPError
from urllib.request import Request

sys.dont_write_bytecode = True
import ticket_github as github
import ticket_replan_store as store
from ticket_dispatch import create_ledger

context = github.context
PREVIEW = "atelier.ticket-github-preview/2"
LEDGER = "atelier.ticket-github-operations/1"
RESULT = "atelier.ticket-github-update/1"
CHANGES = ("title", "state", "add-blocker", "remove-blocker", "add-child", "remove-child")
# A timeout, transport error, 5xx or unrecognized response leaves the effect uncertain.
REJECTIONS = {400, 401, 403, 404, 405, 410, 412, 422, 429}


class WriteClient(github.GitHubClient):
    """Send a single approved request and retain only its envelope."""

    def __init__(self, token=None, *, opener=None):
        super().__init__(token, opener=opener)
        self.writes = []

    def mutate(self, request):
        context.require("Authorization" in self.headers, "a GitHub Issues write credential is required")
        envelope = Request(
            github.API + request["endpoint"], method=request["method"],
            headers={**self.headers, "Content-Type": "application/json"},
            data=context.canonical(request["body"]) if request["body"] is not None else None,
        )
        status, headers = None, {}
        try:
            with self.opener.open(envelope, timeout=10) as response:
                status, headers = response.status, response.headers
        except HTTPError as error:
            with error:
                status, headers = error.code, error.headers or {}
        except (OSError, http.client.HTTPException):
            pass
        if status == 429 or (status == 403 and (
            headers.get("X-RateLimit-Remaining") == "0" or headers.get("Retry-After")
        )):
            self.stop_reason = "rate-limited"
        receipt_id = headers.get("X-GitHub-Request-Id", "")
        receipt = {
            "method": request["method"], "endpoint": request["endpoint"],
            "http_status": status, "request_id": receipt_id if github.REQUEST_ID.fullmatch(receipt_id) else None,
            "response": "success" if status == request["expected_http_status"] else (
                "rejected" if status in REJECTIONS else "uncertain"
            ),
        }
        self.writes.append(receipt)
        return receipt


def edge_change(change):
    return change.startswith(("add-", "remove-"))


def relation(change):
    return ("sub_issues", "children") if change.endswith("child") else ("blocked_by", "depends_on")


def identity_key(row):
    return row["repository"], row["number"], row["id"]


def expected_state(ticket):
    recorded = ticket["recorded_status"]
    if recorded == "accepted":
        context.require(ticket["acceptance_status"] == "supported"
                        and ticket["execution_disposition"] == "satisfied",
                        "a completion export requires checked, available local acceptance")
        return {"state": "closed", "reason": "completed"}
    if recorded == "deferred":
        return {"state": "closed", "reason": "not_planned"}
    return {"state": "open"}


def project_binding(root, projection, mapping, ticket_id, change, related_id):
    context.require(change in CHANGES, "unsupported GitHub issue change")
    context.require(edge_change(change) == bool(related_id) and related_id != ticket_id,
                    "relationship changes require one other mapped ticket")
    snapshot = github.trees.Snapshot(root)
    board = github.trees.project_board(root, projection, snapshot=snapshot)
    repo, bindings, mapping_pin = github.mapping_for(snapshot, mapping, board)
    context.require(ticket_id in bindings and (related_id is None or related_id in bindings),
                    "selected tickets must have explicit GitHub issue mappings")
    ticket = next(row for row in board["tickets"] if row["id"] == ticket_id)
    related = bindings[related_id] if related_id is not None else None
    if related:
        _, local = relation(change)
        context.require((related_id in ticket[local]) == change.startswith("add-"),
                        "the selected relationship change disagrees with the project projection")
    binding = {
        "repository": repo, "issue": bindings[ticket_id], "related_issue": related,
        "project_id": board["project_id"], "native_revision": board["native_revision"],
        "checkout_sha256": context.digest(os.fsencode(root)),
        "projection": board["projection"], "mapping": mapping_pin,
        "sources": {path: context.digest(data) for path, data in sorted(snapshot.paths.items())},
        "ticket_id": ticket_id, "related_ticket_id": related_id, "change": change,
    }
    return snapshot, binding, ticket


def read_field(client, binding):
    repo_path, repo = github.verify_repository(client, binding["repository"])
    if repo.get("has_issues") is False:
        raise github.GitHubUnavailable("issues-disabled")
    endpoint, issue = github.read_issue(client, repo_path, binding["issue"])
    change = binding["change"]
    if change == "state":
        return endpoint, github.issue_status(issue)
    if change == "title":
        title = issue.get("title")
        if not isinstance(title, str) or not title.strip():
            raise github.GitHubUnavailable("invalid-issue-title")
        return endpoint, {"title_sha256": context.digest(title.encode("utf-8"))}

    # Confirm the related issue's independent identity before considering a link.
    related = binding["related_issue"]
    github.read_issue(client, repo_path, related)
    field, _ = relation(change)
    suffix = "sub_issues" if field == "sub_issues" else "dependencies/blocked_by"
    rows = github.github_relations(client, f"{endpoint}/{suffix}")
    count = github.expected_relation_count(issue, field)
    if count is not None and (type(count) is not int or count != len(rows)):
        raise github.GitHubUnavailable("relation-count-changed-or-incomplete")
    if any((row["id"] == related["id"]
            or (row["repository"], row["number"]) == (related["repository"], related["number"]))
           and identity_key(row) != identity_key(related) for row in rows):
        raise github.GitHubUnavailable("related-issue-identity-mismatch")
    return endpoint, sorted(
        ({key: row[key] for key in ("repository", "number", "id")} for row in rows),
        key=identity_key,
    )


def desired_change(binding, ticket, endpoint, before):
    change = binding["change"]
    if change == "title":
        title = ticket["title"]
        after = {"title_sha256": context.digest(title.encode("utf-8"))}
        return after, ("PATCH", endpoint, {"title": title}, 200)
    if change == "state":
        after = expected_state(ticket)
        context.require(not (before.get("state") == after["state"] == "closed" and before != after),
                        "GitHub cannot change a close reason in place")
        body = {"state": after["state"]}
        if "reason" in after:
            body["state_reason"] = after["reason"]
        return after, ("PATCH", endpoint, body, 200)

    related = binding["related_issue"]
    issue_id = related["id"]
    add = change.startswith("add-")
    after = [edge for edge in before if edge["id"] != issue_id]
    if add:
        after.append(related)
    after.sort(key=identity_key)
    if change.endswith("child"):
        route = ("POST", endpoint + "/sub_issues", {"sub_issue_id": issue_id, "replace_parent": False}, 201)
        if not add:
            route = ("DELETE", endpoint + "/sub_issue", {"sub_issue_id": issue_id}, 200)
    else:
        route = ("POST", endpoint + "/dependencies/blocked_by", {"issue_id": issue_id}, 201)
        if not add:
            route = ("DELETE", f"{endpoint}/dependencies/blocked_by/{issue_id}", None, 200)
    return after, route


def issue_endpoint(binding):
    return f"/repos/{binding['repository']['full_name']}/issues/{binding['issue']['number']}"


def preview(root, projection, mapping, ticket, change, related, client):
    snapshot, binding, local = project_binding(root, projection, mapping, ticket, change, related)
    if change == "state":
        expected_state(local)
    endpoint, before = read_field(client, binding)
    after, route = desired_change(binding, local, endpoint, before)
    snapshot.verify_unchanged()
    method, target, body, code = route
    intent = {
        "schema_version": PREVIEW, **binding,
        "before": before, "after": after,
        "request": {"method": method, "endpoint": target, "body": body, "expected_http_status": code},
    }
    return {
        **intent, "operation_id": context.digest(context.canonical(intent)),
        "reads": client.reads, "provider_atomic_guard": False,
    }


def check_remote_value(change, value):
    if edge_change(change):
        context.require(isinstance(value, list)
                        and all(isinstance(row, dict)
                                and set(row) == {"repository", "number", "id"}
                                and github.repo_name(row["repository"])
                                and all(github.positive_int(row[key]) for key in ("number", "id"))
                                for row in value),
                        "invalid GitHub relation snapshot")
        context.require(len({row["id"] for row in value}) == len(value),
                        "ambiguous GitHub relation snapshot")
    elif change == "title":
        context.require(isinstance(value, dict) and set(value) == {"title_sha256"},
                        "invalid GitHub title snapshot")
        store.check_digest(value["title_sha256"], "title")
    else:
        context.require(value == {"state": "open"} or (
            isinstance(value, dict) and set(value) == {"state", "reason"}
            and value["state"] == "closed" and value["reason"] in
            (None, "completed", "not_planned", "duplicate")
        ), "invalid GitHub state snapshot")


def load_preview(root, name, sha):
    context.require(root.is_absolute() and root.is_dir() and root.resolve() == root,
                    "expected a canonical absolute project root")
    store.check_digest(sha, "preview")
    raw = context.bound_bytes(root, name)
    context.require(context.digest(raw) == sha, "approved preview bytes changed")
    obj = context.json_object(raw)
    expected = {
        "schema_version", "repository", "issue", "related_issue", "project_id", "native_revision",
        "projection", "mapping", "sources", "ticket_id", "related_ticket_id", "change", "checkout_sha256",
        "before", "after", "request", "operation_id", "reads", "provider_atomic_guard",
    }
    context.require(set(obj) == expected and obj["schema_version"] == PREVIEW
                    and obj["change"] in CHANGES and obj["provider_atomic_guard"] is False,
                    "invalid approved GitHub preview")
    identity = {k: v for k, v in obj.items() if k not in {"operation_id", "reads", "provider_atomic_guard"}}
    context.require(obj["operation_id"] == context.digest(context.canonical(identity)),
                    "preview operation identity changed")
    require_checkout(root, obj)
    repo = obj["repository"]
    context.require(isinstance(repo, dict) and set(repo) == {"full_name", "id"}
                    and github.repo_name(repo["full_name"]) and github.positive_int(repo["id"]),
                    "invalid preview repository")
    has_edge = edge_change(obj["change"])
    context.require(has_edge == (obj["related_issue"] is not None), "invalid preview relation")
    for issue in [obj["issue"]] + ([obj["related_issue"]] if has_edge else []):
        context.require(isinstance(issue, dict) and set(issue) == {"repository", "number", "id"}
                        and issue["repository"] == repo["full_name"].lower()
                        and all(github.positive_int(issue[key]) for key in ("number", "id")),
                        "invalid preview issue")
    context.require(not has_edge or obj["related_issue"] != obj["issue"], "self relation")
    for key in ("projection", "mapping"):
        github.trees.pins([obj[key]])
    for key in ("before", "after"):
        check_remote_value(obj["change"], obj[key])
    return obj


def ledger_path(root, obj):
    directory = context.local(root, ".atelier", existing=False)
    path = directory / f"github-issues-{obj['repository']['id']}-operations.json"
    context.require(not path.is_symlink(), "linked GitHub operation ledger")
    return path


def read_ledger(root, path, obj):
    base = {
        "schema_version": LEDGER, "project": obj["project_id"],
        "root": str(root), "repository_id": obj["repository"]["id"],
    }
    if not path.exists():
        return None, {**base, "operations": {}}
    info = path.lstat()
    context.require(stat.S_ISREG(info.st_mode) and info.st_nlink == 1, "invalid GitHub operation ledger")
    raw = context.bound_bytes(root, path.relative_to(root).as_posix())
    ledger = context.json_object(raw)
    context.require(set(ledger) == {*base, "operations"}
                    and all(ledger[key] == value for key, value in base.items())
                    and isinstance(ledger["operations"], dict), "GitHub operation ledger scope mismatch")
    for identifier, row in ledger["operations"].items():
        store.check_digest(identifier, "operation ID")
        context.require(isinstance(row, dict) and set(row) == {
                            "issues", "status", "response", "reads", "confirmed_at", "rejections",
                        }
                        and isinstance(row["issues"], list) and len(row["issues"]) in (1, 2)
                        and all(github.positive_int(val) for val in row["issues"])
                        and row["status"] in ("attempting", "observed", "rejected")
                        and isinstance(row["reads"], list) and isinstance(row["rejections"], list)
                        and (row["status"] != "rejected" or isinstance(row["response"], dict)),
                        "invalid GitHub operation row")
    return raw, ledger


def save_ledger(root, path, before, ledger, obj, recheck=None):
    data = store.projection_bytes(ledger)
    context.require(len(data) <= context.MAX_BOUND_SOURCE, "GitHub operation ledger is full")

    def precondition():
        if recheck is not None:
            recheck()
        current, _ = read_ledger(root, path, obj)
        context.require(current == before, "GitHub operation ledger changed")

    if before is not None:
        store.atomic_replace(path, data, precondition)
    else:
        path.parent.mkdir(mode=0o700, exist_ok=True)
        # Persist the journal directory itself before sending a provider request.
        fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
        try:
            os.fsync(fd)
        finally:
            os.close(fd)
        create_ledger(path, data, precondition)
    current, _ = read_ledger(root, path, obj)
    context.require(current == data, "GitHub operation ledger write is unverified")
    return current


def local_recheck(root, obj):
    snapshot, binding, local = project_binding(
        root, obj["projection"]["path"], obj["mapping"]["path"],
        obj["ticket_id"], obj["change"], obj["related_ticket_id"],
    )
    context.require(all(obj[key] == value for key, value in binding.items()),
                    "SOURCE_DRIFT: refresh and reapprove the GitHub preview")
    target = issue_endpoint(binding)
    after, (method, route, body, code) = desired_change(binding, local, target, obj["before"])
    context.require(obj["after"] == after and obj["request"] == {
        "method": method, "endpoint": route, "body": body, "expected_http_status": code,
    }, "approved change disagrees with local target and effect")
    return snapshot


def result(obj, client, status, **extra):
    return {
        "schema_version": RESULT, "status": status, "operation_id": obj["operation_id"],
        "repository": obj["repository"], "issue": obj["issue"], "change": obj["change"],
        "reads": client.reads, "writes": client.writes, **extra,
    }


def read_attempt(root, path, raw, ledger, obj, client, attempt):
    try:
        observed = read_field(client, obj)[1]
    except github.GitHubUnavailable as error:
        status = {"attempting": "pending", "rejected": "rejected", "observed": "unavailable"}[attempt["status"]]
        return result(obj, client, status, reason=error.code, prior_attempt=attempt)
    if attempt["status"] == "rejected":
        return result(obj, client, "rejected", observed=observed, prior_attempt=attempt)
    matched = observed == obj["after"]
    if attempt["status"] == "attempting" and matched:
        attempt.update(status="observed", reads=list(client.reads),
                       confirmed_at=datetime.now(timezone.utc).isoformat())
        save_ledger(root, path, raw, ledger, obj)
    status = "desired-state-observed" if matched else (
        "drift-after-readback" if attempt["status"] == "observed" else "pending"
    )
    return result(obj, client, status, observed=observed, prior_attempt=attempt)


def require_checkout(root, preview):
    context.require(preview.get("checkout_sha256") == context.digest(os.fsencode(root)),
                    "approved preview belongs to a different checkout")


def execute(root, obj, client, *, apply, retry_rejected=False):
    context.require(root.is_absolute() and root.is_dir() and root.resolve() == root,
                    "expected a canonical absolute project root")
    require_checkout(root, obj)
    # Hold the common root lock used by replan and dispatch. Read-back keeps
    # working even after the old projection file or its directory is removed.
    with store.coordinator_lock(root, root / store.LOCK_NAME):
        path = ledger_path(root, obj)
        raw, ledger = read_ledger(root, path, obj)
        operations = ledger["operations"]
        operation_id = obj["operation_id"]
        previous = operations.get(operation_id)
        if retry_rejected and (previous is None or previous["status"] != "rejected"):
            return result(obj, client, "conflict", reason="retry-requires-definite-rejection")
        if previous is not None and not retry_rejected:
            return read_attempt(root, path, raw, ledger, obj, client, previous)
        if not apply:
            observed = read_field(client, obj)[1]
            return result(obj, client, "unattempted", observed=observed)

        snapshot = local_recheck(root, obj)
        issue_ids = [obj["issue"]["id"]]
        if obj["related_issue"]:
            issue_ids.append(obj["related_issue"]["id"])
        for row in operations.values():
            if row["status"] == "attempting" and set(issue_ids).intersection(row["issues"]):
                return result(obj, client, "conflict", reason="unresolved-operation-on-mapped-issue")
        observed = read_field(client, obj)[1]
        snapshot.verify_unchanged()
        rejections = [*previous["rejections"], previous["response"]] if previous else []
        if observed == obj["after"]:
            operations[operation_id] = {
                "issues": issue_ids, "status": "observed", "response": None,
                "reads": list(client.reads), "confirmed_at": datetime.now(timezone.utc).isoformat(),
                "rejections": rejections,
            }
            save_ledger(root, path, raw, ledger, obj, snapshot.verify_unchanged)
            return result(obj, client, "already-current", observed=observed)
        if observed != obj["before"]:
            return result(obj, client, "conflict", reason="github-state-changed", observed=observed)

        context.require("Authorization" in client.headers, "a GitHub Issues write credential is required")
        attempt = {
            "issues": issue_ids, "status": "attempting", "response": None,
            "reads": [], "confirmed_at": None,
            "rejections": rejections,
        }
        operations[operation_id] = attempt
        raw = save_ledger(root, path, raw, ledger, obj, snapshot.verify_unchanged)
        receipt = client.mutate(obj["request"])
        if receipt["response"] == "rejected":
            attempt["status"] = "rejected"
        attempt["response"] = receipt
        raw = save_ledger(root, path, raw, ledger, obj)
        return read_attempt(root, path, raw, ledger, obj, client, attempt)


def main(argv=None, *, client=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="operation", required=True)
    review = commands.add_parser("preview", help="show one exact proposed change using GET requests")
    review.add_argument("--root", required=True, type=Path)
    review.add_argument("--projection", required=True)
    review.add_argument("--mapping", required=True)
    review.add_argument("--ticket", required=True)
    review.add_argument("--change", required=True, choices=CHANGES)
    review.add_argument("--related")
    for name in ("commit", "read-back"):
        command = commands.add_parser(name)
        command.add_argument("--root", required=True, type=Path)
        command.add_argument("--preview", required=True, help="path inside the project")
        command.add_argument("--sha256", required=True, help="SHA-256 of the approved preview file")
        if name == "commit":
            command.add_argument("--retry-rejected", action="store_true",
                                 help="retry an explicitly rejected request after rechecking the same preview")
    args = parser.parse_args(argv)
    try:
        client = client or WriteClient(os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN"))
        if args.operation == "preview":
            output = preview(args.root, args.projection, args.mapping, args.ticket,
                             args.change, args.related, client)
        else:
            obj = load_preview(args.root, args.preview, args.sha256)
            output = execute(args.root, obj, client, apply=args.operation == "commit",
                             retry_rejected=getattr(args, "retry_rejected", False))
    except github.GitHubUnavailable as error:
        print(json.dumps({"status": "unavailable", "reason": error.code, "reads": client.reads}))
        return 2
    except (context.ContextError, OSError, UnicodeError) as error:
        print(json.dumps({"status": "invalid-input", "error": str(error)}), file=sys.stderr)
        return 2
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if output.get("status") in (None, "already-current", "desired-state-observed") else 2


if __name__ == "__main__":
    sys.exit(main())
