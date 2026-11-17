"""Check real local dispatch reservations across CLI processes."""

import json
import os
from pathlib import Path
import select
import signal
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

SCRIPTS = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPTS))
import ticket_dispatch as dispatch
import ticket_handoff as handoff
import ticket_replan_correction as correction
import ticket_replan_plan as model
import ticket_replan_store as store
import ticket_worktree as worktree
import ticket_worktree_checkpoint as checkpoint

context = handoff.context


class TicketDispatchTest(unittest.TestCase):
    def setUp(self):
        scratch = TemporaryDirectory()
        self.addCleanup(scratch.cleanup)
        self.scratch = Path(scratch.name).resolve()
        self.root = self.scratch / "repo"
        self.root.mkdir()
        self.projection = "plans/tickets.json"
        for name in ("plans", "review", "product"):
            (self.root / name).mkdir()
        (self.root / "product/export.py").write_text("def export(): return 'v1'\n", encoding="utf-8")
        requirement = "Both export routes use the four approved columns."
        self.save("requirements.json", {"requirements": [{"id": "R-CSV", "text": requirement}]})
        self.save(self.projection, {
            "schema_version": model.tree.PROJECTION, "project_id": "exports", "native_revision": "r1",
            "requirement_sources": [self.pin("requirements.json")],
            "tickets": [{"id": "I", "kind": "initiative", "title": "Delivery", "status": "planned"}],
        })
        (self.root / "review/baseline.json").write_bytes((self.root / self.projection).read_bytes())
        self.git("init", "-q", "--template=")
        self.git("add", self.projection, "requirements.json", "product/export.py")
        self.git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid",
                 "-c", "core.hooksPath=/dev/null", "-c", "commit.gpgsign=false",
                 "commit", "-qm", "initial fixture")
        self.save("review/request.json", {
            "schema_version": model.REQUEST, "project_id": "exports", "native_revision": "r1",
            "target_revision": "r2", "projection_sha256": self.pin(self.projection)["sha256"],
            "changes": [
                {
                    "action": "create", "rationale": "Assign work for the approved export.",
                    "sources": [{**self.pin("requirements.json"), "requirement_id": "R-CSV",
                                 "excerpt": requirement}],
                    "ticket": {"id": key, "title": key, "kind": "story", "parent": "I",
                               "requirement_ids": ["R-CSV"], "acceptance": "Exact header"},
                }
                for key in ("T-A", "T-B", "T-C")
            ],
        })
        plan = model.build_plan(self.root, self.projection, "review/request.json")
        self.plan_sha = store.plan_sha256(plan)
        self.save("review/approval.json", {
            "schema_version": store.DECISION, "decision": "approve", "operation_id": "approved-replan",
            **{key: plan[key] for key in store.BINDING}, "plan_sha256": self.plan_sha,
            "authority_ref": "Fixture owner approval",
        })
        result = store.apply_plan(self.root, self.projection, "review/request.json", "review/approval.json",
                                  self.pin("review/approval.json")["sha256"])
        self.assertTrue(result["verified_readback"])

    def git(self, *argv):
        env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
        env.update(GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull)
        subprocess.run(["git", *argv], cwd=self.root, env=env, check=True,
                       capture_output=True, timeout=10)

    def save(self, name, data):
        (self.root / name).write_bytes(store.projection_bytes(data))

    def pin(self, name):
        return {"path": name, "sha256": context.digest((self.root / name).read_bytes())}

    def packet(self, name, ticket, path, *, returns=None):
        handoff_name = f"review/{name}.json"
        packet = handoff.prepare(
            self.root, self.projection, "approved-replan", self.plan_sha, ticket, [path],
            returns or f"review/{name}-return.json",
        )
        self.save(handoff_name, packet)
        return handoff_name, self.pin(handoff_name)["sha256"]

    def cli(self, mode, *args, expected=0):
        command = [sys.executable, "-B", str(SCRIPTS / "ticket_dispatch.py"),
                   mode, "--root", str(self.root), *args]
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        self.assertEqual(expected, result.returncode, result.stderr or result.stdout)
        return json.loads(result.stdout if expected == 0 else result.stderr)

    def claim(self, identifier, packet, *, binding=None, expected=0):
        binding_args = () if binding is None else ("--binding", str(binding), "--binding-sha256", self.sha(binding))
        return self.cli("claim", "--reservation-id", identifier, "--handoff", packet[0],
                        "--handoff-sha256", packet[1], *binding_args, expected=expected)

    def sha(self, path):
        return context.digest(path.read_bytes())

    def bind(self, key, path="product/export.py", *, worker=None, record_name=None):
        base = worktree.git_text(self.root, "rev-parse", "HEAD")
        data = worktree.make_binding(
            self.root, base, worker or self.scratch / key, f"codex/{key}", [path], create=worker is None,
        )
        name = self.scratch / (record_name or f"{key}-binding.json")
        name.write_bytes(store.projection_bytes(data))
        return name, Path(data["worktree"])

    def freeze(self, binding, native_ref, readback, *, name="checkpoint"):
        stop = self.scratch / f"{name}-interruption.json"
        stop.write_bytes(store.projection_bytes({
            "schema_version": checkpoint.INTERRUPTION,
            "binding_sha256": self.sha(binding),
            "state": "interrupted",
            "native_run_ref": native_ref,
            "readback_ref": readback,
            "next_action": "Read and complete the durable edit, then verify the export.",
        }))
        frozen = self.scratch / f"{name}.json"
        frozen.write_bytes(store.projection_bytes(checkpoint.capture(binding, self.sha(binding), stop, self.sha(stop))))
        return frozen

    def reserve_resume(self, identifier, packet, frozen, effects, *, expected=0):
        return self.cli(
            "reserve-resume", "--reservation-id", identifier, "--handoff-sha256", packet[1],
            "--checkpoint", str(frozen), "--checkpoint-sha256", self.sha(frozen),
            "--effects-readback-ref", effects, expected=expected,
        )

    def abort_resume(self, identifier, packet, frozen, readback, *, attempt_id=None, expected=0):
        return self.cli(
            "abort-resume", "--reservation-id", identifier, "--handoff-sha256", packet[1],
            "--checkpoint-sha256", self.sha(frozen), "--readback-ref", readback,
            *(("--attempt-id", attempt_id) if attempt_id is not None else ()), expected=expected,
        )

    def retry_resume(self, identifier, packet, frozen, abort_sha256, attempt_id, readback, *, expected=0):
        return self.cli(
            "retry-resume", "--reservation-id", identifier, "--handoff-sha256", packet[1],
            "--checkpoint-sha256", self.sha(frozen), "--abort-sha256", abort_sha256,
            "--attempt-id", attempt_id, "--readback-ref", readback, expected=expected,
        )

    def observe(self, identifier, packet, phase, readback, job_ref=None, *, attempt_id=None, expected=0):
        return self.cli("observe", "--reservation-id", identifier, "--handoff-sha256", packet[1],
                        "--phase", phase, "--readback-ref", readback,
                        *(("--native-job-ref", job_ref) if job_ref is not None else ()),
                        *(("--attempt-id", attempt_id) if attempt_id is not None else ()),
                        expected=expected)

    def prepare_next(self, key, request):
        request_path = f"review/{key}-request.json"
        decision_path = f"review/{key}-decision.json"
        self.save(request_path, {
            "project_id": "exports", "native_revision": "r2", "target_revision": "r3",
            "projection_sha256": self.pin(self.projection)["sha256"], **request,
        })
        plan = store.build_plan(self.root, self.projection, request_path)
        self.save(decision_path, {
            "schema_version": store.DECISION, "decision": "approve", "operation_id": key,
            **{field: plan[field] for field in store.BINDING}, "plan_sha256": store.plan_sha256(plan),
            "authority_ref": "Fixture owner approved the exact replan",
        })
        return request_path, decision_path, self.pin(decision_path)["sha256"]

    def apply_next(self, pins):
        return store.apply_plan(self.root, self.projection, *pins)

    def test_replan_cannot_change_reserved_work_and_allows_an_independent_change(self):
        first = self.packet("first", "T-A", "product/export.py")
        self.claim("job-a", first)
        self.assertEqual(store.apply_plan(
            self.root, self.projection, "review/request.json", "review/approval.json",
            self.pin("review/approval.json")["sha256"],
        )["status"], "replayed")
        requirement = {**self.pin("requirements.json"), "requirement_id": "R-CSV",
                       "excerpt": "Both export routes use the four approved columns."}
        change = {
            "action": "replace", "ticket_id": "T-A", "rationale": "Change the implementation ticket.",
            "sources": [requirement],
            "ticket": {"id": "T-D", "title": "D", "kind": "story", "parent": "I",
                       "requirement_ids": ["R-CSV"], "acceptance": "Exact header"},
        }
        before = self.pin(self.projection)
        blocked = self.prepare_next("affected", {"schema_version": model.REQUEST, "changes": [change]})
        with self.assertRaisesRegex(context.ContextError, "affects an unresolved Builder reservation: T-A"):
            self.apply_next(blocked)
        self.assertEqual(before, self.pin(self.projection))

        change["ticket_id"] = "T-B"
        independent = self.prepare_next("independent", {"schema_version": model.REQUEST, "changes": [change]})
        self.assertTrue(self.apply_next(independent)["verified_readback"])
        self.assertEqual(self.cli("status", "--reservation-id", "job-a")["reservation"]["phase"], "reserved")
        with self.assertRaisesRegex(context.ContextError, "historical"):
            handoff.verify(self.root, *first)

    def correction_pins(self):
        witness = "review/no-dispatch.json"
        self.save(witness, {
            "schema_version": correction.NO_DISPATCH, "status": "no-dispatch-observed",
            "project_id": "exports", "native_revision": "r2", "operation_id": "approved-replan",
            "projection": self.pin(self.projection), "plan_sha256": self.plan_sha,
            "authority_ref": "Fixture operator reports no dispatch from owning host",
        })
        return self.prepare_next("undo", {
            "schema_version": correction.REQUEST, "undo_operation_id": "approved-replan",
            "undo_plan_sha256": self.plan_sha, "baseline": self.pin("review/baseline.json"),
            "no_dispatch": self.pin(witness), "rationale": "Restore before starting planned work.",
        })

    def test_correction_refuses_prior_started_reservation_even_after_finished(self):
        pins = self.correction_pins()
        first = self.packet("first", "T-A", "product/export.py")
        self.claim("job-a", first)
        before = self.pin(self.projection)
        with self.assertRaisesRegex(context.ContextError, "unresolved or previously started"):
            self.apply_next(pins)
        self.observe("job-a", first, "running", "Host start record", "native/11")
        self.observe("job-a", first, "finished", "Host finish record", "native/11")
        with self.assertRaisesRegex(context.ContextError, "unresolved or previously started"):
            self.apply_next(pins)
        self.assertEqual(before, self.pin(self.projection))

    def test_correction_after_operator_reconciled_early_reservation_without_launch(self):
        pins = self.correction_pins()
        first = self.packet("first", "T-A", "product/export.py")
        self.claim("job-a", first)
        self.observe("job-a", first, "released", "Owning host confirms no launch occurred")
        result = self.apply_next(pins)
        self.assertTrue(result["verified_readback"])
        self.assertEqual(result["native_revision"], "r3")

    def test_disjoint_reservations_share_checkout_and_casefold_aliases_conflict(self):
        first = self.packet("first", "T-A", "product/export.py")
        second = self.packet("second", "T-B", "product/report.py")
        case_alias = self.packet("alias", "T-C", "product/EXPORT.py")
        same_ticket = self.packet("same", "T-A", "product/elsewhere.py")
        prior_input = self.packet("prior-input", "T-C", "review/FIRST.json")
        same_return = self.packet("conflicting-return", "T-C", "product/other.py",
                                  returns="review/FIRST-RETURN.json")
        initial = self.claim("job-a", first)
        self.assertTrue(initial["admission_rechecked"])
        self.assertEqual(initial["project_id"], "exports")
        self.assertFalse(initial["launch_performed"])
        self.assertFalse(initial["native_receipt_authenticated"])
        self.assertEqual(self.claim("job-b", second)["reservation"]["phase"], "reserved")
        self.assertIn("path overlaps", self.claim("job-c", case_alias, expected=2)["error"])
        self.assertIn("path overlaps", self.claim("job-c", same_return, expected=2)["error"])
        self.assertIn("path overlaps", self.claim("job-c", prior_input, expected=2)["error"])
        self.assertIn("ticket already reserved", self.claim("job-other", same_ticket, expected=2)["error"])
        self.assertIn("handoff already has", self.claim("duplicate", first, expected=2)["error"])
        self.assertEqual(self.claim("job-a", first)["status"], "replayed")
        self.assertFalse(self.claim("job-a", first)["admission_rechecked"])
        listed = self.cli("list")
        self.assertEqual([(row["ticket_id"], row["phase"]) for row in listed["reservations"]],
                         [("T-A", "reserved"), ("T-B", "reserved")])

    def test_observations_reconcile_launch_without_double_reservation_or_release(self):
        first = self.packet("first", "T-A", "product/export.py")
        second = self.packet("second", "T-B", "product/report.py")
        self.claim("job-a", first)
        self.claim("job-b", second)
        self.assertIn("missing text", self.observe("job-a", first, "released", "", expected=2)["error"])
        self.assertEqual(self.observe("job-a", first, "running", "Host showed started: record 12",
                                      "native/12")["reservation"]["phase"], "running")
        self.assertIn("already observed", self.observe(
            "job-b", second, "running", "Host record 12", "native/12", expected=2)["error"])
        self.assertIn("invalid dispatch phase", self.observe(
            "job-a", first, "released", "No return yet", expected=2)["error"])
        self.assertIn("differs", self.observe(
            "job-a", first, "finished", "Host completion record", "native/13", expected=2)["error"])
        done = self.observe("job-a", first, "finished", "Host completion record", "native/12")
        self.assertEqual(done["reservation"]["phase"], "finished")
        self.assertFalse(done["launch_performed"])
        self.assertFalse(done["process_permissions_enforced"])
        reread = self.cli("status", "--reservation-id", "job-a")
        self.assertEqual(reread["reservation"], done["reservation"])
        changed_packet = self.packet("changed-return", "T-A", "product/export.py")
        self.assertIn("already started this ticket revision",
                      self.claim("second-launch", changed_packet, expected=2)["error"])
        self.assertEqual(self.observe("job-a", first, "running", "Host showed started: record 12",
                                      "native/12")["status"], "replayed")
        released = self.observe("job-b", second, "released", "Host reconciled: launch did not occur")
        self.assertEqual(released["reservation"]["phase"], "released")
        self.assertIn("handoff already has", self.claim("repeat-after-release", second, expected=2)["error"])
        fresh_packet = self.packet("after-verified-release", "T-B", "product/report.py")
        self.assertEqual(self.claim("job-b-confirmed-retry", fresh_packet)["reservation"]["phase"], "reserved")
        self.assertIn("reservation identity", self.observe(
            "job-a", second, "finished", "Other ticket", "native/12", expected=2)["error"])

    def test_claim_rechecks_nested_projection_lock_and_rejects_stale_handoff(self):
        first = self.packet("first", "T-A", "product/export.py")
        ledger = self.root / dispatch.FILENAME
        with store.projection_lock(self.root / self.projection):
            self.assertIn("busy", self.claim("job-a", first, expected=2)["error"])
        self.assertFalse(ledger.exists())
        self.assertEqual(self.claim("job-a", first)["reservation"]["phase"], "reserved")
        stale = self.packet("stale", "T-B", "product/report.py")
        (self.root / "product/report.py").write_text("Different prior bytes\n", encoding="utf-8")
        self.assertIn("stale", self.claim("job-b", stale, expected=2)["error"])
        self.assertEqual(self.cli("status", "--reservation-id", "job-b")["status"], "no-local-reservation")
        self.assertEqual(ledger.stat().st_nlink, 1)
        self.assertFalse(list(self.root.glob(".ticket-dispatch-*")))

    def test_builder_scope_cannot_write_ledger_or_nested_lock_metadata(self):
        self.claim("job-a", self.packet("first", "T-A", "product/export.py"))
        for index, target in enumerate((dispatch.FILENAME, "plans/.ticket-replan.lock", ".ticket-replan.lock")):
            with self.subTest(target=target):
                name, _ = self.packet(f"bad-{index}", "T-B", "product/report.py")
                row = json.loads((self.root / name).read_bytes())
                row["write_paths"] = [self.pin(target)]
                self.save(name, row)
                self.assertIn("protected write path", self.claim(
                    "job-b", (name, self.pin(name)["sha256"]), expected=2
                )["error"])
        self.assertEqual(len(self.cli("list")["reservations"]), 1)

    def test_observed_process_interruption_has_only_one_continuation_under_the_original_reservation(self):
        packet = self.packet("first", "T-A", "product/export.py")
        binding, worker = self.bind("first")
        self.assertEqual(self.claim("job-a", packet, binding=binding)["reservation"]["phase"], "reserved")
        worker_code = (
            "import os, time\n"
            "with open('product/export.py', 'w') as stream:\n"
            "    stream.write(\"def export(): return 'partial'\\n\")\n"
            "    stream.flush()\n"
            "    os.fsync(stream.fileno())\n"
            "print('edit persisted', flush=True)\n"
            "time.sleep(90)\n"
        )
        with subprocess.Popen([sys.executable, "-c", worker_code], cwd=worker, text=True,
                              stdout=subprocess.PIPE, start_new_session=True) as process:
            try:
                native_ref = f"local-process/{process.pid}"
                self.observe("job-a", packet, "running", "Owning test runner started child", native_ref)
                self.assertTrue(select.select([process.stdout], [], [], 10)[0], "worker failed to persist edit")
                self.assertEqual(process.stdout.readline().strip(), "edit persisted")
                self.assertIsNone(process.poll())
                self.assertEqual(self.cli("status", "--reservation-id", "job-a")["reservation"]["phase"], "running")
                process.terminate()
                self.assertEqual(process.wait(timeout=10), -signal.SIGTERM)
            finally:
                if process.poll() is None:
                    process.kill()
        stop_result = f"Owning runner waited for process {process.pid}, exit {process.returncode}"
        frozen = self.freeze(binding, native_ref, stop_result)
        effects = "Owning runner verified its local-file-only operation and inspected the exact dirty paths"

        # Separate CLI contenders race on the same durable continuation.
        command = [sys.executable, "-B", str(SCRIPTS / "ticket_dispatch.py"), "reserve-resume",
                   "--root", str(self.root), "--reservation-id", "job-a", "--handoff-sha256", packet[1],
                   "--checkpoint", str(frozen), "--checkpoint-sha256", self.sha(frozen),
                   "--effects-readback-ref", effects]
        with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as first:
            with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as second:
                receipts = []
                for contender in (first, second):
                    stdout, stderr = contender.communicate(timeout=15)
                    if contender.returncode == 0:
                        receipts.append(json.loads(stdout))
                    else:
                        self.assertEqual(contender.returncode, 2, stderr)
                        self.assertIn("busy", json.loads(stderr)["error"])
        self.assertEqual([item["status"] for item in receipts].count("resume-reserved"), 1)
        reserved = next(item for item in receipts if item["status"] == "resume-reserved")
        self.assertTrue(reserved["admission_rechecked"])
        self.assertFalse(reserved["native_receipt_authenticated"])
        self.assertFalse(reserved["launch_performed"])
        self.assertEqual(reserved["continuation"]["resumed_from"], native_ref)
        self.assertEqual(reserved["reservation"]["events"][-1]["readback_ref"], stop_result)

        replay = self.reserve_resume("job-a", packet, frozen, effects)
        self.assertEqual(replay["status"], "replayed")
        self.assertFalse(replay["admission_rechecked"])
        self.assertIn("path overlaps", self.claim(
            "different-ticket", self.packet("other", "T-B", "product/export.py"), expected=2,
        )["error"])
        self.assertIn("invalid dispatch phase", self.observe(
            "job-a", packet, "released", "No response to dispatch request", expected=2,
        )["error"])
        self.assertIn("already observed", self.observe(
            "job-a", packet, "running", "Duplicate ID from stopped process", native_ref, expected=2,
        )["error"])

        complete_code = (
            "from pathlib import Path\n"
            "p = Path('product/export.py')\n"
            "assert p.read_text() == \"def export(): return 'partial'\\n\"\n"
            "p.write_text(\"def export(): return 'complete'\\n\")\n"
        )
        with subprocess.Popen([sys.executable, "-c", complete_code], cwd=worker) as resumed:
            next_ref = f"local-process/{resumed.pid}"
            self.observe("job-a", packet, "running", "Owning runner started the continuation", next_ref)
            self.assertEqual(resumed.wait(timeout=10), 0)
        self.assertIn("differs", self.observe(
            "job-a", packet, "finished", "Old terminal result", native_ref, expected=2,
        )["error"])
        done = self.observe("job-a", packet, "finished", "Owning runner waited for success", next_ref)
        self.assertEqual([item["phase"] for item in done["reservation"]["events"]],
                         ["reserved", "running", "resume-reserved", "running", "finished"])
        self.assertEqual((worker / "product/export.py").read_text(), "def export(): return 'complete'\n")
        self.assertEqual((self.root / "product/export.py").read_text(), "def export(): return 'v1'\n")
        # The status replay survives legitimate edits to the now-completed worktree.
        self.assertEqual(self.reserve_resume("job-a", packet, frozen, effects)["status"], "replayed")

    def test_recovery_requires_the_original_worktree_exact_stopped_job_and_unchanged_project(self):
        first = self.packet("first", "T-A", "product/export.py")
        binding, worker = self.bind("first")
        self.claim("job-a", first, binding=binding)
        same_worker_binding, _ = self.bind("first", "product/report.py", worker=worker,
                                           record_name="competing-binding.json")
        self.assertIn("already has an active reservation", self.claim(
            "job-b", self.packet("second", "T-B", "product/report.py"),
            binding=same_worker_binding, expected=2,
        )["error"])
        observed_job = "native/first"
        self.observe("job-a", first, "running", "Actual start recorded by fixture operator", observed_job)
        effects = "Fixture operator inspected local edits and reconciled all owned operations"
        target = worker / "product/export.py"
        target.write_text("partial\n", encoding="utf-8")
        wrong_job = self.freeze(binding, "native/other", "Foreign run terminal", name="wrong-job")
        self.assertIn("current dispatch attempt", self.reserve_resume("job-a", first, wrong_job, effects,
                                                                    expected=2)["error"])
        foreign_binding, foreign_worker = self.bind("foreign")
        (foreign_worker / "product/export.py").write_text("partial\n", encoding="utf-8")
        foreign = self.freeze(foreign_binding, observed_job, "Reported stop", name="foreign")
        self.assertIn("different dispatch worktree", self.reserve_resume(
            "job-a", first, foreign, effects, expected=2,
        )["error"])
        frozen = self.freeze(binding, observed_job, "Confirmed stop")
        self.assertIn("effects_readback_ref", self.reserve_resume("job-a", first, frozen, "", expected=2)["error"])
        target.write_text("unexpected changed bytes\n", encoding="utf-8")
        self.assertIn("checkpoint is stale", self.reserve_resume("job-a", first, frozen, effects,
                                                                 expected=2)["error"])
        target.write_text("partial\n", encoding="utf-8")
        (self.root / "requirements.json").write_text("Changed authoritative requirements\n", encoding="utf-8")
        obsolete = self.reserve_resume("job-a", first, frozen, effects, expected=2)
        self.assertIn("SOURCE_DRIFT: requirements.json", obsolete["error"])
        self.assertEqual(self.cli("status", "--reservation-id", "job-a")["reservation"]["phase"], "running")

    def test_aborts_only_the_exact_pending_attempt_after_confirmed_no_start(self):
        packet = self.packet("first", "T-A", "product/export.py")
        binding, worker = self.bind("first")
        self.claim("job-a", packet, binding=binding)
        self.observe("job-a", packet, "running", "First launch observed", "native/first")
        target = worker / "product/export.py"
        target.write_text("first attempt's partial edit\n", encoding="utf-8")
        first = self.freeze(binding, "native/first", "First attempt confirmed stopped", name="prior")
        effects = "Owning fixture reconciled all effects"
        no_start = "Owning host confirms that the pending continuation was never launched"
        self.assertIn("no pending continuation", self.abort_resume(
            "job-a", packet, first, no_start, expected=2,
        )["error"])
        self.reserve_resume("job-a", packet, first, effects)
        self.observe("job-a", packet, "running", "New launch observed", "native/second")
        self.assertIn("no pending continuation", self.abort_resume(
            "job-a", packet, first, no_start, expected=2,
        )["error"])
        target.write_text("second attempt's partial edit\n", encoding="utf-8")
        pending = self.freeze(binding, "native/second", "Second attempt confirmed stopped")
        self.reserve_resume("job-a", packet, pending, effects)
        self.assertIn("pending checkpoint", self.abort_resume(
            "job-a", packet, first, no_start, expected=2,
        )["error"])
        another = self.packet("other", "T-B", "product/report.py")
        self.assertIn("reservation identity", self.abort_resume(
            "job-a", another, pending, no_start, expected=2,
        )["error"])
        self.assertIn("readback_ref", self.abort_resume("job-a", packet, pending, "", expected=2)["error"])
        self.assertIn("invalid dispatch phase", self.observe(
            "job-a", packet, "released", "No response at all", expected=2,
        )["error"])
        self.assertEqual(self.cli("status", "--reservation-id", "job-a")["reservation"]["phase"], "resume-reserved")

        # Two operators independently try to record the no-start for the
        # exact pending continuation. Only one receipt can become authoritative.
        command = [sys.executable, "-B", str(SCRIPTS / "ticket_dispatch.py"), "abort-resume",
                   "--root", str(self.root), "--reservation-id", "job-a", "--handoff-sha256", packet[1],
                   "--checkpoint-sha256", self.sha(pending), "--readback-ref"]
        with subprocess.Popen([*command, no_start], stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, text=True) as left:
            with subprocess.Popen([*command, no_start + " (second observation)"], stdout=subprocess.PIPE,
                                  stderr=subprocess.PIPE, text=True) as right:
                results = []
                for contender in (left, right):
                    stdout, stderr = contender.communicate(timeout=15)
                    if contender.returncode == 0:
                        results.append(json.loads(stdout))
                    else:
                        self.assertEqual(contender.returncode, 2, stderr)
                        self.assertRegex(json.loads(stderr)["error"], "busy|no pending continuation")
        self.assertEqual([result["status"] for result in results], ["resume-aborted"])
        final_row = self.cli("status", "--reservation-id", "job-a")["reservation"]
        self.assertEqual(final_row, results[0]["reservation"])
        self.assertEqual(final_row["phase"], "resume-aborted")
        self.assertEqual(final_row["events"][-1]["checkpoint_sha256"], self.sha(pending))
        self.assertFalse(results[0]["native_receipt_authenticated"])
        self.assertEqual(self.abort_resume(
            "job-a", packet, pending, final_row["events"][-1]["readback_ref"],
        )["status"], "replayed")
        self.assertIn("aborted", self.reserve_resume("job-a", packet, pending, effects, expected=2)["error"])
        self.assertIn("invalid dispatch phase", self.observe(
            "job-a", packet, "running", "Late purported launch", "native/third", expected=2,
        )["error"])
        self.assertIn("already started this ticket revision", self.claim(
            "fresh-id", self.packet("same-ticket", "T-A", "product/export.py"), expected=2,
        )["error"])
        self.assertEqual(self.claim(
            "another-ticket", self.packet("overlap", "T-C", "product/export.py"),
        )["reservation"]["phase"], "reserved")
        self.assertEqual(target.read_text(), "second attempt's partial edit\n")

    def test_retry_requires_exact_abort_fresh_admission_and_new_attempt_fence(self):
        packet = self.packet("first", "T-A", "product/export.py")
        binding, worker = self.bind("first")
        self.claim("job-a", packet, binding=binding)
        self.observe("job-a", packet, "running", "Observed first start", "native/first")
        target = worker / "product/export.py"
        target.write_text("durable partial edit\n", encoding="utf-8")
        frozen = self.freeze(binding, "native/first", "First attempt confirmed stopped")
        effects = "Owning fixture reconciled all effects"
        self.reserve_resume("job-a", packet, frozen, effects)
        denied = "Owning host confirmed no-start of the original continuation"
        fresh = "Owning host rechecked no-start before retry"
        aborted = self.abort_resume("job-a", packet, frozen, denied)
        abort_sha = aborted["abort_sha256"]
        self.assertEqual(self.cli("status", "--reservation-id", "job-a")["abort_sha256"], abort_sha)
        self.assertIn("confirmed no-start", self.retry_resume(
            "job-a", packet, frozen, "0" * 64, "attempt-1", fresh, expected=2,
        )["error"])
        self.assertIn("fresh no-start", self.retry_resume(
            "job-a", packet, frozen, abort_sha, "attempt-1", denied, expected=2,
        )["error"])
        contender = self.packet("contender", "T-B", "product/export.py")
        self.claim("job-b", contender)
        self.assertIn("path overlaps", self.retry_resume(
            "job-a", packet, frozen, abort_sha, "attempt-1", fresh, expected=2,
        )["error"])
        self.observe("job-b", contender, "released", "Owning host confirmed no follow-on launch")
        target.write_text("drifted edit\n", encoding="utf-8")
        self.assertIn("checkpoint is stale", self.retry_resume(
            "job-a", packet, frozen, abort_sha, "attempt-1", fresh, expected=2,
        )["error"])
        target.write_text("durable partial edit\n", encoding="utf-8")
        admitted = self.retry_resume("job-a", packet, frozen, abort_sha, "attempt-1", fresh)
        self.assertEqual(admitted["status"], "resume-reserved")
        self.assertTrue(admitted["admission_rechecked"])
        self.assertEqual(admitted["reservation"]["events"][-1]["attempt_id"], "attempt-1")
        self.assertIn("confirmed no-start", self.retry_resume(
            "job-a", packet, frozen, abort_sha, "duplicate-resume", fresh, expected=2,
        )["error"])
        replay = self.retry_resume("job-a", packet, frozen, abort_sha, "attempt-1", fresh)
        self.assertEqual(replay["status"], "replayed")
        self.assertFalse(replay["admission_rechecked"])
        self.assertIn("pending attempt fence", self.observe(
            "job-a", packet, "running", "Late unfenced start observation", "native/second", expected=2,
        )["error"])
        self.assertIn("pending attempt fence", self.abort_resume(
            "job-a", packet, frozen, denied, expected=2,
        )["error"])
        fenced_abort = self.abort_resume(
            "job-a", packet, frozen, "Owning host confirmed attempt 1 also never started", attempt_id="attempt-1",
        )
        self.assertIn("different retry inputs", self.retry_resume(
            "job-a", packet, frozen, fenced_abort["abort_sha256"], "attempt-1", fresh, expected=2,
        )["error"])
        new_attempt = self.retry_resume("job-a", packet, frozen, fenced_abort["abort_sha256"], "attempt-2",
                                        "Owning host reconfirmed no-start after attempt 1")
        self.assertTrue(new_attempt["admission_rechecked"])
        self.assertIn("pending attempt fence", self.abort_resume(
            "job-a", packet, frozen, "Late attempt 1 no-start observation", attempt_id="attempt-1", expected=2,
        )["error"])
        self.observe("job-a", packet, "running", "Owning host observed the expected fresh run", "native/second",
                     attempt_id="attempt-2")
        done = self.observe("job-a", packet, "finished", "Observed completed fresh job", "native/second")
        self.assertEqual(done["reservation"]["phase"], "finished")


if __name__ == "__main__":
    unittest.main()
