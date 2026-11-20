#!/usr/bin/env python3
"""Replay the exact Lower Fen visual fixture through the managed production lifecycle."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
STANDARDS = REPO / "standards"
UX = REPO / "kit/skills/app-atelier-experience/scripts/ux_prototype.py"
sys.path.insert(0, str(STANDARDS))

from production_choices import APPROVAL_SCHEMA, DEFAULT_RECORD, SCHEMA, decision_subject, verify_project  # noqa: E402


MASTERS = ("riverdesk.html", "riverlines.html")
DEPENDENCIES = ("riverdesk.css", "riverlines.css", "riverdesk.js", "riverlines.js", "reports.js")
SOURCE_FILES = (*MASTERS, *DEPENDENCIES, "requirements.md", "interaction.md", "check-browser.mjs")
SCREENSHOTS = tuple(f"{site}-{viewport}.png" for site in ("riverdesk", "riverlines")
                    for viewport in ("desktop", "phone"))
RECEIPT = "browser-receipt.json"
REVIEW = "independent-review.md"
KEYBOARD = "keyboard-review-receipt.json"
EXPECTED_REVIEW = {
    RECEIPT: "6c2e0fd614906037146dc160b40cae903d5b1326e93c9ef0f3b1f4e876ff43a7",
    REVIEW: "bb3c3425bca3a8ac564a78485c6f0e654a40fb05ac77e4d153fba27e0f94714a",
    KEYBOARD: "81153878d9ae05ba64a81f282ed96d1d4595b4dbfb64c63319119131ad2aaa00",
    "check-keyboard.mjs": "c17797dd43ae2f646c56f2208ba7992c41ef30bdc59a536fb1519be9eaf0c11d",
}
AUTHOR = "Codex /root/domain_routes"
REVIEWER = "Codex /root/choice_contract"
SCOPE = "Exact local Lower Fen synthetic evaluation and repeat. No external publication, product-owner acceptance, or production permission."
CHECKED_ON = "2026-11-20"
REVIEW_BY = "2026-12-20"


def require(condition, message):
    if not condition:
        raise ValueError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def pin(root, name):
    data = (root / name).read_bytes()
    return {"path": name, "sha256": digest(data), "bytes": len(data)}


def write_json(root, name, data):
    (root / name).write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return pin(root, name)


def copy_pinned(source, output, files):
    output.mkdir(parents=True, exist_ok=False)
    for name in files:
        file = source / name
        require(file.is_file() and not file.is_symlink(), f"Expected an ordinary exact input file: {file}")
        shutil.copyfile(file, output / name)


def inventory(rows, expected, field):
    result = {item["path"]: item["sha256"] for item in rows}
    require(len(result) == len(rows) and set(result) == set(expected), f"Unexpected {field} inventory")
    return result


def browser_observation(root, evidence):
    receipt = json.loads((evidence / RECEIPT).read_text(encoding="utf-8"))
    require(receipt["method"] == "browser" and receipt["product"] == "HeadlessChrome/156.0.8078.4",
            "Expected the independently reviewed Chromium version")
    require(len(receipt["checks"]) == len(set(receipt["checks"])) == 32,
            "The evidence must include all 32 executed browser assertions")
    for label in ("desktop", "phone"):
        for case in ("actual browser receipt targets exact report and revision", "conflict keeps selected report",
                     "viewer reads evidence and cannot hand off", "chronology changes article and focus"):
            require(f"{label} {case}" in receipt["checks"], f"Missing browser observation: {label} {case}")
    sources = inventory(receipt["sources"], SOURCE_FILES, "browser source")
    for name, expected in sources.items():
        require(pin(root, "site/" + name)["sha256"] == expected, f"Run used different source bytes: {name}")
    screenshots = inventory(receipt["screenshots"], SCREENSHOTS, "browser screenshot")
    for name, expected in screenshots.items():
        require(pin(evidence, name)["sha256"] == expected, f"Screenshot differs from captured bytes: {name}")
    return receipt


def source_snapshot():
    paths = [HERE / name for name in SOURCE_FILES]
    paths.extend((Path(__file__).resolve(), STANDARDS / "production_choices.py", UX,
                  UX.with_name("production_choices.py")))
    files = [pin(REPO, path.relative_to(REPO).as_posix()) for path in paths]
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    matching = []
    for item in files:
        blob = subprocess.run(["git", "show", f"{head}:{item['path']}"], cwd=REPO,
                              capture_output=True, check=False)
        matching.append(blob.returncode == 0 and digest(blob.stdout) == item["sha256"])
    return {"checkout_head": head, "verified_source_commit": head if all(matching) else None,
            "source_files": files}


def choice_record(root, evidence):
    brief = pin(root, "site/requirements.md")
    criteria = pin(root, "site/interaction.md")
    browser_sources = [
        {"url": "https://html.spec.whatwg.org/multipage/interactive-elements.html#the-details-element",
         "checked_on": CHECKED_ON, "claim": "Native summary and details provide disclosure without a component dependency."},
        {"url": "https://www.w3.org/TR/css-grid-2/", "checked_on": CHECKED_ON,
         "claim": "Grid describes the two desktop panes and keeps its responsive layout in CSS."},
        {"url": "https://chromedevtools.github.io/devtools-protocol/tot/Input/", "checked_on": CHECKED_ON,
         "claim": "The recorded browser harness can dispatch keyboard, mouse, and touch input."},
    ]
    return {
        "schema": SCHEMA, "id": "lower-fen-visual-lifecycle", "revision": 1, "author": AUTHOR,
        "objective": "Preserve separate operational and editorial mechanics on the same synthetic reports.",
        "target": evidence["product"] + " local desktop and emulated touch layouts", "target_kind": "web",
        "requirements": [
            {"id": key, "description": label, "source": brief, "hard": True} for key, label in (
                ("E01", "Bind evidence and handoff to LF-042, refuse an unprivileged or stale transfer, recover the same report."),
                ("E02", "Read the chronology and its article-specific source without operations controls."),
                ("E03", "Keep actions, focus and reading order usable at the two measured viewports."),
            )
        ],
        "references": [{"role": "constraint", "source": criteria,
                        "reason": "Stable layout and interaction requirements for both surfaces."}],
        "candidates": [{
            "id": "authored-local", "description": "Separate authored HTML/CSS/JS masters on shared local data.",
            "reason": "Keep the exact application and editorial behavior with minimal runtime dependencies.",
            "mode": "feasible", "components": [{"role": "browser", "name": "Chromium", "version": evidence["product"]}],
            "checks": {"E01": "pass", "E02": "pass", "E03": "pass"},
            "sources": browser_sources, "probe": pin(root, f"proof/first/{RECEIPT}"),
        }, {
            "id": "common-walkthrough", "description": "Use the existing offline walkthrough with the same subject matter.",
            "reason": "It is suitable for exploring navigation. It cannot carry both exact brand compositions and local stateful receipt behavior unchanged.",
            "mode": "excluded", "components": [{"role": "prototype", "name": "UX walkthrough", "version": "codex-agents.ux-prototype/1"}],
            "checks": {"E01": "fail", "E02": "fail", "E03": "unknown"}, "sources": [],
        }],
        "experiment": {"candidate_id": "authored-local", "purpose": "Run the same report through two different working experiences.",
                       "inputs": [brief, criteria, pin(root, "site/reports.js")],
                       "procedure": pin(root, "site/check-browser.mjs"),
                       "success_criteria": ["Transfer only reviewed LF-042 after recovery from a conflict.",
                                            "Open and return from the same report's public source notes without a transfer action.",
                                            "Exercise desktop keyboard and narrow touch without viewport overflow."],
                       "temporary_boundary": "Synthetic local content and user-role simulation. Preserve the original media and reviewer evidence; re-review any material replacement."},
    }


def native_master(root, artifact, allow):
    result = subprocess.run([sys.executable, "-B", str(UX), "verify-master", "--root", str(root),
                             "--artifact", str(root / artifact)], capture_output=True, text=True, check=False)
    require(result.returncode == (0 if allow else 2), f"Unexpected master's exit for {artifact}: {result.stdout or result.stderr}")
    return {"artifact": artifact, "exit_code": result.returncode, "receipt": json.loads(result.stdout or result.stderr)}


def negative_controls(root):
    outcomes = []
    for path in ("site/riverdesk.css", "site/interaction.md"):
        source = root / path
        original = source.read_bytes()
        try:
            source.write_bytes(original + b"\n/* unapproved replacement */\n")
            result = native_master(root, "site/riverdesk.html", allow=False)
            require(path in result["receipt"]["reason"], f"Negative did not detect the tested drift: {path}")
            outcomes.append({"changed_source": path, **result})
        finally:
            source.write_bytes(original)
    photo = native_master(root, "proof/independent/riverdesk-desktop.png", allow=False)
    require("exact approved master" in photo["receipt"]["reason"], "Screenshot did not fail the master identity check")
    return write_json(root, "proof/negative-controls.json", outcomes + [photo])


def lifecycle(output, authored, independent, chromium):
    output.mkdir(parents=True, exist_ok=False)
    copy_pinned(HERE, output / "site", SOURCE_FILES)
    copy_pinned(authored, output / "proof/first", (RECEIPT, *SCREENSHOTS))
    copy_pinned(independent, output / "proof/independent", (*EXPECTED_REVIEW, *SCREENSHOTS))
    for name, expected in EXPECTED_REVIEW.items():
        require(pin(output, "proof/independent/" + name)["sha256"] == expected,
                f"Independent review does not match the supplied exact bytes: {name}")
    first = browser_observation(output, output / "proof/first")
    review = browser_observation(output, output / "proof/independent")
    require(first == review, "First and independent browser observations disagree")
    record = choice_record(output, first)
    write_json(output, DEFAULT_RECORD, record)
    explore = verify_project(output, "explore", required_kind="web")

    configuration = [pin(output, "site/" + name) for name in DEPENDENCIES]
    original_masters = [pin(output, "site/" + name) for name in MASTERS]
    record["decision"] = {
        "selected": "authored-local", "reason": "The first controlled runtime and independent comparison support separate operational and editorial surfaces. Keep their defining artifacts.",
        "review_by": REVIEW_BY, "configuration": configuration, "masters": original_masters,
        "flows": [pin(output, "site/interaction.md")],
        "adaptations": "Keep these exact HTML, scripts, styles, and workflow. Use the existing responsive rules. Independently review later material adaptations.",
    }
    write_json(output, DEFAULT_RECORD, record)
    subject = decision_subject(output)
    authority = write_json(output, "proof/fixture-authority.json", {
        "actor": "Codex /root", "record": "Parent's direct delegation to /root/domain_routes",
        "instruction_excerpt": "Bind HTML/CSS/JS and interaction flow exact to actual local delegated fixture authority then native `ux_prototype.py verify-master` for both.",
        "scope": SCOPE, "subject_sha256": subject,
        "limitation": "Delegated authority covers the exact synthetic re-verification. This record does not attest a prior real product design approval.",
    })
    record["decision"]["approval"] = write_json(output, "proof/fixture-approval.json", {
        "schema": APPROVAL_SCHEMA, "actor": "Codex /root", "scope": SCOPE,
        "source": authority, "subject_sha256": subject,
    })
    write_json(output, DEFAULT_RECORD, record)
    implementation = verify_project(output, "implement", required_kind="web")
    masters = [native_master(output, "site/" + name, allow=True) for name in MASTERS]
    negative = negative_controls(output)
    for name in MASTERS:
        native_master(output, "site/" + name, allow=True)

    subprocess.run([os.environ.get("AGENT_SYSTEM_NODE", "node"), str(output / "site/check-browser.mjs"),
                    str(chromium), str(output / "proof/replay")], check=True, timeout=90)
    replay = browser_observation(output, output / "proof/replay")
    require(replay == review, "Run after master verification differs from the independent receipt; review it anew")
    outputs = [pin(output, "proof/replay/" + name) for name in SCREENSHOTS]
    positive = pin(output, f"proof/replay/{RECEIPT}")
    independent_review = pin(output, f"proof/independent/{REVIEW}")
    record["evidence"] = []
    for phase in ("scale", "accept"):
        record["evidence"].append({
            "id": phase + "-lower-fen", "phase": phase, "decision_sha256": subject,
            "author": AUTHOR, "reviewer": REVIEWER, "method": "browser", "outcome": "pass",
            "environment": replay["product"] + " desktop and touch emulation; local synthetic permission, conflict and recovery",
            "artifacts": original_masters + configuration + outputs + [pin(output, f"proof/independent/{KEYBOARD}")],
            "receipt": independent_review,
            "controls": [{"id": "actual-play-through", "expect": "positive", "outcome": "pass", "observation": positive},
                         {"id": "deny-replacement", "expect": "negative", "outcome": "pass", "observation": negative}],
        })
    write_json(output, DEFAULT_RECORD, record)
    return write_json(output, "lifecycle-receipt.json", {
        **source_snapshot(), "scope": SCOPE, "decision_sha256": subject, "explore": explore,
        "implement": implementation, "native_masters": masters, "negative_controls": negative,
        "independent_review": independent_review, "replay": positive,
        "scale": verify_project(output, "scale", required_kind="web"),
        "accept": verify_project(output, "accept", required_kind="web"),
    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--authored", type=Path, required=True, help="First browser receipt and four captured PNGs")
    parser.add_argument("--independent", type=Path, required=True, help="Exact independent browser and keyboard evidence")
    parser.add_argument("--chromium", type=Path, required=True, help="Local executable for the reviewed Chromium version")
    parser.add_argument("output", type=Path, help="A new output directory")
    args = parser.parse_args()
    print(json.dumps(lifecycle(args.output.resolve(), args.authored, args.independent, args.chromium), indent=2))
