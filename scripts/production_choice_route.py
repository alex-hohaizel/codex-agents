"""Bind project-backed repository operations to a declared production choice."""
from __future__ import annotations

from pathlib import Path

from production_choices import ChoiceError, verify_project

RECORD = "production-choices.json"
CORE_REQUIREMENTS = {f"PQ-{item:02}" for item in range(1, 21)}


def verify_route(root: Path, phase: str, *, required: bool = False) -> dict | None:
    """Keep legacy operations readable; an existing record cannot be ignored."""
    try:
        (root / RECORD).lstat()
    except FileNotFoundError:
        if not required:
            return None
        raise ChoiceError(f"{RECORD} is required before {phase}") from None
    return verify_project(root, phase)
