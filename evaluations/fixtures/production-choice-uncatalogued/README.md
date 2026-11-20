# A local audit report with an uncatalogued runtime

Take the open IDs from nested or reformatted JSON and emit a stable JSON array. Refuse malformed input before emitting a report. The target is an isolated Mac service account with only its local allowlisted tools. Its project owner would permit Perl and a paired local shell tool, and require a no-install and no-network workflow. This is a synthetic target constraint, independent of what languages are installed elsewhere on the test computer.

Project stack candidate: system Perl, bundled `JSON::PP`, UTF-8 JSON in and out. The initial candidate catalogue did not name Perl. The specific host can read, running it locally has no metered provider charge, and this fixture can be regenerated and verified from the repository. It publishes no assets or dependencies. The normal handoff is one source file, a command and schema examples. A replacement only needs to preserve the plain JSON I/O. Remove the report command to roll back adoption and retain the input files. Revisit if system Perl or the permission list changes.

| Candidate | Required input and validation | Current target |
| --- | --- | --- |
| Perl with JSON::PP | Handles structure and validates the relevant state, refuses malformed input | `perl -MJSON::PP` verified locally |
| Text line matching | A multiline, reordered document can carry valid entries whose state and ID appear on separate lines | Text matching alone lacks JSON structure for this task |
| Python or Node with a standard JSON decoder | Technically suitable | Outside this scenario's service runtime allowlist |
| New dependency or service | Could support the transformation | Violates the target's permission and dependency constraints |

Check the actual local runtime before choosing it. `JSON::PP` ships in Perl core and its API decodes UTF-8 JSON. The linked documentation was reviewed on 2026-11-20. This is a candidate card for this target and specific operation. [Perl core JSON::PP docs](https://perldoc.perl.org/JSON%3A%3APP)

```sh
PROBE=evaluations/fixtures/production-choice-uncatalogued/report.pl
/usr/bin/perl -MJSON::PP -e 'printf "%vd / %s\n", $^V, $JSON::PP::VERSION'
printf '%s\n' '[{"state":"open","id":"Z10"},' '{"id":"A2",' '"state":"open"},{"id":"C6","state":"closed"}]' | /usr/bin/perl "$PROBE"
printf '%s\n' '[{"id":"A2",' | /usr/bin/perl "$PROBE"
```

The first input produces `["A2","Z10"]`. The malformed input exits with an error and empty standard output. Treat this as exploration until the target owner approves the combination for dependent implementation.
