#!/usr/bin/env python3
"""Use the exact bundled constructor to check a child without installing it."""
from pathlib import Path

target=Path(__file__).resolve().parents[1]/'skills/agent-foundry/scripts/check_generated_inheritance.py'
if not target.is_file() or target.is_symlink():
    raise SystemExit('Bundled constructor checker is unavailable; verify the complete release.')
namespace={'__file__':str(target),'__name__':'bundled_inheritance_checker'}
exec(compile(target.read_bytes(),str(target),'exec'),namespace)
raise SystemExit(namespace['main']())
