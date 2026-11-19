#!/usr/bin/env python3
"""Observe an exact setup process without contacting seller infrastructure."""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import runpy
import sys

PAYMENT_PATH = re.compile(r"(?:^|[/.:_\s-])(?:stripe|paypal|paddle|lemonsqueezy|checkout|seller|fulfillment|redemption|redeem|payments?|orders?|callbacks?|payment-analytics|registration)(?:$|[/.:_\s-])", re.I)
RELEVANT = {
    'exec': 'in_process_code',
    'import': 'module_import',
    'subprocess.Popen': 'child_process',
    'os.exec': 'child_process',
    'os.posix_spawn': 'child_process',
    'socket.connect': 'socket_connect',
    'socket.getaddrinfo': 'dns_resolution',
    'urllib.Request': 'http_request',
    'http.client.connect': 'http_connection',
    'sqlite3.connect': 'sqlite_open',
}


class ProductPaymentAttempt(RuntimeError):
    pass


def flattened(value):
    if isinstance(value, (str, bytes, os.PathLike)):
        yield os.fsdecode(value)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from flattened(item)


def event_values(event, args):
    if event == 'exec':
        return (args[0].co_filename,)
    if event == 'import':
        return flattened(args[:2])
    if event in ('subprocess.Popen', 'os.exec', 'os.posix_spawn'):
        return flattened(args[:2])
    if event == 'socket.connect':
        return flattened(args[1:2])
    if event == 'http.client.connect':
        return flattened(args[1:2])
    # Observe only the URL, hostname or SQLite catalog identity. Requests,
    # authorization headers, accounts and other arguments are never logged.
    return flattened(args[:1])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--receipt', required=True, type=Path)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument('--script', type=Path)
    mode.add_argument('--probe', action='store_true')
    parser.add_argument('setup_args', nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    setup_args = args.setup_args[1:] if args.setup_args[:1] == ['--'] else args.setup_args
    path = args.script.resolve(strict=True) if args.script else None
    scope = {
        'schema': 'codex-agents.installer-payment-observation/1',
        'mode': 'positive-fixture' if args.probe else 'actual-python-setup',
        'source_sha256': sha256(path.read_bytes()).hexdigest() if path else None,
        'observed_categories': {},
        'product_payment_attempts': [],
        'product_payment_executions_allowed': 0,
    }
    observed = Counter()

    def check(event, values):
        category = RELEVANT.get(event)
        if not category:
            return
        observed[category] += 1
        if any(PAYMENT_PATH.search(value.replace('\\','/').rsplit('/', 1)[-1] if event in ('exec','import') else value.replace('\\','/'))
               for value in event_values(event, values)):
            scope['product_payment_attempts'].append(category)
            raise ProductPaymentAttempt('The observer detected and blocked an attempted product payment or seller operation.')

    # Open the private receipt before adding the irreversible per-process hook.
    # Archive integrity checks can read seller source as data. Only events
    # capable of executing it, opening a seller DB or making a call are counted.
    with args.receipt.open('x', encoding='utf8') as report:
        sys.addaudithook(check)
        exit_status = 0
        try:
            if args.probe:
                compiled = compile('raise AssertionError("Forbidden code ran")', 'fixture/fulfillment.py', 'exec')
                exec(compiled, {})
            else:
                sys.argv = [str(path), *setup_args]
                sys.path.insert(0, str(path.parent))
                runpy.run_path(str(path), run_name='__main__')
        except ProductPaymentAttempt:
            exit_status = 42
        except SystemExit as result:
            exit_status = result.code
        finally:
            scope['observed_categories'] = dict(observed)
            scope['status'] = 'blocked-attempt' if scope['product_payment_attempts'] else 'zero-observed-attempts'
            json.dump(scope, report, indent=2)
            report.write('\n')
    return 42 if scope['product_payment_attempts'] else exit_status


if __name__ == '__main__':
    raise SystemExit(main())
