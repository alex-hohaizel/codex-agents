#!/usr/bin/env python3
"""Verify the current showcase, with an explicit mode when supplied."""
import sys

from build_campaign import main


if __name__ == "__main__":
    modes = {"--check-source", "--check", "--verify", "--export", "--refresh-markdown"}
    if not modes.intersection(sys.argv[1:]):
        sys.argv.append("--check")
    raise SystemExit(main())
