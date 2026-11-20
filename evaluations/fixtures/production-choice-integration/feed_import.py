#!/usr/bin/env python3
"""Import one UTF-8 listing feed into an atomically replaced local snapshot."""

import argparse
import csv
import hashlib
import http.client
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile

MAX_BYTES = 64 * 1024
COLUMNS = ["event_id", "title", "remaining_seats"]
LOOPBACK = "127.0.0.1"
FEED_ROUTE = "/events.csv"


class ImportFailure(Exception):
    def __init__(self, code, detail):
        super().__init__(detail)
        self.code = code


def read_export(path):
    try:
        with path.open("rb") as stream:
            return stream.read(MAX_BYTES + 1)
    except OSError as error:
        raise ImportFailure("source_unavailable", "The export file could not be read.") from error


def fetch_export(port, timeout):
    connection = http.client.HTTPConnection(LOOPBACK, port, timeout=timeout)
    try:
        connection.request("GET", FEED_ROUTE)
        response = connection.getresponse()
        if response.status == 403:
            raise ImportFailure("provider_denied", "The source denied access to the export.")
        if response.status != 200:
            raise ImportFailure("source_unavailable", f"The source returned HTTP {response.status}.")
        if response.headers.get_content_type() != "text/csv":
            raise ImportFailure("invalid_feed", "The source did not return a CSV export.")
        length = response.headers.get("Content-Length", "")
        if not re.fullmatch(r"[0-9]{1,6}", length) or int(length) > MAX_BYTES:
            raise ImportFailure("invalid_feed", "The source did not declare a bounded export size.")
        content = response.read(int(length))
        if len(content) != int(length):
            raise ImportFailure("source_unavailable", "The source closed before sending the complete export.")
        return content
    except TimeoutError as error:
        raise ImportFailure("source_timeout", "The source did not respond within the socket timeout.") from error
    except (OSError, http.client.HTTPException) as error:
        raise ImportFailure("source_unavailable", "The loopback source could not be read.") from error
    finally:
        connection.close()


def parse_export(content):
    if len(content) > MAX_BYTES:
        raise ImportFailure("invalid_feed", "The feed exceeds 64 KiB.")
    try:
        reader = csv.reader(io.StringIO(content.decode("utf-8"), newline=""), strict=True)
        if next(reader, None) != COLUMNS:
            raise ImportFailure("invalid_feed", "The expected CSV header is missing.")
        events = {}
        for row in reader:
            if len(row) != len(COLUMNS):
                raise ImportFailure("invalid_feed", f"Unexpected column count at row {reader.line_num}.")
            event_id, title, capacity = row
            if (not re.fullmatch(r"EV-[0-9]{3}", event_id) or event_id in events or
                    not title.strip() or not re.fullmatch(r"[0-9]{1,3}", capacity)):
                raise ImportFailure("invalid_feed", f"Invalid or duplicate event at row {reader.line_num}.")
            events[event_id] = dict(event_id=event_id, title=title, remaining_seats=int(capacity))
    except (UnicodeError, csv.Error) as error:
        raise ImportFailure("invalid_feed", "The feed is not well-formed UTF-8 CSV.") from error
    if not events:
        raise ImportFailure("invalid_feed", "A complete event feed must contain at least one event.")
    return json.dumps(sorted(events.values(), key=lambda event: event["event_id"]),
                      indent=2, ensure_ascii=False).encode("utf-8") + b"\n"


def install_snapshot(path, content):
    if path.exists() and path.read_bytes() == content:
        return False
    stream = tempfile.NamedTemporaryFile(dir=path.parent, prefix=f".{path.name}.", delete=False)
    staging = Path(stream.name)
    try:
        with stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(staging, path)
    finally:
        staging.unlink(missing_ok=True)
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--role", choices=("publisher", "viewer"), required=True)
    parser.add_argument("--snapshot", type=Path, required=True)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--export", type=Path)
    source.add_argument("--loopback-port", type=int)
    parser.add_argument("--socket-timeout", type=float, default=1.0)
    args = parser.parse_args()
    if args.loopback_port is not None and not 1 <= args.loopback_port <= 65535:
        parser.error("--loopback-port must be within 1..65535")
    if not 0 < args.socket_timeout <= 10:
        parser.error("--socket-timeout must be positive and at most 10 seconds")
    try:
        if args.role != "publisher":
            raise ImportFailure("permission_denied", "A publisher role is required before accessing the source.")
        content = read_export(args.export) if args.export is not None else fetch_export(args.loopback_port, args.socket_timeout)
        snapshot = parse_export(content)
        changed = install_snapshot(args.snapshot, snapshot)
    except ImportFailure as error:
        print(json.dumps({"code": error.code, "detail": str(error)}), file=sys.stderr)
        return 1
    except OSError:
        print(json.dumps({"code": "snapshot_unavailable", "detail": "The target snapshot could not be written."}), file=sys.stderr)
        return 1
    print(json.dumps({"code": "published" if changed else "already_current",
                      "snapshot_sha256": hashlib.sha256(snapshot).hexdigest()}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
