"""Verify the production choice contract is mapped to all distributed consumers."""
import json
from pathlib import Path, PurePosixPath


def check_coverage(root: Path, release: dict, skill_names: list[str]) -> list[str]:
    def read(relative):
        path = PurePosixPath(relative)
        if path.is_absolute() or not path.parts or ".." in path.parts or "\\" in relative:
            raise ValueError(f"Invalid coverage path {relative}")
        target = root.joinpath(*path.parts)
        if target.is_symlink() or not target.is_file() or not target.resolve().is_relative_to(root.resolve()):
            raise ValueError(f"Missing coverage source {relative}")
        return target

    try:
        contract = release["production_choices"]
        if contract["schema"] != "atelier.production-choices/1":
            raise ValueError("Unknown production choice record schema")
        for key in ("standard", "validator", "catalog"):
            read(contract[key])
        coverage = json.loads(read(contract["coverage"]).read_text(encoding="utf-8"))
        if coverage["schema"] != "atelier.production-choice-coverage/1":
            raise ValueError("Unknown coverage schema")
        roles = json.loads(read("agent-profiles/manifest.json").read_text(encoding="utf-8"))
        role_ids = {path.stem for path in (root / "agent-profiles").glob("foundry-*.toml")}
        stages = {f"S{n}" for n in range(1, 7)}
        requirements = {f"PQ-{n:02}" for n in range(1, 21)}
        acceptance = {f"A{n:02}" for n in range(1, 17)}
        if set(coverage["stages"]) != stages:
            raise ValueError("Coverage stages differ from S1–S6")
        rows, scenarios = coverage["requirements"], coverage["acceptance"]
        if len(rows) != len(requirements) or {r["id"] for r in rows} != requirements:
            raise ValueError("Coverage requirements differ from PQ-01–PQ-20")
        if len(scenarios) != len(acceptance) or {r["id"] for r in scenarios} != acceptance:
            raise ValueError("Coverage scenarios differ from A01–A16")
        consumers = coverage["consumers"]
        ids = {item["id"] for item in consumers}
        expected = set(skill_names) | role_ids | {
            "orchestrator", "maintenance", "host-profile", "workbench", "portable",
            "foundry-factory-import-migrate", "design-constructor", "ux-and-documents",
            "tickets-and-tracker", "distribution", "release", "operator-docs", "work-host",
        }
        if len(ids) != len(consumers) or expected - ids or len(role_ids) != len(roles["roles"]):
            raise ValueError(f"Coverage consumers duplicate or missing {sorted(expected - ids)}")
        for item in consumers:
            if (not item["pq"] or not set(item["pq"]) <= requirements or not item["stages"]
                    or not set(item["stages"]) <= stages or not item["sources"]):
                raise ValueError(f"Incomplete consumer {item['id']}")
            for path in item["sources"]:
                read(path)
        for row in rows:
            linked = [c for c in consumers if row["id"] in c["pq"]]
            if (not row["acceptance"] or not set(row["acceptance"]) <= acceptance
                    or set(row["consumers"]) != {c["id"] for c in linked}
                    or set(row["stages"]) != {stage for c in linked for stage in c["stages"]}):
                raise ValueError(f"Stale trace for {row['id']}")
        for scenario in scenarios:
            if not scenario["requirements"] or not set(scenario["requirements"]) <= requirements:
                raise ValueError(f"Cannot trace {scenario['id']} to its requirements")
        for name in skill_names:
            contents = read(f"kit/skills/{name}/SKILL.md").read_text(encoding="utf-8")
            if "references/production-choices.md" not in contents:
                raise ValueError(f"{name} does not load production choices directly")
            read(f"kit/skills/{name}/references/production-choices.md")
        return []
    except (KeyError, TypeError, ValueError, OSError) as exc:
        return [f"production choice coverage: {exc}"]
