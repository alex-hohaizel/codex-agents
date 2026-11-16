from contextlib import redirect_stderr, redirect_stdout
from dataclasses import replace
import hashlib
import io
import json
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import warnings
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import admit_codex_bundle as admission


def raw_json(value):
    return json.dumps(value).encode("utf-8")


class ReleaseAdmissionTest(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.stage = self.root / "stage"
        self.archive = self.root / "input.zip"
        self.manifest = raw_json({"schema_version": "atelier.skill-suite/1"})
        manifest_sha = hashlib.sha256(self.manifest).hexdigest()
        self.pin = admission.ReleasePin(
            source_sha="a" * 40,
            source_ref="refs/heads/main",
            signer_workflow=".github/workflows/validate.yml",
            archive_sha256="0" * 64,
            manifest_sha256=manifest_sha,
            repository_version="1.4.0",
            suite_version="6.2.0",
            installed_suite_version="6.1.0",
        )
        self.package = {
            "schema": "codex-agents.package/1", "mode": "CODEX",
            "suite_version": "6.2.0", "repository_version": "1.4.0",
            "manifest": "kit/manifest.json", "skill_sources": "kit/skills",
            "repository_branch": "main", "installation_performed": False,
            "release_stage": "stable",
        }
        self.release = {
            "schema_version": "codex-agents.release/1", "suite_version": "6.2.0",
            "repository_version": "1.4.0", "repository_branch": "main",
            "source_manifest_sha256": manifest_sha,
            "release_stage": "stable",
        }

    def bundle(self, extras=()):
        entries = [
            ("PACKAGE.json", raw_json(self.package), stat.S_IFREG | 0o644),
            ("releases/current.json", raw_json(self.release), stat.S_IFREG | 0o644),
            ("kit/manifest.json", self.manifest, stat.S_IFREG | 0o644),
            ("kit/portable/update_skill_suite.py", b"this must never execute", stat.S_IFREG | 0o755),
        ]
        with warnings.catch_warnings(), zipfile.ZipFile(self.archive, "w") as archive:
            warnings.simplefilter("ignore", UserWarning)
            for name, body, mode in [*entries, *extras]:
                info = zipfile.ZipInfo(name)
                info.create_system = 3
                info.external_attr = mode << 16
                archive.writestr(info, body)
        return replace(self.pin, archive_sha256=hashlib.sha256(self.archive.read_bytes()).hexdigest())

    def cli_args(self, pin, *mode):
        args = ["admit_codex_bundle.py", "--archive", str(self.archive), "--stage", str(self.stage)]
        for name, value in vars(pin).items():
            if name != "installed_suite_version":
                args.extend(("--" + name.replace("_", "-"), value))
        return [*args, *mode]

    @staticmethod
    def attestation(digest):
        data = [{
            "verificationResult": {
                "statement": {"predicateType": admission.PREDICATE,
                              "subject": [{"digest": {"sha256": digest}}]},
            },
        }]
        return subprocess.CompletedProcess([], 0, raw_json(data), b"")

    def test_valid_bundle_requests_pinned_online_provenance_then_stages(self):
        pin = self.bundle()
        with patch.object(admission.subprocess, "run", return_value=self.attestation(pin.archive_sha256)) as gh:
            # The actual updater validates the 33-skill tree elsewhere. This
            # small synthetic archive tests handoff and that embedded code is inert.
            with patch.object(admission, "trusted_read_kit") as read_kit:
                result = admission.admit(self.archive, self.stage, pin)
        argv = gh.call_args.args[0]
        self.assertIn(admission.REPOSITORY, argv)
        self.assertIn(f"{admission.REPOSITORY}/{pin.signer_workflow}", argv)
        self.assertEqual(argv[argv.index("--source-digest") + 1], pin.source_sha)
        self.assertEqual(argv[argv.index("--source-ref") + 1], pin.source_ref)
        self.assertEqual(argv[argv.index("--predicate-type") + 1], admission.PREDICATE)
        self.assertIn("--deny-self-hosted-runners", argv)
        self.assertNotIn("--bundle", argv)
        self.assertNotIn("--signer-repo", argv)
        self.assertEqual(read_kit.call_count, 1)
        self.assertEqual(result["status"], "admitted-for-updater-audit")
        self.assertEqual(result["installation_mode"], "update")
        self.assertEqual(result["installed_suite_version"], "6.1.0")
        kit = Path(result["kit"])
        self.assertTrue(kit.is_dir())
        self.assertEqual((kit / "manifest.json").read_bytes(), self.manifest)
        self.assertEqual(stat.S_IMODE((kit / "portable/update_skill_suite.py").stat().st_mode), 0o755)
        self.assertEqual(stat.S_IMODE(self.stage.stat().st_mode), 0o700)

    def test_fresh_cli_stages_with_verified_provenance_and_no_installed_version(self):
        pin = self.bundle()
        output = io.StringIO()
        with (
            patch.object(sys, "argv", self.cli_args(pin, "--fresh-install")),
            patch.object(admission.subprocess, "run", return_value=self.attestation(pin.archive_sha256)) as gh,
            patch.object(admission, "trusted_read_kit") as read_kit,
            redirect_stdout(output),
        ):
            self.assertEqual(admission.main(), 0)

        receipt = json.loads(output.getvalue())
        self.assertEqual(receipt["installation_mode"], "fresh")
        self.assertIsNone(receipt["installed_suite_version"])
        self.assertEqual(receipt["source_sha"], pin.source_sha)
        self.assertEqual(receipt["manifest_sha256"], pin.manifest_sha256)
        gh.assert_called_once()
        read_kit.assert_called_once()
        self.assertEqual((Path(receipt["kit"]) / "manifest.json").read_bytes(), self.manifest)

    def test_cli_requires_one_installation_mode_before_verification(self):
        pin = self.bundle()
        for mode in ((), ("--fresh-install", "--installed-suite-version", "6.1.0")):
            with self.subTest(mode=mode), patch.object(sys, "argv", self.cli_args(pin, *mode)):
                with patch.object(admission, "admit") as admit, redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as error:
                        admission.main()
                self.assertEqual(error.exception.code, 2)
                admit.assert_not_called()
        self.assertFalse(self.stage.exists())

    def test_archive_mismatch_and_downgrade_fail_before_network(self):
        pin = self.bundle()
        with patch.object(admission.subprocess, "run") as gh:
            with self.assertRaisesRegex(ValueError, "Archive digest"):
                admission.admit(self.archive, self.stage, replace(pin, archive_sha256="f" * 64))
            with self.assertRaisesRegex(ValueError, "older than the installed baseline"):
                admission.admit(self.archive, self.stage, replace(pin, installed_suite_version="6.3.0"))
        gh.assert_not_called()
        self.assertFalse(self.stage.exists())

    def test_no_valid_verified_subject_leaves_stage_absent(self):
        pin = self.bundle()
        for response in [
            subprocess.CompletedProcess([], 1, b"[]", b"credential error"),
            self.attestation("f" * 64),
        ]:
            with self.subTest(response=response.returncode):
                with patch.object(admission.subprocess, "run", return_value=response):
                    with self.assertRaisesRegex(ValueError, "attestation|statement"):
                        admission.admit(self.archive, self.stage, pin)
        self.assertFalse(self.stage.exists())

    def test_stale_embedded_metadata_does_not_gain_authority_from_signature(self):
        self.release["suite_version"] = "6.1.0"
        pin = self.bundle()
        with patch.object(admission.subprocess, "run", return_value=self.attestation(pin.archive_sha256)):
            with self.assertRaisesRegex(ValueError, "metadata differs"):
                admission.admit(self.archive, self.stage, pin)
        self.assertFalse(self.stage.exists())

    def test_attested_candidate_is_not_an_admitted_installation_source(self):
        self.package["release_stage"] = self.release["release_stage"] = "candidate"
        pin = self.bundle()
        with patch.object(admission.subprocess, "run", return_value=self.attestation(pin.archive_sha256)):
            with self.assertRaisesRegex(ValueError, "promoted to stable"):
                admission.admit(self.archive, self.stage, pin)
        self.assertFalse(self.stage.exists())

    def test_attested_bundle_without_explicit_stable_stage_is_rejected(self):
        del self.package["release_stage"]
        del self.release["release_stage"]
        pin = self.bundle()
        with patch.object(admission.subprocess, "run", return_value=self.attestation(pin.archive_sha256)):
            with self.assertRaisesRegex(ValueError, "promoted to stable"):
                admission.admit(self.archive, self.stage, pin)
        self.assertFalse(self.stage.exists())

    def test_unsafe_members_refused_before_extraction(self):
        regular = stat.S_IFREG | 0o644
        bad_cases = [
            [("../escaped.txt", b"bad", regular)],
            [("kit/unsafe-symlink", b"../../file", stat.S_IFLNK | 0o755)],
            [("kit/X/data", b"", regular), ("kit/x/other", b"", regular)],
            [("kit/collision", b"", regular), ("kit/collision/file", b"", regular)],
            [("kit/.env", b"", regular)],
            [("kit/manifest.json", b"", regular)],
        ]
        for entries in bad_cases:
            with self.subTest(entries=entries):
                pin = self.bundle(entries)
                with patch.object(admission.subprocess, "run", return_value=self.attestation(pin.archive_sha256)):
                    with self.assertRaisesRegex(ValueError, "Unsafe|Unsupported|collision"):
                        admission.admit(self.archive, self.stage, pin)
        self.assertFalse(self.stage.exists())
        self.assertFalse((self.root / "escaped.txt").exists())

    def test_existing_or_discoverable_stage_remains_untouched(self):
        pin = self.bundle()
        self.stage.mkdir()
        keep = self.stage / "keep"
        keep.write_bytes(b"preserve")
        discovery = self.root / ".agents/skills"
        discovery.mkdir(parents=True)
        with patch.object(admission.subprocess, "run") as gh:
            for forbidden in (self.stage, discovery / "candidate"):
                with self.subTest(stage=forbidden.name):
                    with self.assertRaisesRegex(ValueError, "fresh|discovery"):
                        admission.admit(self.archive, forbidden, pin)
        gh.assert_not_called()
        self.assertEqual(keep.read_bytes(), b"preserve")


if __name__ == "__main__":
    unittest.main()
