"""Check retained-launcher search order; native curses probes run separately."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE = Path(__file__).resolve().parents[1] / 'setup/setup.py'
SPEC = importlib.util.spec_from_file_location('terminfo_environment_under_test', SOURCE)
setup = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(setup)


class TerminfoEnvironment(unittest.TestCase):
    def test_owner_search_precedes_bundled_layers_and_final_system_fallback(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            machine = platform.machine().lower()
            cpu = 'arm64' if machine in ('arm64', 'aarch64') else 'x64'
            key = sys.platform + '-' + cpu
            prefix = 'runtimes/' + key
            references = [prefix + '/python/share/terminfo', prefix + '/python/share/terminfo-extra']
            executables = {'python_executable': prefix + '/python/bin/python3', 'node_executable': prefix + '/node/bin/node'}
            files = {}
            for name in [*executables.values(), *[value + '/x/xterm' for value in references]]:
                path = root / name; path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(b'unit-test metadata input; never executed')
                files[name] = {'sha256': hashlib.sha256(path.read_bytes()).hexdigest(), 'size': path.stat().st_size, 'mode': 0o644}
            data = {'files': files, 'portable_runtimes': {key: dict(executables, terminfo_dirs=references)}}
            (root / 'product-manifest.json').write_text(json.dumps(data), encoding='utf8')
            original = 'owner-first' + os.pathsep + 'owner-second'
            with patch.dict(os.environ, {'TERMINFO_DIRS': original}):
                result = setup.runtime_environment(root)
            expected = os.pathsep.join([original, *[str(root / value) for value in references], ''])
            self.assertEqual(result['TERMINFO_DIRS'], expected)
            self.assertTrue(result['TERMINFO_DIRS'].endswith(os.pathsep))
            data['portable_runtimes'][key]['terminfo_dirs'] = ['../unlisted-database']
            (root / 'product-manifest.json').write_text(json.dumps(data), encoding='utf8')
            with self.assertRaisesRegex(ValueError, 'database layer'):
                setup.runtime_environment(root)


if __name__ == '__main__':
    unittest.main()
