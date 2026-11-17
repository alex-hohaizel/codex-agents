"""Exercise both HTTP entry points through the WSGI callable without binding a port."""

from datetime import datetime, timedelta
import csv
from io import StringIO
import json
from pathlib import Path
import sys
from wsgiref.util import setup_testing_defaults


def request(app, endpoint, district, actor, method="GET"):
    environ = {}
    setup_testing_defaults(environ)
    environ["REQUEST_METHOD"] = method
    environ["PATH_INFO"] = endpoint
    environ["QUERY_STRING"] = "district=" + district
    if actor is not None:
        environ["HTTP_X_FIXTURE_SUPERVISOR"] = actor
    response = {}

    def start_response(status, headers):
        response["status"] = int(status.split()[0])
        response["headers"] = dict(headers)

    response["body"] = b"".join(app(environ, start_response))
    return response


def expect(condition, label):
    if not condition:
        raise AssertionError(label)


def check(phase):
    # This file lives in review/ in the disposable project.
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from src import RosterExport

    baseline = phase == "historical"
    labels = ("Visit ID", "Site", "Scheduled at", "Inspector name")
    visits = (
        ("NW-101", "École, site A", "2026-11-18 09:00", "Iryna Horbunova"),
        ("NW-102", 'Museum "North"', "2026-11-18 10:30", "Maksym Lytvyn"),
    )
    if baseline:
        labels += ("Inspector mobile",)
        visits = tuple(row + (f"555-010{index}",) for index, row in enumerate(visits, 1))

    checked = []
    for route in ("/web/roster.csv", "/api/roster.csv"):
        app = RosterExport()
        valid = request(app, route, "NW", "lead-nw")
        expect(valid["status"] == 200, f"{route} authorized status")
        expect(valid["headers"].get("Content-Type") == "text/csv; charset=utf-8",
               f"{route} explicit UTF-8 download")
        expect("attachment" in valid["headers"].get("Content-Disposition", ""),
               f"{route} attachment")
        csv_body = valid["body"].decode("utf-8")
        actual = [tuple(fields) for fields in csv.reader(StringIO(csv_body))]
        expect(actual == [labels, *visits], f"{route} exact header, quoted UTF-8 rows and district")
        if not baseline:
            expect(all(value not in csv_body for value in
                       ("Inspector mobile", "555-0101", "555-0102", "SE-101")),
                   f"{route} forbidden values absent")
        checked.append(f"{route}:authorized-csv")

        expect(len(app.audit) == 1, f"{route} exactly one success audit row")
        row = dict(app.audit[0])
        timestamp = datetime.fromisoformat(row.pop("UTC_TIMESTAMP"))
        expect(timestamp.utcoffset() == timedelta(0), f"{route} audit UTC timestamp")
        expect(row == {"ACTOR_ID": "lead-nw", "DISTRICT_ID": "NW", "ROW_COUNT": 2,
                       "EXPORT_FORMAT_VERSION": "roster-csv-v1" if baseline else "roster-csv-v2"},
               f"{route} exact metadata-only audit")
        checked.append(f"{route}:metadata-only-audit")

        for actor in ("lead-se", None):
            denied = request(app, route, "NW", actor)
            expect(denied["status"] == 403 and b"NW-101" not in denied["body"],
                   f"{route} own-district access")
        expect(len(app.audit) == 1, f"{route} denied attempts leave audit unchanged")
        checked.append(f"{route}:district-denial")

        disabled = RosterExport(current_available=False)
        protected = request(disabled, route, "NW", "lead-se")
        expect(protected["status"] == 403 and not disabled.audit,
               f"{route} denied before availability announcement")
        result = request(disabled, route, "NW", "lead-nw")
        if baseline:
            expect(result["status"] == 200 and b"555-0101" in result["body"],
                   f"{route} historical v1 fallback")
        else:
            expect(result["status"] == 503 and b"NW-101" not in result["body"]
                   and "csv" not in result["headers"].get("Content-Type", "")
                   and "Content-Disposition" not in result["headers"]
                   and not disabled.audit, f"{route} no fallback or success audit while disabled")
        checked.append(f"{route}:availability-branch")

    expect(request(RosterExport(), "/fake", "NW", "lead-nw")["status"] == 404,
           "unknown route remains unavailable")
    expect(request(RosterExport(), "/api/roster.csv", "NW", "lead-nw", "POST")["status"] == 405,
           "method contract preserved")
    checked += ["unknown-route", "method-contract"]
    return {"status": "passed", "phase": phase, "checks": checked}


if __name__ == "__main__":
    if len(sys.argv) != 2 or sys.argv[1] not in {"historical", "current"}:
        raise SystemExit("Select historical or current")
    print(json.dumps(check(sys.argv[1]), ensure_ascii=False, sort_keys=True))
