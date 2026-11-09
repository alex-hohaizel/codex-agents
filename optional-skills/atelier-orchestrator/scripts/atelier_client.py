#!/usr/bin/env python3
"""Bounded loopback client for Agent Atelier API1. No implicit task/effect authority."""
import argparse
import base64
import hashlib
import hmac
import http.cookiejar
import json
import os
from pathlib import Path
import re
import secrets
import stat
import sys
import urllib.error
import urllib.parse
import urllib.request


def strict_json(raw):
    def unique(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key: ' + key)
            result[key] = value
        return result
    def finite(value):
        raise ValueError('nonfinite JSON value: ' + value)
    return json.loads(raw, object_pairs_hook=unique, parse_constant=finite)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError('local service redirect rejected')


def owner_credentials(data_dir, port):
    """Only a private local credential + verified instance can bootstrap this client."""
    root = Path(data_dir).expanduser().resolve(strict=True)
    def read(name):
        file = root / name
        info = file.lstat()
        if not stat.S_ISREG(info.st_mode) or stat.S_ISLNK(info.st_mode) or info.st_mode & 0o077 or info.st_uid != os.getuid() or info.st_size > 16 * 1024:
            raise ValueError('private bounded owner/runtime file required')
        return strict_json(file.read_text(encoding='utf-8'))
    runtime = read('runtime.json')
    owner = read('owner-credentials.json')
    base = 'http://127.0.0.1:' + str(port)
    if runtime.get('origin') != base or runtime.get('port') != port or Path(runtime.get('data_dir', '')).resolve() != root:
        raise ValueError('runtime origin/data directory mismatch')
    instance = runtime.get('instance_id', '')
    key = owner.get('control_key', '')
    if not re.fullmatch(r'instance_[a-f0-9-]{36}', instance) or owner.get('instance_id') != instance or not re.fullmatch(r'[A-Za-z0-9_-]{43}', key):
        raise ValueError('owner instance/key mismatch')
    return base, instance, key


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('operation', choices=['status', 'doctor', 'projects', 'workspace', 'source',
                                       'prepare', 'dispatch', 'interrupt', 'reconcile', 'command'])
    p.add_argument('--port', type=int, default=4317)
    p.add_argument('--data-dir', default=str(Path.home() / 'Library/Application Support/Agent Atelier'))
    p.add_argument('--project')
    p.add_argument('--path')
    p.add_argument('--data', help='JSON payload file; do not put secrets in arguments')
    p.add_argument('--command-id', help='retain identity across unknown command outcomes')
    p.add_argument('--expected-revision')
    args = p.parse_args()
    try:
        if not 1024 <= args.port <= 65535:
            raise ValueError('invalid local port')
        base, instance, control_key = owner_credentials(args.data_dir, args.port)
        opener = urllib.request.build_opener(NoRedirect(), urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        def request(path, data=None, csrf=None, control=None):
            headers = {'Origin': base, 'Accept': 'application/json'}
            if csrf:
                headers['X-Atelier-CSRF'] = csrf
            if control:
                headers['X-Atelier-Control'] = control
            if data is not None:
                headers['Content-Type'] = 'application/json'
            req = urllib.request.Request(base + path,
                data=json.dumps(data, allow_nan=False).encode() if data is not None else None,
                headers=headers)
            with opener.open(req, timeout=20) as response:
                raw = response.read(4 * 1024 * 1024 + 1)
            if len(raw) > 4 * 1024 * 1024:
                raise ValueError('response exceeds bounded client read')
            return strict_json(raw)
        nonce = secrets.token_urlsafe(24)
        proof = request('/health?owner_probe=' + nonce)
        decoded_key = base64.urlsafe_b64decode(control_key + '=')
        expected = base64.urlsafe_b64encode(hmac.new(decoded_key, ('atelier.instance.' + instance + '.' + nonce).encode(), hashlib.sha256).digest()).decode().rstrip('=')
        if proof.get('instance_id') != instance or not hmac.compare_digest(str(proof.get('owner_proof', '')), expected):
            raise ValueError('local listener ownership proof failed')
        request('/api/v1/session', control=control_key)
        bootstrap = request('/api/v1/bootstrap')
        if args.operation == 'status':
            result = {'version': bootstrap.get('version'), 'capabilities': bootstrap.get('capabilities'),
                      'projects': len(bootstrap.get('projects', [])), 'jobs': bootstrap.get('jobs', [])}
        elif args.operation == 'doctor':
            result = request('/api/v1/doctor')
        elif args.operation == 'projects':
            result = bootstrap.get('projects', [])
        elif args.operation in ['workspace', 'source']:
            if not args.project:
                raise ValueError('--project required')
            path = '/api/v1/projects/' + urllib.parse.quote(args.project, safe='')
            path += '/workspace' if args.operation == 'workspace' else '/source?' + urllib.parse.urlencode({'path': args.path or ''})
            result = request(path)
        else:
            if not args.data:
                raise ValueError('--data payload file required')
            file = Path(args.data)
            if not file.is_file() or file.is_symlink() or file.stat().st_size > 1024 * 1024:
                raise ValueError('bounded regular payload file required')
            payload = strict_json(file.read_text(encoding='utf-8'))
            if not isinstance(payload, dict):
                raise ValueError('payload must be an object')
            if args.operation == 'command':
                command = payload
            else:
                operation = {'prepare': 'task.prepare', 'dispatch': 'task.dispatch',
                             'interrupt': 'job.interrupt', 'reconcile': 'job.reconcile'}[args.operation]
                if not args.command_id:
                    raise ValueError('persist an explicit --command-id before mutation; reuse it when reconciling')
                command = {'command_id': args.command_id, 'operation': operation,
                           'project_id': args.project, 'expected_revision': args.expected_revision,
                           'payload': payload}
            if not isinstance(command.get('command_id'), str) or not command['command_id']:
                raise ValueError('persist an explicit command_id before mutation')
            result = request('/api/v1/commands', command, bootstrap['csrf_token'])
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, KeyError, TypeError, urllib.error.URLError) as error:
        ident = locals().get('command', {}).get('command_id')
        print(json.dumps({'ok': False, 'error': str(error), 'command_id': ident,
                          'outcome': 'unknown_until_reconciled' if ident else 'not_dispatched',
                          'next_action': 'read the existing command receipt before retrying' if ident else 'correct input/access'}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
