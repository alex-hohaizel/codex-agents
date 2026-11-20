#!/usr/bin/env python3
"""Check a current, source-bound production decision before a managed stage.

This dependency-free reader checks local bytes and declared observations. It
does not execute a probe, authenticate people or authority, or judge craft.
"""

from __future__ import annotations

import argparse
from datetime import date, datetime, timezone
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
from urllib.parse import urlsplit


SCHEMA = "atelier.production-choices/1"
APPROVAL_SCHEMA = "atelier.production-choice-approval/1"
DEFAULT_RECORD = "production-choices.json"
PHASES = ("explore", "implement", "scale", "accept")
KINDS = (
    "web", "app", "game", "chatbot", "visual", "audio", "video", "document",
    "cli", "script", "backend", "data", "integration", "model", "operations",
    "agent", "physical", "other",
)
MASTER_KINDS = {"web", "app", "game", "visual", "audio", "video", "document"}
FLOW_KINDS = {"web", "app", "game", "chatbot", "cli", "backend", "integration"}
ACTUAL_METHODS = {
    "browser", "device", "playback", "runtime", "cli", "render", "import",
    "native", "integration",
}
METHODS_BY_KIND = {
    "web": {"browser", "device"},
    "app": {"browser", "device", "native"},
    "game": {"device", "runtime", "native"},
    "visual": {"render", "browser", "device", "import", "native"},
    "audio": {"playback", "device", "native"},
    "video": {"playback", "device", "native"},
    "document": {"render", "browser", "native", "import"},
}
OUTCOMES = {"pass", "fail", "unknown"}
MAX_JSON = 2 * 1024 * 1024
MAX_FILE = 2 * 1024 * 1024 * 1024
MAX_TOTAL = 4 * 1024 * 1024 * 1024
MAX_PINS = 2048
BLOCK = 1024 * 1024
HASH = re.compile(r"[0-9a-f]{64}\Z")
IDENTIFIER = re.compile(r"[a-zA-Z0-9][a-zA-Z0-9_.:-]{0,127}\Z")
WINDOWS_DEVICE = re.compile(
    r"^(?:CON|PRN|AUX|NUL|CONIN\$|CONOUT\$|COM[1-9¹²³]|LPT[1-9¹²³])(?:\.|$)", re.I,
)
PRIVATE_NAME = re.compile(
    r"^(?:\.env(?:\..*)?|credentials(?:\..*)?|owner-credentials\.json|"
    r"id_(?:rsa|ed25519)|.*\.(?:pem|key|p12|pfx)|auth\.json)$", re.I,
)
PRIVATE_PARTS = {".git", ".aws", ".ssh", ".config", "node_modules"}


class ChoiceError(ValueError):
    """The requested stage lacks a current structural prerequisite."""


def require(condition, message):
    if not condition:
        raise ChoiceError(message)


def fields(value, name, required, optional=()):
    require(isinstance(value, dict), f"{name} must be an object")
    missing = set(required) - value.keys()
    extra = value.keys() - set(required) - set(optional)
    require(not missing, f"{name} is missing: {', '.join(sorted(missing))}")
    require(not extra, f"{name} has unsupported fields: {', '.join(sorted(extra)[:12])}")


def text(value, name, limit=8000):
    require(isinstance(value, str) and value.strip() and len(value) <= limit,
            f"{name} must contain bounded nonempty text")
    try:
        value.encode("utf-8")
    except UnicodeError as error:
        raise ChoiceError(f"{name} must be valid Unicode text") from error
    return value


def eq_choice(value, choices, name):
    require(isinstance(value, str) and value in choices, f"{name} is unsupported")
    return value


def integer(value, name, minimum=0):
    require(type(value) is int and minimum <= value <= 2**53 - 1,
            f"{name} must be an integer >= {minimum}")
    return value


def digest_value(value, name):
    require(isinstance(value, str) and HASH.fullmatch(value),
            f"{name} must be a lowercase SHA-256")
    return value


def rows(value, name, minimum=0, maximum=256):
    require(isinstance(value, list) and minimum <= len(value) <= maximum,
            f"{name} must have {minimum} to {maximum} entries")
    return value


def ident(value, name):
    require(isinstance(value, str) and IDENTIFIER.fullmatch(value),
            f"{name} must be a stable identifier")
    return value


