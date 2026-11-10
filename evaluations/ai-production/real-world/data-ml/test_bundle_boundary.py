"""Sanitized structure-only import-shadow controls, never model accuracy."""
from pathlib import Path
import tempfile
import unittest
from common import atomic_json, sha_file
from deliver import validate_bundle


def generic_bundle(root):
    names = ['forecast.py', 'reviews.py', 'common.py', 'consumer.py', 'source_guards.py', 'STUDY.json',
             'forecast-model.json', 'review-model.json', 'day.csv', 'signature.json', 'MODEL-CARD.json']
    for name in names:
        path = root / name
        path.write_text('{}' if path.suffix == '.json' else '')
    atomic_json(root / 'signature.json', {'forecast_weights_sha256': sha_file(root / 'forecast-model.json'),
                                         'review_weights_sha256': sha_file(root / 'review-model.json')})
    atomic_json(root / 'bundle-manifest.json', {'schema': 'atelier.actual-json-model-bundle/2',
                                              'files': [{'path': name, 'bytes': (root / name).stat().st_size,
                                                         'sha256': sha_file(root / name)} for name in names]})


class BundleBoundaries(unittest.TestCase):
    def test_unlisted_import_shadow_and_bytecode_are_rejected_before_execution(self):
        for kind in ('json.py', 'bytecode', 'symlink'):
            with tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                generic_bundle(root)
                validate_bundle(root)
                if kind == 'json.py':
                    (root / kind).write_text('raise RuntimeError("never execute")')
                elif kind == 'bytecode':
                    (root / '__pycache__').mkdir()
                    (root / '__pycache__/json.pyc').write_bytes(b'not trusted')
                else:
                    (root / 'outside.py').symlink_to(root / 'common.py')
                with self.assertRaisesRegex(ValueError, 'unlisted code'):
                    validate_bundle(root)

    def test_changed_listed_code_cannot_reuse_old_manifest(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            generic_bundle(root)
            (root / 'consumer.py').write_text('raise RuntimeError("never execute")')
            with self.assertRaisesRegex(ValueError, 'bundle bytes differ'):
                validate_bundle(root)


if __name__ == '__main__':
    unittest.main()
