"""Small reproducible evaluation utilities; no private data is shipped here."""
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import resource
import sys
import tempfile

def reusable_root(path):
    return next((parent for parent in (path, *path.parents)
                 if (parent / 'standards' / 'ai_production.py').is_file()
                 and (parent / 'AGENTS.md').is_file()), None)


REPO = reusable_root(Path(__file__).resolve().parent)
MAX_JSON = 8 * 1024 * 1024


def require(value, message):
    if not value:
        raise ValueError(message)


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def sha_bytes(value):
    return hashlib.sha256(value).hexdigest()


def sha_file(path):
    return sha_bytes(Path(path).read_bytes())


def decode_json(raw, maximum=MAX_JSON):
    def pairs(values):
        out = {}
        for key, value in values:
            require(key not in out, 'duplicate JSON key')
            out[key] = value
        return out
    def number(value):
        result = float(value)
        require(math.isfinite(result), 'nonfinite JSON numeric overflow')
        return result
    require(len(raw) <= maximum, 'bounded JSON input exceeded')
    return json.loads(raw, object_pairs_hook=pairs, parse_float=number,
                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError('nonfinite JSON')))


def load_json(path, maximum=MAX_JSON):
    with Path(path).open('rb') as stream:
        raw = stream.read(maximum + 1)
    return decode_json(raw, maximum)


def private_root(path):
    root = Path(path).resolve()
    require((REPO is None or not root.is_relative_to(REPO)) and reusable_root(root) is None,
            'raw/evaluation output must remain outside reusable repository')
    root.mkdir(parents=True, exist_ok=True, mode=0o700)
    return root


def atomic_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    data = json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False).encode() + b'\n'
    require(len(data) <= MAX_JSON, 'evaluation output exceeds bounded JSON capacity')
    fd, temporary = tempfile.mkstemp(prefix='.' + path.name, dir=path.parent)
    try:
        with os.fdopen(fd, 'wb') as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def observed_resources(start):
    import time
    usage = resource.getrusage(resource.RUSAGE_SELF)
    rss = usage.ru_maxrss if sys.platform == 'darwin' else usage.ru_maxrss * 1024
    result = {'elapsed_seconds': time.monotonic() - start, 'peak_rss_bytes': rss,
              'cpu_seconds': usage.ru_utime + usage.ru_stime}
    require(result['elapsed_seconds'] <= 60, '60 second command envelope exceeded')
    require(rss <= 256 * 1024 * 1024, '256 MiB command envelope exceeded')
    return result


def at():
    return datetime.now(timezone.utc).isoformat()
