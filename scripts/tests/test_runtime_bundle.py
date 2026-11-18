"""Verify portable terminal database allocation using actual archive extraction."""
import importlib.util
import io
from pathlib import Path
import stat
import tarfile
import tempfile
import unicodedata
import unittest

SOURCE = Path(__file__).resolve().parents[1] / 'runtime_bundle.py'
SPEC = importlib.util.spec_from_file_location('runtime_bundle_under_test', SOURCE)
runtime = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(runtime)


class PortableTerminfo(unittest.TestCase):
    def archive(self, root, entries):
        archive = root / 'python.tar.gz'
        with tarfile.open(archive, 'w:gz') as output:
            for name, content, target in entries:
                item = tarfile.TarInfo(name)
                item.mode = 0o755 if name.startswith('python/bin/') else 0o644
                if target is not None:
                    item.type = tarfile.SYMTYPE; item.linkname = target
                    output.addfile(item)
                else:
                    item.size = len(content)
                    output.addfile(item, io.BytesIO(content))
        return archive

    def test_all_terminal_names_alias_bytes_and_casefold_prefixes_survive_real_extraction(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            entries = [
                ('python/LICENSE.txt', b'Original Python license', None),
                ('python/bin/python3.13', b'actual-byte-placeholder-not-executed', None),
                ('python/bin/python3', b'', 'python3.13'),
                ('python/lib/support.bin', b'library bytes', None),
                ('python/aliaslib', b'', 'lib'),
                ('python/share/terminfo/E/Eterm', b'uppercase-Eterm-distinct', None),
                ('python/share/terminfo/e/eterm', b'lowercase-eterm-distinct', None),
                ('python/share/terminfo/h/hp2621', b'original-hp2621', None),
                ('python/share/terminfo/2/2621A', b'', '../h/hp2621'),
                ('python/share/terminfo/2/2621a', b'', '2621A'),
                ('python/share/terminfo/A/first', b'directory-uppercase', None),
                ('python/share/terminfo/a/second', b'directory-lowercase', None),
                ('python/share/terminfo/K/first', b'K directory', None),
                ('python/share/terminfo/k/second', b'k directory', None),
                ('python/share/terminfo/\u212a/third', b'Kelvin normalized directory', None),
            ]
            archive = self.archive(root, entries)
            with tarfile.open(archive) as source:
                members = source.getmembers()
                _, _, _, mapping, planned = runtime.python_layout(members)
                self.assertEqual(runtime.python_layout(list(reversed(members)))[3:], (mapping, planned))
            output = root / 'materialized'; output.mkdir()
            directories = runtime.python_archive(archive, output)
            self.assertEqual(directories, ['python/share/terminfo', 'python/share/terminfo-extra', 'python/share/terminfo-extra2'])
            regular = {name: content for name, content, target in entries if target is None}
            for name, content, target in entries:
                if name.startswith('python/share/terminfo/'):
                    expected = b'original-hp2621' if target is not None else content
                    self.assertEqual((output / mapping[name]).read_bytes(), expected, name)
            self.assertEqual((output / 'python/bin/python3').read_bytes(), regular['python/bin/python3.13'])
            self.assertEqual((output / 'python/aliaslib/support.bin').read_bytes(), b'library bytes')
            prefixes = {}
            for path in output.rglob('*'):
                self.assertFalse(path.is_symlink())
                if path.is_file(): self.assertEqual(path.stat().st_nlink, 1)
                relative = path.relative_to(output).as_posix()
                key = unicodedata.normalize('NFC', relative).casefold()
                self.assertNotIn(key, prefixes, (prefixes.get(key), relative))
                prefixes[key] = relative
            self.assertEqual(len([path for directory in directories for path in (output / directory).rglob('*') if path.is_file()]), 10)

    def test_collisions_outside_terminal_database_are_rejected_before_any_extraction(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            archive = self.archive(root, [('python/LICENSE', b'license', None),
                ('python/lib/A/first', b'one', None), ('python/lib/a/second', b'two', None)])
            output = root / 'materialized'; output.mkdir()
            with self.assertRaisesRegex(ValueError, 'outside terminfo'):
                runtime.python_archive(archive, output)
            self.assertEqual(list(output.iterdir()), [])

    def test_missing_or_cyclic_alias_is_rejected_before_any_extraction(self):
        for links in [[('python/a', b'', 'missing')], [('python/a', b'', 'b'), ('python/b', b'', 'a')]]:
            with self.subTest(links=links), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                archive = self.archive(root, [('python/LICENSE', b'license', None), *links])
                output = root / 'materialized'; output.mkdir()
                with self.assertRaises(ValueError): runtime.python_archive(archive, output)
                self.assertEqual(list(output.iterdir()), [])


if __name__ == '__main__':
    unittest.main()
