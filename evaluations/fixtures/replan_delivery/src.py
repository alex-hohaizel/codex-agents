"""Minimal FieldSlate roster export. All visits and supervisors are fabricated."""

from datetime import datetime, timezone
import csv
from io import StringIO
from urllib.parse import parse_qs


EXPORT_PATHS = {"/web/roster.csv", "/api/roster.csv"}
FIELDS = ("Visit ID", "Site", "Scheduled at", "Inspector name", "Inspector mobile")
SUPERVISORS = {"lead-nw": "NW", "lead-se": "SE"}
VISITS = {
    "NW": [
        ("NW-101", "École, site A", "2026-11-18 09:00", "Iryna Horbunova", "555-0101"),
        ("NW-102", 'Museum "North"', "2026-11-18 10:30", "Maksym Lytvyn", "555-0102"),
    ],
    "SE": [("SE-101", "Library", "2026-11-18 11:00", "Olena Sokil", "555-0103")],
}


def reply(start_response, status, data, headers=()):
    defaults = [("Content-Type", "text/plain; charset=utf-8")]
    start_response(status, list(headers) or defaults)
    return [data]


class RosterExport:
    def __init__(self, current_available=True):
        self.current_available = current_available
        self.audit = []

    def serialize(self, district):
        stream = StringIO(newline="")
        writer = csv.writer(stream)
        writer.writerow(FIELDS)
        writer.writerows(VISITS[district])
        return stream.getvalue().encode("utf-8")

    def __call__(self, environ, start_response):
        if environ.get("PATH_INFO") not in EXPORT_PATHS:
            return reply(start_response, "404 Not Found", b"Not found")
        if environ.get("REQUEST_METHOD") != "GET":
            return reply(start_response, "405 Method Not Allowed", b"Use GET")

        # Synthetic authentication fixture. In production the gateway supplies the actor.
        actor = environ.get("HTTP_X_FIXTURE_SUPERVISOR")
        district = SUPERVISORS.get(actor)
        requested = parse_qs(environ.get("QUERY_STRING", "")).get("district", [])
        if not district or requested != [district]:
            return reply(start_response, "403 Forbidden", b"District access denied")

        if not self.current_available:
            # Historical R3.1 behavior: serve v1 as fallback.
            payload = self.serialize(district)
        else:
            payload = self.serialize(district)

        self.audit.append({
            "ACTOR_ID": actor,
            "DISTRICT_ID": district,
            "ROW_COUNT": len(VISITS[district]),
            "UTC_TIMESTAMP": datetime.now(timezone.utc).isoformat(),
            "EXPORT_FORMAT_VERSION": "roster-csv-v1",
        })
        return reply(start_response, "200 OK", payload, (
            ("Content-Type", "text/csv; charset=utf-8"),
            ("Content-Disposition", 'attachment; filename="roster.csv"'),
        ))
