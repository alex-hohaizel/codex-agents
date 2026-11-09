#!/usr/bin/env python3
"""Check a declared orchestration task; never classify intent, execute or grant authority.

Older task/1 projections remain readable as legacy_not_declared. --ready requires
current routing context. Receipts are structurally bound declarations, not proof
that a host, human or provider actually performed the reported operation.
"""
import argparse
import json
from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "atelier.orchestrator-task/1"
GROUPS = ("entry", "routing", "creation_scope", "execution_scope",
          "original_result_acceptance", "continuation", "maintenance", "execution")
STABLE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
SHA256 = re.compile(r"[a-f0-9]{64}\Z")


def strict_json_loads(raw):
    if len(raw) > 4 * 1024 * 1024:
        raise ValueError("task projection exceeds4MiB")

    def unique(pairs):
        value = {}
        for key, item in pairs:
            if key in value:
                raise ValueError("duplicate JSON key: " + key)
            value[key] = item
        return value

    def finite(value):
        raise ValueError("nonfinite JSON value: " + value)

    return json.loads(raw, object_pairs_hook=unique, parse_constant=finite)


def validate(data, ready=False):
    contract = strict_json_loads((ROOT / "assets/routing-contract.json").read_text(encoding="utf8"))
    errors = []

    def require(condition, message):
        if not condition:
            errors.append(message)

    def text(value):
        return isinstance(value, str) and bool(value.strip())

    def choice(value, values):
        return isinstance(value, str) and value in values

    def obj(value, label):
        if not isinstance(value, dict):
            errors.append(label + " must be an object")
            return {}
        return value

    def strings(value, label, nonempty=False):
        if not isinstance(value, list) or any(not text(v) for v in value):
            errors.append(label + " must be a string array")
            return []
        require(not nonempty or bool(value), label + " cannot be empty")
        return value

    def pin(value, label):
        value = obj(value, label)
        if value.get("selector") is not None:
            require(text(value["selector"]) and len(value["selector"]) <= 64
                    and bool(STABLE.fullmatch(value["selector"])), label + " requires a stable selector")
        if ready:
            require(text(value.get("source_ref") or value.get("path")), label + " requires actual source reference")
            require(isinstance(value.get("sha256"), str) and bool(SHA256.fullmatch(value["sha256"])),
                    label + " requires source SHA256")
        return value

    data = obj(data, "task")
    require(data.get("schema_version") == SCHEMA, "unsupported task schema")
    require(data.get("is_template") is False, "instantiate the task template before use")
    require(data.get("quality_certified", False) is False, "a task projection cannot certify quality")
    declared = any(key in data for key in GROUPS)
    if not declared:
        require(not ready, "legacy task has no declared route; prepare a current projection from actual sources")
        return result(errors, "legacy_not_declared")

    entry = obj(data.get("entry"), "entry")
    require(choice(entry.get("surface"), {"chat", "panel", "delegated"}), "invalid entry.surface")
    routing = obj(data.get("routing"), "routing")
    route = routing.get("route")
    require(choice(route, contract["routes"]), "invalid routing.route")
    require(text(routing.get("reason")), "routing.reason required")
    sources = routing.get("source_pins")
    require(isinstance(sources, list), "routing.source_pins must be an array")
    for index, source in enumerate(sources if isinstance(sources, list) else []):
        pin(source, "routing.source_pins[" + str(index) + "]")
    gaps = strings(routing.get("capability_gaps"), "routing.capability_gaps")
    if ready and route in contract["source_required_routes"]:
        require(bool(sources), "selected specialist route requires actual source pins")
    if route == "bridge":
        require(bool(gaps), "bridge requires a concrete missing capability")

    creation = obj(data.get("creation_scope"), "creation_scope")
    execution_scope = obj(data.get("execution_scope"), "execution_scope")
    for label, scope in (("creation_scope", creation), ("execution_scope", execution_scope)):
        require(isinstance(scope.get("requested"), bool), label + ".requested must be boolean")
        if scope.get("requested") is True and ready:
            require(text(scope.get("authority_ref")), label + ".authority_ref required")
            strings(scope.get("acceptance"), label + ".acceptance", True)
    if creation.get("requested") is True:
        require(choice(creation.get("stage"), {"planning", "construction", "installation", "verification"}),
                "creation_scope.stage required")
    if execution_scope.get("requested") is True:
        require(choice(execution_scope.get("activity"), {"planning", "task_execution", "product_execution"}),
                "execution_scope.activity required")
    if ready and route == "create_agent":
        require(creation.get("requested") is True, "create_agent route must name its planning/construction scope")

    continuation = obj(data.get("continuation"), "continuation")
    preferred = continuation.get("preferred_project_agent")
    if preferred is not None:
        require(text(preferred) and len(preferred) <= 64 and bool(STABLE.fullmatch(preferred)),
                "continuation requires a stable project-agent selector")
        require(choice(continuation.get("project_agent_status"), {"host_discovered", "executed"}),
                "an active preferred project agent requires actual host discovery")
        pin(continuation.get("project_agent_source_pin"), "continuation.project_agent_source_pin")
        require(text(continuation.get("recommendation")), "explain the recommended project-agent continuation")
    if route == "project_agent":
        require(preferred is not None, "project_agent route requires a verified continuation binding")

    maintenance = data.get("maintenance")
    if route == "maintain_system" or maintenance is not None:
        maintenance = obj(maintenance, "maintenance")
        require(choice(maintenance.get("target_kind"), contract["maintenance_targets"]), "invalid maintenance.target_kind")
        require(choice(maintenance.get("action"), {"recommend", "audit", "plan", "apply"}), "invalid maintenance.action")
        targets = maintenance.get("target_refs")
        require(isinstance(targets, list) and bool(targets), "maintenance needs actual target references")
        for index, target in enumerate(targets if isinstance(targets, list) else []):
            pin(target, "maintenance.target_refs[" + str(index) + "]")
        strings(maintenance.get("preservation"), "maintenance.preservation", True)
        conflicts = strings(maintenance.get("unresolved_conflicts"), "maintenance.unresolved_conflicts")
        if ready and maintenance.get("action") == "apply":
            require(text(maintenance.get("review_ref")), "maintenance apply requires reviewed diff/impact reference")
            require(text(maintenance.get("rollback_ref")), "maintenance apply requires an actual before-copy/rollback reference")
            require(not conflicts, "resolve current source/settings conflicts before maintenance apply")

    execution = obj(data.get("execution"), "execution")
    state = execution.get("state")
    require(choice(state, contract["execution_states"]), "invalid execution.state")
    receipts = execution.get("receipt_refs")
    require(isinstance(receipts, list), "execution.receipt_refs must be an array")
    kinds = set()
    actual_results = []
    for index, value in enumerate(receipts if isinstance(receipts, list) else []):
        receipt = obj(value, "execution.receipt_refs[" + str(index) + "]")
        kind = receipt.get("kind")
        require(choice(kind, contract["receipt_kinds"]), "invalid receipt kind")
        require(text(receipt.get("ref")) and text(receipt.get("actor")), "receipt requires source reference and actual actor")
        if choice(kind, contract["receipt_kinds"]):
            kinds.add(kind)
        if kind == "execution_result":
            actual_results.append(receipt)
        if kind == "review":
            require(isinstance(receipt.get("independent"), bool), "review must distinguish self-check and independence")
    for kind in contract["required_receipts_by_state"].get(state if isinstance(state, str) else "", []):
        require(kind in kinds, state + " requires " + kind + "; delivery is not execution")
    if choice(state, {"started", "result", "reviewed", "accepted"}):
        require(text(execution.get("executor_ref")), "execution state requires an actual executor reference")
    if choice(state, {"result", "reviewed", "accepted"}) and execution_scope.get("requested") is True:
        activity = execution_scope.get("activity")
        require(any(r.get("activity") == activity for r in actual_results),
                "agent-construction output does not close the requested task/product execution")
    if choice(state, {"blocked", "unknown"}):
        require(text(data.get("recovery")), "blocked/unknown state requires exact reconciliation or recovery")

    if ready:
        for key in ("task_id", "objective", "owner", "authority_ref", "consumer", "stop", "recovery"):
            require(text(data.get(key)), "missing " + key)
        require(text(entry.get("request_ref")) and text(entry.get("original_objective")),
                "entry must retain original request and objective")
        require(text(routing.get("execution_owner")), "routing.execution_owner required")
        strings(data.get("original_result_acceptance"), "original_result_acceptance", True)
        require(text(continuation.get("next_action")), "continuation.next_action required")
        if entry.get("surface") == "delegated":
            require(text(continuation.get("return_to")), "delegated task requires an exact upstream return")
    return result(errors, "declared", route, state)


def result(errors, status, route=None, state=None):
    return {"valid": not errors, "errors": errors, "routing_status": status,
            "route": route, "execution_state": state, "execution_performed": False,
            "grants_created": [], "semantic_fit_certified": False,
            "human_authority_authenticated": False, "quality_certified": False}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("task", type=Path)
    parser.add_argument("--ready", action="store_true", help="require a complete current task projection and source pins")
    args = parser.parse_args(argv)
    try:
        if args.task.is_symlink() or not args.task.is_file():
            raise ValueError("task must be an existing regular JSON file, not a symlink")
        output = validate(strict_json_loads(args.task.read_text(encoding="utf8")), args.ready)
    except (OSError, ValueError, TypeError, KeyError) as error:
        parser.error(str(error))
    print(json.dumps(output, ensure_ascii=False, indent=2))
    return 0 if output["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
