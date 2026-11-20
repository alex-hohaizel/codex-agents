"""Synthetic production decision fixtures. These records never claim live review."""

from datetime import timedelta
import hashlib
import json
from pathlib import Path
import sys


STANDARDS = Path(__file__).resolve().parents[2] / "standards"
if str(STANDARDS) not in sys.path:
    sys.path.insert(0, str(STANDARDS))
from production_choices import (  # noqa: E402
    APPROVAL_SCHEMA, FLOW_KINDS, MASTER_KINDS, SCHEMA,
    decision_subject, utc_today, verify_project,
)


def current_pin(root, relative):
    raw = (root / relative).read_bytes()
    return {"path": relative, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def put(root, relative, content):
    path = root / relative
    path.parent.mkdir(exist_ok=True, parents=True)
    if isinstance(content, str):
        path.write_text(content, encoding="utf-8")
    else:
        path.write_text(json.dumps(content, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return current_pin(root, relative)


def make_choice(root, *, target_kind="script", phase="implement",
                record="production-choices.json", accepted_artifacts=None):
    root = Path(root)
    base = "_choice-fixture"
    today = utc_today()
    deadline = (today + timedelta(days=31)).isoformat()
    source = put(root, f"{base}/requirement.md", "Read the fixture without network access.\n")
    approved_scope = put(root, f"{base}/authority.txt",
                         "Synthetic approval scope, valid only for this test.\n")
    raw_probe = put(root, f"{base}/probe.txt", "Synthetic record of the controlled probe.\n")
    master = [put(root, f"{base}/master.html", "<main>Evidence and decision</main>\n")]
    flow = [put(root, f"{base}/flow.md", "Open evidence; review; confirm or refuse.\n")]
    configuration = put(root, f"{base}/configuration.md",
                        "Keep the workflow local and avoid an additional server.\n")
    selected = {
        "id": "native-files",
        "description": "Local consumer with the current file format",
        "reason": "Isolated and directly inspectable on the target",
        "mode": "feasible",
        "components": [{"role": "format", "name": "JSON", "version": "RFC 8259"}],
        "checks": {"R1": "pass"},
        "sources": [{
            "url": "https://www.rfc-editor.org/rfc/rfc8259",
            "checked_on": today.isoformat(), "review_by": deadline,
            "claim": "JSON grammar for the local fixture format",
        }],
        "probe": raw_probe,
    }
    value = {
        "schema": SCHEMA,
        "id": "synthetic-production-choices",
        "revision": 1,
        "author": "fixture-author",
        "objective": "Consume a controlled evidence sample",
        "target": "Synthetic test consumer",
        "target_kind": target_kind,
        "experiment": {
            "candidate_id": "native-files", "purpose": "Compare the exact source read in the local consumer",
            "inputs": [source], "procedure": configuration,
            "success_criteria": ["The input is read and no network request is made"],
            "temporary_boundary": "Disposable path and local fixture; no deployment or product writes",
        },
        "requirements": [{
            "id": "R1", "description": "Keep evidence local", "source": source, "hard": True,
        }],
        "candidates": [
            selected,
            {
                "id": "hosted", "description": "Hosted consumer",
                "reason": "A provider conflicts with local-only evidence handling",
                "mode": "excluded",
                "components": [{"role": "service", "name": "Hosted alternative", "version": "tbd"}],
                "checks": {"R1": "fail"},
                "sources": [],
            },
        ],
    }
    if phase == "explore":
        put(root, record, value)
        return verify_project(root, phase, record=record)
    value["decision"] = {
        "selected": "native-files",
        "reason": "The local alternative passes the hard requirement and preserves the format",
        "review_by": deadline,
        "configuration": [configuration],
        "masters": master if target_kind in MASTER_KINDS else [],
        "flows": flow if target_kind in FLOW_KINDS else [],
        "adaptations": "Only the final display width may change.",
    }
    put(root, record, value)
    subject = decision_subject(root, record=record)
    value["decision"]["approval"] = put(root, f"{base}/approval.json", {
        "schema": APPROVAL_SCHEMA, "subject_sha256": subject,
        "actor": "fixture-owner", "scope": "Synthetic test only", "source": approved_scope,
    })
    positive = put(root, f"{base}/allow.txt", "Controlled valid fixture passed.\n")
    negative = put(root, f"{base}/deny.txt", "Controlled invalid fixture was refused.\n")
    method = {
        "web": "browser", "app": "device", "game": "runtime", "visual": "render",
        "audio": "playback", "video": "playback", "document": "render",
    }.get(target_kind, "cli")
    value["evidence"] = []
    for stage in ("scale", "accept"):
        if phase not in (stage, "accept"):
            continue
        value["evidence"].append({
            "id": stage + "-review",
            "phase": stage,
            "decision_sha256": subject,
            "author": "fixture-implementer",
            "reviewer": "fixture-reviewer",
            "method": method,
            "environment": "Synthetic fixture, not execution evidence",
            "outcome": "pass",
            "artifacts": ([current_pin(root, path) for path in accepted_artifacts]
                          if stage == "accept" and accepted_artifacts is not None else
                          [put(root, f"{base}/{stage}-artifact.txt", "Synthetic artifact.\n")]),
            "receipt": put(root, f"{base}/{stage}-receipt.txt", "Synthetic review receipt.\n"),
            "controls": [
                {"id": "allow", "expect": "positive", "outcome": "pass", "observation": positive},
                {"id": "deny", "expect": "negative", "outcome": "pass", "observation": negative},
            ],
        })
    put(root, record, value)
    return verify_project(root, phase, record=record)
