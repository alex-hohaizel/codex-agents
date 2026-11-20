# Reproduce A10 with a local supplier feed

A community venue receives a small UTF-8 CSV listing of events and remaining seats. The last complete listing remains visible when a delivery fails. Only the trusted publisher may request an update. A repeated delivery leaves the snapshot untouched. The example uses synthetic event titles and seats.

## Decision before the probe

Both candidates use the same input bytes, CSV parser and snapshot writer. The fixture owns the CLI, fixed feed schema and an isolated output directory. The supplier owns the export; the eventual reader consumes the canonical JSON snapshot. The fixture assumes one trusted writer and a controlled regular-file export or loopback endpoint. It requires intact Unicode and CSV quoting, precise permission and source errors, whole-file updates, and an explicit successful retry after repairing the source. Five identical successful repeats measure command startup, source read, parsing and snapshot comparison on the same host. The time measurement describes those runs and does not establish a performance SLA.

| Candidate | Runtime and access | Decision |
| --- | --- | --- |
| Read the supplier's local export | Python standard library, UTF-8 CSV, a local file readable by the publisher | Primary route. The venue can already receive an export. This needs only a controlled local file and retains the previous snapshot when delivery is missing or invalid. |
| Fetch the same CSV from a loopback supplier endpoint | Python standard library, fixed HTTP path on `127.0.0.1`, bounded response size and socket wait | Verified comparison. A long-running server adds an availability dependency and a service boundary. Revisit if the venue needs a pull integration and can govern service ownership, authentication and timeouts. |

The probe uses only local computation and TCP loopback. Each path has USD 0 in third-party charges. Host resource charges are outside this measurement. The synthetic feed permits this replay. No third-party add-on or model is required. The built-in `csv`, `http.client` and `os.replace` supply the parsing, test transport and same-directory atomic replacement. Consulted on 2026-11-20. [Python CSV library](https://docs.python.org/3/library/csv.html) · [HTTP connection and timeout](https://docs.python.org/3/library/http.client.html#http.client.HTTPConnection) · [Atomic file replacement](https://docs.python.org/3/library/os.html#os.replace)

## Run the probe

From the repository root, run Python 3.13 on a desktop or CI host that allows local loopback sockets. Pass a new, private evidence directory.

```bash
python3.13 evaluations/fixtures/production-choice-integration/run_case.py /tmp/venue-feed-a10
```

The runner launches the actual import CLI in separate processes. It serves identical feed bytes over a real ephemeral loopback socket for the HTTP route. The receipt pins all source files and records before/after snapshot hashes, actual request counts, outcomes and measured elapsed time. The two routes must produce identical complete JSON at first import and after recovery. Open `export-snapshot.json` and `loopback-snapshot.json` to inspect the recovered output. HTTP `403`, `503`, a short response and a real read timeout must preserve the last snapshot. Local missing or malformed exports also preserve it. A denied viewer must produce no HTTP request and no snapshot effect. The `--role` argument represents a role resolved by the trusted application in this standalone example. It is not an identity provider. All feed values are fictitious.

## Maintenance boundary

`feed_import.py` owns transport errors, CSV validation and the one snapshot write. `samples.json` is the shared acceptance data. `run_case.py` owns the isolated comparison server and receipts. Only the standard library is imported. To change the feed contract, update both the validator and the sample, then re-run both transports before changing the consumer. Keep the last good snapshot in place during recovery and re-run after verifying the source is complete. The loopback timeout bounds blocking socket operations. Use an overall deadline, production authentication, a concurrent-writer policy and power-loss recovery checks if deploying this pattern with those requirements.
