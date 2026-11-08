#!/usr/bin/env python3
"""Check all canonical bilingual campaign outputs without changing them."""
from build_campaign import main
import sys
if __name__=='__main__':
    if '--check' not in sys.argv:sys.argv.append('--check')
    raise SystemExit(main())
