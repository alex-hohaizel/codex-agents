# FieldSlate roster change for the next sprint revision

The existing FieldSlate application exports municipal inspection visits. A supervisor can request only their own district. The previous release included Inspector mobile in both web and API exports and allowed the old export path when the current export was unavailable.

The revised requirements in requirements.json remove Inspector mobile, preserve the rest of the CSV and the district boundary, set roster-csv-v2 in successful audit entries, and disable both entry points with a 503 when the current export is unavailable. Access denial still takes precedence over an unavailable export. Audit rows remain metadata only.

Keep prior acceptance receipt EXP-12 as historical evidence. Keep scheduling work UI-07 in motion. Create an implementation task for the shared v2 web/API export. Split the planned release packet into separate user-facing documentation and operations checks that wait for the implementation. The obsolete task to restore the legacy fallback may be retired. The synthetic owner will consider only that specific plan.

The implementation task owns src.py, including output format, successful audit and the unavailable branch. It must leave later release follow-up, scheduling, prior evidence and all project planning records untouched.