def add_unique(items, key, value, name):
    require(key not in items, f"duplicate {name}: {key}")
    items[key] = value


def utc_today():
    return datetime.now(timezone.utc).date()


def iso_date(value, name):
    require(isinstance(value, str) and re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value),
            f"{name} must be YYYY-MM-DD")
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ChoiceError(f"{name} is not a calendar date") from error


def pairs(values):
    result = {}
    for key, value in values:
        require(key not in result, "duplicate JSON object key")
        result[key] = value
    return result


def unsupported_number(value):
    raise ChoiceError("only bounded integers are supported in decision records")


def json_object(data):
    try:
        value = json.loads(
            data.decode("utf-8"), object_pairs_hook=pairs,
            parse_float=unsupported_number, parse_constant=unsupported_number,
        )
    except ChoiceError:
        raise
    except (ValueError, UnicodeError, RecursionError) as error:
        raise ChoiceError("invalid or deeply nested UTF-8 JSON") from error
    require(isinstance(value, dict), "JSON record must be an object")
    return value


def linked(info):
    return stat.S_ISLNK(info.st_mode) or bool(getattr(info, "st_file_attributes", 0) & 0x400)


def stable(info):
    return (info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns)


class LocalReads:
    """Read bounded regular files below an existing, resolved project root."""

    def __init__(self, root):
        try:
            self.root = Path(root).resolve(strict=True)
        except (OSError, RuntimeError, ValueError) as error:
            raise ChoiceError("project root is unavailable") from error
        require(self.root.is_dir(), "project root must be an existing directory")
        self.pins = {}
        self.total = 0

    def path(self, value):
        value = text(value, "relative path", 512)
        pure = PurePosixPath(value)
        require(
            pure.parts and not pure.is_absolute() and pure.as_posix() == value
            and all(
                part not in (".", "..") and part.casefold() not in PRIVATE_PARTS
                and not part.endswith((" ", ".")) and not WINDOWS_DEVICE.match(part)
                and not PRIVATE_NAME.match(part)
                and not any(char in '\\:<>"|?*' or ord(char) < 32 for char in part)
                for part in pure.parts
            ),
            "unsafe or protected project-relative path",
        )
        return self.root.joinpath(*pure.parts)

    def read(self, value, *, json_input=False):
        path = self.path(value)
        for parent in path.parents:
            if parent == self.root:
                break
            try:
                info = parent.lstat()
            except OSError as error:
                raise ChoiceError(f"missing parent of {value}") from error
            require(not linked(info) and stat.S_ISDIR(info.st_mode),
                    f"linked or invalid parent of {value}")
        try:
            before = path.lstat()
            require(not linked(before) and stat.S_ISREG(before.st_mode)
                    and path.resolve(strict=True) == path, f"linked or nonregular file: {value}")
            limit = MAX_JSON if json_input else MAX_FILE
            require(0 <= before.st_size <= limit, f"file exceeds size bound: {value}")
            cached = self.pins.get(value)
            if cached is not None:
                identity, digest, data = cached
                require(identity == stable(before), f"file changed during validation: {value}")
                if not json_input or data is not None:
                    return digest, before.st_size, data
            else:
                require(len(self.pins) < MAX_PINS and self.total + before.st_size <= MAX_TOTAL,
                        "project evidence exceeds read budget")
            flags = (os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
                     | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_BINARY", 0))
            with os.fdopen(os.open(path, flags), "rb") as handle:
                opened = os.fstat(handle.fileno())
                require(stat.S_ISREG(opened.st_mode) and stable(before) == stable(opened),
                        f"file changed before reading: {value}")
                hasher = hashlib.sha256()
                size = 0
                content = bytearray() if json_input else None
                while True:
                    chunk = handle.read(BLOCK)
                    if not chunk:
                        break
                    size += len(chunk)
                    require(size <= before.st_size, f"file grew during validation: {value}")
                    hasher.update(chunk)
                    if content is not None:
                        content.extend(chunk)
                require(stable(before) == stable(os.fstat(handle.fileno())) == stable(path.lstat())
                        and path.resolve(strict=True) == path and size == before.st_size,
                        f"file changed during validation: {value}")
        except (OSError, RuntimeError) as error:
            raise ChoiceError(f"could not read project file: {value}") from error
        digest = hasher.hexdigest()
        data = bytes(content) if content is not None else None
        if cached is None:
            self.total += size
        else:
            require(cached[1] == digest, f"file changed during validation: {value}")
        self.pins[value] = (stable(before), digest, data)
        return digest, size, data

    def pin(self, pin, name, *, json_input=False):
        fields(pin, name, ("path", "sha256"), ("bytes",))
        expected = digest_value(pin["sha256"], name + ".sha256")
        digest, size, data = self.read(pin["path"], json_input=json_input)
        require(digest == expected, f"stale {name}: {pin['path']}")
        if "bytes" in pin:
            require(integer(pin["bytes"], name + ".bytes") == size, f"wrong size: {pin['path']}")
        return data

    def pin_list(self, value, name, minimum=0):
        unique = {}
        for pin in rows(value, name, minimum):
            self.pin(pin, name)
            add_unique(unique, pin["path"], pin, name + " path")
        return unique

    def finish(self):
        for relative, (identity, _, _) in self.pins.items():
            path = self.path(relative)
            try:
                info = path.lstat()
                require(not linked(info) and stable(info) == identity
                        and path.resolve(strict=True) == path,
                        f"file changed during validation: {relative}")
            except (OSError, RuntimeError) as error:
                raise ChoiceError(f"file changed during validation: {relative}") from error


def sources(value, today):
    deadlines = []
    for source in rows(value, "candidate sources", maximum=64):
        fields(source, "candidate source", ("url", "checked_on", "claim"), ("review_by",))
        url = text(source["url"], "candidate source URL", 2048)
        try:
            parsed = urlsplit(url)
            require(parsed.scheme == "https" and parsed.hostname
                    and parsed.username is None and parsed.password is None
                    and not any(char.isspace() or ord(char) < 32 for char in url),
                    "candidate source must be an HTTPS URL without credentials")
        except ValueError as error:
            if isinstance(error, ChoiceError):
                raise
            raise ChoiceError("invalid candidate source URL") from error
        checked = iso_date(source["checked_on"], "source checked_on")
        require(checked <= today, "source cannot be checked in the future")
        if "review_by" in source:
            deadline = iso_date(source["review_by"], "source review_by")
            require(checked <= deadline, "source review deadline predates its check")
            deadlines.append(deadline)
        text(source["claim"], "candidate source claim")
    return deadlines


def initial(reader, value, today):
    fields(
        value, "decision record",
        ("schema", "id", "revision", "author", "objective", "target", "target_kind",
         "requirements", "candidates", "experiment"),
        ("references", "decision", "evidence"),
    )
    require(value["schema"] == SCHEMA, "unsupported production choice schema")
    ident(value["id"], "decision record ID")
    integer(value["revision"], "decision revision", 1)
    text(value["author"], "author", 240)
    text(value["objective"], "objective")
    text(value["target"], "target")
    eq_choice(value["target_kind"], KINDS, "target kind")
    requirements = {}
    for requirement in rows(value["requirements"], "requirements", 1):
        fields(requirement, "requirement", ("id", "description", "source", "hard"))
        key = ident(requirement["id"], "requirement ID")
        text(requirement["description"], "requirement description")
        require(type(requirement["hard"]) is bool, "requirement hard flag must be boolean")
        reader.pin(requirement["source"], "requirement source")
        add_unique(requirements, key, requirement, "requirement ID")
    require(any(row["hard"] for row in requirements.values()),
            "at least one explicit hard requirement is needed")

    references = {}
    for reference in rows(value.get("references", []), "references"):
        fields(reference, "reference", ("role", "source", "reason"))
        eq_choice(reference["role"], ("inspiration", "constraint", "master", "rejected"),
                  "reference role")
        text(reference["reason"], "reference role reason")
        reader.pin(reference["source"], "reference source")
        add_unique(references, reference["source"]["path"], reference, "reference path")

    candidates = {}
    for candidate in rows(value["candidates"], "candidates", 1, 64):
        fields(candidate, "candidate", ("id", "description", "reason", "mode",
                                       "components", "checks", "sources"), ("probe",))
        key = ident(candidate["id"], "candidate ID")
        text(candidate["description"], "candidate description")
        text(candidate["reason"], "candidate reason")
        eq_choice(candidate["mode"], {"feasible", "excluded"}, "candidate mode")
        components = {}
        for component in rows(candidate["components"], "candidate components", 1, 64):
            fields(component, "component", ("role", "name", "version"))
            role = ident(component["role"], "component role")
            text(component["name"], "component name", 240)
            text(component["version"], "component version", 240)
            add_unique(components, role, component, "component role")
        fields(candidate["checks"], "candidate requirement checks", requirements)
        for outcome in candidate["checks"].values():
            eq_choice(outcome, OUTCOMES, "candidate check outcome")
        sources(candidate["sources"], today)
        if "probe" in candidate:
            reader.pin(candidate["probe"], "candidate probe")
        add_unique(candidates, key, candidate, "candidate ID")
    experiment = value["experiment"]
    fields(experiment, "exploration plan", ("candidate_id", "purpose", "inputs", "procedure",
                                              "success_criteria", "temporary_boundary"))
    route = ident(experiment["candidate_id"], "experiment candidate ID")
    require(route in candidates and candidates[route]["mode"] == "feasible",
            "exploration plan requires a declared feasible candidate")
    text(experiment["purpose"], "experiment purpose")
    reader.pin_list(experiment["inputs"], "comparable experiment inputs", 1)
    reader.pin(experiment["procedure"], "exploration procedure")
    for criterion in rows(experiment["success_criteria"], "experiment criteria", 1, 64):
        text(criterion, "experiment criterion")
    text(experiment["temporary_boundary"], "experiment temporary boundary")
    return requirements, references, candidates


def decided(reader, value, requirements, references, candidates, today):
    decision = value.get("decision")
    fields(decision, "production decision",
           ("selected", "reason", "review_by", "configuration", "masters", "flows", "adaptations"),
           ("approval",))
    selected_id = ident(decision["selected"], "selected candidate ID")
    selected = candidates.get(selected_id)
    require(selected is not None and selected["mode"] == "feasible", "select a feasible candidate")
    text(decision["reason"], "decision reason")
    text(decision["adaptations"], "allowed adaptations")
    review_by = iso_date(decision["review_by"], "decision review_by")
    require(today <= review_by, "production decision review is overdue")
    hard = {key for key, row in requirements.items() if row["hard"]}
    require(all(selected["checks"][key] == "pass" for key in hard),
            "selected candidate has failed or unknown hard requirements")
    feasible = [candidate for candidate in candidates.values() if candidate["mode"] == "feasible"]
    for candidate in feasible:
        require(not any(candidate["checks"][key] == "fail" for key in hard),
                f"feasible candidate fails a hard requirement: {candidate['id']}")
        require(candidate["sources"] and "probe" in candidate,
                f"feasible candidate needs dated sources and a pinned probe: {candidate['id']}")
        require(all(today <= deadline for deadline in sources(candidate["sources"], today)),
                f"candidate source review is overdue: {candidate['id']}")
    exact_components = [
        component for candidate in feasible for component in candidate["components"]
    ]
    require(all(component["version"].strip().casefold() not in {
        "latest", "stable", "current", "unknown", "tbd", "pending", "default", "*",
    } for component in exact_components), "freeze concrete versions for feasible components")
    configuration = reader.pin_list(decision["configuration"], "implementation configuration", 1)
    masters = reader.pin_list(decision["masters"], "approved master",
                              int(value["target_kind"] in MASTER_KINDS))
    flows = reader.pin_list(decision["flows"], "approved flow",
                            int(value["target_kind"] in FLOW_KINDS))
    for path, reference in references.items():
        if reference["role"] == "master":
            require(path in masters, f"approved reference master omitted from decision: {path}")
        elif reference["role"] == "rejected":
            require(path not in masters and path not in flows,
                    f"rejected reference cannot define the accepted work: {path}")
    # The subject stays stable as its approval and later observations are added.
    subject = {key: data for key, data in value.items() if key != "evidence"}
    subject["decision"] = {key: data for key, data in decision.items() if key != "approval"}
    try:
        data = json.dumps(subject, sort_keys=True, ensure_ascii=False,
                          separators=(",", ":"), allow_nan=False).encode("utf-8")
    except (ValueError, UnicodeError, RecursionError) as error:
        raise ChoiceError("decision cannot be serialized canonically") from error
    return hashlib.sha256(data).hexdigest(), masters, flows, configuration


def approved(reader, decision, subject):
    require("approval" in decision, "record an exact approval before implementation")
    record = json_object(reader.pin(decision["approval"], "approval", json_input=True))
    fields(record, "approval", ("schema", "subject_sha256", "actor", "scope", "source"))
    require(record["schema"] == APPROVAL_SCHEMA, "unsupported approval schema")
    require(digest_value(record["subject_sha256"], "approval subject") == subject,
            "approval is for a different decision revision")
    text(record["actor"], "approval actor", 240)
    text(record["scope"], "approved scope")
    reader.pin(record["source"], "authority source")
    require(record["source"]["path"] != decision["approval"]["path"],
            "approval must point to a separate authority source")


def reviewed(reader, value, subject, phase):
    seen = {}
    phases = {"scale"} if phase == "scale" else {"scale", "accept"}
    accepted = set()
    recorded_artifacts = {}
    for proof in rows(value.get("evidence", []), "stage evidence", 1, 128):
        fields(proof, "stage evidence", ("id", "phase", "decision_sha256", "author", "reviewer",
                                        "method", "environment", "outcome", "artifacts", "receipt",
                                        "controls"))
        key = ident(proof["id"], "evidence ID")
        add_unique(seen, key, proof, "evidence ID")
        stage = eq_choice(proof["phase"], {"scale", "accept"}, "evidence phase")
        require(digest_value(proof["decision_sha256"], "evidence decision") == subject,
                f"stale evidence decision: {key}")
        author = text(proof["author"], "evidence author", 240).strip().casefold()
        reviewer = text(proof["reviewer"], "evidence reviewer", 240).strip().casefold()
        require(reviewer not in (author, value["author"].strip().casefold()),
                "evidence requires a distinct reviewer")
        eq_choice(proof["method"], METHODS_BY_KIND.get(value["target_kind"], ACTUAL_METHODS),
                  "actual consumer method")
        text(proof["environment"], "observed environment")
        outcome = eq_choice(proof["outcome"], OUTCOMES, "evidence outcome")
        artifacts = reader.pin_list(proof["artifacts"], "observed artifact", 1)
        reader.pin(proof["receipt"], "observation receipt")
        require(proof["receipt"]["path"] not in artifacts,
                "observation receipt must be separate from consumed artifacts")
        controls = {}
        passed = set()
        for control in rows(proof["controls"], "evidence controls", 1, 64):
            fields(control, "control", ("id", "expect", "outcome", "observation"))
            control_id = ident(control["id"], "control ID")
            add_unique(controls, control_id, control, "control ID")
            expect = eq_choice(control["expect"], {"positive", "negative"}, "control expectation")
            observed = eq_choice(control["outcome"], OUTCOMES, "control outcome")
            reader.pin(control["observation"], "control observation")
            if observed == "pass":
                passed.add(expect)
            if stage in phases:
                require(observed == "pass", f"open or failed control: {control_id}")
        if stage in phases:
            require(outcome == "pass", f"open or failed stage evidence: {key}")
            require(passed == {"positive", "negative"},
                    "positive and negative controls must both pass")
            accepted.add(stage)
            recorded_artifacts.setdefault(stage, {}).update(artifacts)
    require(phases <= accepted, "required evidence missing for: " + ", ".join(sorted(phases - accepted)))
    return {stage: [pins[path] for path in sorted(pins)]
            for stage, pins in sorted(recorded_artifacts.items())}


def _read_record(root, record, expected_sha256, required_kind):
    reader = LocalReads(root)
    actual, _, data = reader.read(record, json_input=True)
    if expected_sha256 is not None:
        require(digest_value(expected_sha256, "expected record SHA-256") == actual,
                "production choice record differs from the previously inspected bytes")
    value = json_object(data)
    today = utc_today()
    requirements, references, candidates = initial(reader, value, today)
    if required_kind is not None:
        eq_choice(required_kind, KINDS, "required target kind")
        require(value["target_kind"] == required_kind,
                f"production choice target kind must be {required_kind}")
    return reader, actual, value, today, requirements, references, candidates


def verify_project(root: Path, phase: str, *, record: str = DEFAULT_RECORD,
                   expected_sha256: str | None = None, required_kind: str | None = None) -> dict:
    """Check the declared requirements for a stage; raise ChoiceError on failure."""
    eq_choice(phase, PHASES, "production choice phase")
    reader, actual, value, today, requirements, references, candidates = _read_record(
        root, record, expected_sha256, required_kind,
    )
    subject, masters, flows, configuration = None, {}, {}, {}
    evidence_artifacts = {}
    if phase != "explore":
        subject, masters, flows, configuration = decided(
            reader, value, requirements, references, candidates, today,
        )
        approved(reader, value["decision"], subject)
        if phase in ("scale", "accept"):
            evidence_artifacts = reviewed(reader, value, subject, phase)
    reader.finish()
    return {
        "ok": True,
        "phase": phase,
        "record_id": value["id"],
        "revision": value["revision"],
        "target_kind": value["target_kind"],
        "record_sha256": actual,
        "decision_sha256": subject,
        "master_count": len(masters),
        "flow_count": len(flows),
        "configuration_artifacts": [configuration[path] for path in sorted(configuration)],
        "evidence_artifacts": evidence_artifacts,
        "checked_paths": sorted(reader.pins),
        "scope": "declared local structure, decision linkage and current source bytes",
        "authority_authenticated": False,
        "craft_certified": False,
        "runtime_authenticated": False,
    }


def decision_subject(root: Path, *, record: str = DEFAULT_RECORD) -> str:
    """Calculate the stable decision digest before attaching its approval."""
    reader, _, value, today, requirements, references, candidates = _read_record(
        root, record, None, None,
    )
    result = decided(reader, value, requirements, references, candidates, today)[0]
    reader.finish()
    return result


CATALOG_FILTERS = ("capability", "language", "platform", "task", "format", "constraint", "role")


def catalog_search(path: Path, filters: dict) -> dict:
    try:
        raw = path.read_bytes()
    except OSError as error:
        raise ChoiceError("Cannot read the bundled technology catalog") from error
    catalog = json_object(raw)
    require(catalog.get("schema") == "atelier.technology-catalog/1", "Unsupported technology catalog")
    found = []
    for group in catalog["categories"]:
        for candidate in group["candidates"]:
            facets = {**group.get("facets", {}), **candidate.get("facets", {})}
            facets["role"] = [candidate["role"]]
            if all(query is None or query.casefold() in {item.casefold() for item in facets.get(key, [])}
                   for key, query in filters.items()):
                found.append({"category": group["id"], **candidate})
    return {"ok": True, "revision": catalog["revision"], "candidates": found,
            "scope": "Search labels and group facets. Verify the actual candidate and target."}


def default_catalog() -> Path:
    location = Path(__file__).resolve().parent
    for candidate in (location / "technology-catalog.json",
                      location.parent / "assets/technology-catalog.json",
                      location.parent / "standards/technology-catalog.json"):
        if candidate.is_file():
            return candidate
    return location / "technology-catalog.json"


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    verify = commands.add_parser("verify", help="Check the prerequisites of one managed stage")
    verify.add_argument("root", type=Path)
    verify.add_argument("--phase", choices=PHASES, required=True)
    verify.add_argument("--record", default=DEFAULT_RECORD)
    verify.add_argument("--expected-sha256")
    verify.add_argument("--required-kind", choices=KINDS)
    subject = commands.add_parser("subject", help="Read the exact pre-approval decision digest")
    subject.add_argument("root", type=Path)
    subject.add_argument("--record", default=DEFAULT_RECORD)
    catalog = commands.add_parser("catalog", help="Find technology candidates by exact indexed facets")
    catalog.add_argument("--catalog", type=Path)
    for key in CATALOG_FILTERS:
        catalog.add_argument("--" + key)
    args = parser.parse_args(argv)
    try:
        if args.command == "subject":
            result = {
                "ok": True, "decision_sha256": decision_subject(args.root, record=args.record),
                "authority_authenticated": False,
            }
        elif args.command == "catalog":
            result = catalog_search(args.catalog or default_catalog(),
                                    {key: getattr(args, key) for key in CATALOG_FILTERS})
        else:
            result = verify_project(args.root, args.phase, record=args.record,
                                    expected_sha256=args.expected_sha256,
                                    required_kind=args.required_kind)
    except ChoiceError as error:
        print(json.dumps({"ok": False, "error": str(error)}, ensure_ascii=True))
        return 1
    print(json.dumps(result, ensure_ascii=True, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
