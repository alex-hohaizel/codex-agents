"""Installer assembly guards; tiny runtime ZIPs do not claim native execution."""
import hashlib
import importlib.util
import json
from pathlib import Path
import posixpath
import re
import stat
import subprocess
import sys
import tempfile
import unittest
import warnings
import zipfile
from urllib.parse import unquote, urlsplit

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))
spec = importlib.util.spec_from_file_location('installer_assembler_under_test', SCRIPTS / 'build_installer.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

SOURCE = 'a' * 40
LOCK = 'b' * 64


class InstallerAssemblyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='installer-guards-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()

    def runtime(self, *, mutate=None, extra=None, body_override=None, duplicate=False, linked=False):
        files = {'node/bin/node': (b'native-node-fixture\n', 0o755),
                 'python/bin/python3': (b'native-python-fixture\n', 0o755),
                 'node/LICENSE': (b'fixture notice\n', 0o644)}
        if extra:
            files.update(extra)
        desc = {'schema': 'codex-agents.portable-runtime/1', 'target': 'linux-x64',
                'os': 'linux', 'arch': 'x64', 'source_commit': SOURCE, 'source_clean': True,
                'input_lock_sha256': LOCK,
                'node': {'executable': 'node/bin/node'},
                'python': {'executable': 'python/bin/python3'},
                'files': {name: {'sha256': hashlib.sha256(content).hexdigest(),
                                  'size': len(content), 'mode': mode}
                          for name, (content, mode) in files.items()}}
        if mutate:
            mutate(desc)
        destination = self.root / ('runtime-' + str(len(list(self.root.glob('runtime-*.zip')))) + '.zip')
        with zipfile.ZipFile(destination, 'w') as archive:
            for name, (content, mode) in files.items():
                info = zipfile.ZipInfo('linux-x64/' + name)
                info.create_system = 3
                info.external_attr = ((stat.S_IFLNK if linked and name == 'node/bin/node' else stat.S_IFREG) | mode) << 16
                archive.writestr(info, body_override if body_override is not None and name == 'node/bin/node' else content)
            info = zipfile.ZipInfo('linux-x64/runtime.json')
            info.create_system = 3
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            encoded = (json.dumps(desc, sort_keys=True) + '\n').encode()
            archive.writestr(info, encoded)
            if duplicate:
                with warnings.catch_warnings():
                    warnings.simplefilter('ignore', UserWarning)
                    archive.writestr(info, encoded)
        return destination, desc, files

    def test_verified_runtime_round_trip_preserves_exact_bytes_and_modes(self):
        archive, expected, files = self.runtime()
        actual = builder.runtime_input(archive, SOURCE, LOCK, False)
        self.assertEqual(actual, expected)
        stage = self.root / 'ready package'
        stage.mkdir()
        modes = {}
        builder.install_runtime(archive, actual, stage, modes)
        for name, (content, mode) in files.items():
            path = 'runtimes/linux-x64/' + name
            self.assertEqual((stage / path).read_bytes(), content)
            self.assertEqual(modes[path], mode)
        ready = self.root / 'ready.zip'
        builder.archive(stage, ready, modes)
        with zipfile.ZipFile(ready) as zipped:
            for name, (content, mode) in files.items():
                info = zipped.getinfo('ready package/runtimes/linux-x64/' + name)
                self.assertEqual(zipped.read(info), content)
                self.assertEqual(stat.S_IMODE(info.external_attr >> 16), mode)

    def test_digest_changes_are_held_before_extraction(self):
        archive, _, _ = self.runtime(body_override=b'altered runtime bytes')
        with self.assertRaises(ValueError):
            builder.runtime_input(archive, SOURCE, LOCK, False)

    def test_source_lock_and_dirty_runtime_cannot_be_rebound_to_release(self):
        archive, _, _ = self.runtime()
        for source, lock in [('c' * 40, LOCK), (SOURCE, 'd' * 64)]:
            with self.subTest(source=source, lock=lock), self.assertRaises(ValueError):
                builder.runtime_input(archive, source, lock, False)
        dirty, _, _ = self.runtime(mutate=lambda row: row.update(source_clean=False))
        with self.assertRaises(ValueError):
            builder.runtime_input(dirty, SOURCE, LOCK, False)
        self.assertFalse(builder.runtime_input(dirty, SOURCE, LOCK, True)['source_clean'])

    def test_duplicate_or_linked_runtime_members_are_rejected(self):
        for options in ({'duplicate': True}, {'linked': True}):
            archive, _, _ = self.runtime(**options)
            with self.subTest(options=options), self.assertRaises(ValueError):
                builder.runtime_input(archive, SOURCE, LOCK, False)

    def test_case_collisions_fail_on_every_building_os(self):
        archive, _, _ = self.runtime(extra={'node/bin/NODE': (b'case alias\n', 0o755)})
        with self.assertRaises(ValueError):
            builder.runtime_input(archive, SOURCE, LOCK, False)

    def test_runtime_target_and_declared_native_platform_must_agree(self):
        for patch in ({'os': 'darwin'}, {'arch': 'arm64'}, {'source_clean': 'true'}):
            archive, _, _ = self.runtime(mutate=lambda row, patch=patch: row.update(patch))
            with self.subTest(patch=patch), self.assertRaises(ValueError):
                builder.runtime_input(archive, SOURCE, LOCK, False)

    def test_executables_must_be_safe_regular_inventory_members(self):
        for executable in ('../outside', 'node/../../outside', '/outside', 'C:/outside', 'missing/node'):
            archive, _, _ = self.runtime(mutate=lambda row, executable=executable: row['node'].update(executable=executable))
            with self.subTest(executable=executable), self.assertRaises(ValueError):
                builder.runtime_input(archive, SOURCE, LOCK, False)
        archive, _, _ = self.runtime(mutate=lambda row: row['python'].update(executable='node/LICENSE'))
        with self.assertRaises(ValueError):
            builder.runtime_input(archive, SOURCE, LOCK, False)

    def test_archive_names_use_portable_windows_and_posix_rules(self):
        for name in ('../escape', '/absolute', 'C:/drive', 'a\\b', 'a//b', 'a/./b',
                     'a\x00b', 'a:stream', 'NUL.txt', 'node/CON', 'node/bad.', 'node/bad ', 'node/a?.txt'):
            with self.subTest(name=name), self.assertRaises(ValueError):
                builder.safe(name)
        self.assertEqual(builder.safe('linux-arm64/notice files/Ліцензія.txt').as_posix(),
                         'linux-arm64/notice files/Ліцензія.txt')

    def test_dirty_checkout_is_rejected_before_any_package_is_built(self):
        source = self.root / 'source'
        source.mkdir()
        subprocess.run(['git', 'init', '-q', str(source)], check=True, capture_output=True)
        (source / 'preserved.txt').write_text('original\n', encoding='utf8')
        subprocess.run(['git', 'add', 'preserved.txt'], cwd=source, check=True, capture_output=True)
        subprocess.run(['git', '-c', 'user.name=Installer Test', '-c', 'user.email=installer-test@example.invalid',
                        'commit', '-qm', 'Initial fixture'], cwd=source, check=True, capture_output=True)
        (source / 'preserved.txt').write_text('uncommitted owner work\n', encoding='utf8')
        output = self.root / 'output'
        with self.assertRaisesRegex(ValueError, 'Commit reviewed sources'):
            builder.build(source, output, [])
        self.assertFalse(output.exists())
        self.assertEqual((source / 'preserved.txt').read_text(encoding='utf8'), 'uncommitted owner work\n')


class BuyerDocumentationPackageTests(unittest.TestCase):
    def test_actual_buyer_zip_keeps_all_commercial_markdown_routes_and_canonical_manuals(self):
        source = SCRIPTS.parent
        release = json.loads((source / 'releases/current.json').read_text(encoding='utf8'))
        offer = json.loads((source / 'commercial/offer.json').read_text(encoding='utf8'))
        with tempfile.TemporaryDirectory(prefix='buyer-documentation-package-') as temporary:
            stage = Path(temporary).resolve() / 'buyer'
            manifest = builder.prepare_buyer_stage(source, stage, release, offer, SOURCE, 'solo')
            destination = stage.parent / 'buyer-documents.zip'
            builder.archive(stage, destination, {name: row['mode'] for name, row in manifest['files'].items()})
            with zipfile.ZipFile(destination) as archive:
                members = set(archive.namelist())
                guides = sorted(name for name in members
                                if name.startswith('buyer/docs/commercial/') and name.endswith('.md'))
                self.assertTrue(guides, 'Exercise the actual packaged buyer guides, not just the source entry page.')
                local_routes = []
                for name in guides:
                    text = archive.read(name).decode('utf8')
                    for href in re.findall(r'\]\(([^\s)]+)\)', text):
                        target = urlsplit(href)
                        if target.scheme or target.netloc or not target.path:
                            continue
                        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), unquote(target.path)))
                        self.assertTrue(resolved.startswith('buyer/'), 'Packaged guide link escaped: ' + name + ' -> ' + href)
                        self.assertIn(resolved, members, 'Broken packaged Markdown route: ' + name + ' -> ' + href)
                        self.assertNotIn('/product/product/', resolved, 'Do not relocate an already relocated path twice.')
                        local_routes.append((name, href, resolved))
                self.assertTrue(local_routes)
                for filename in ('BUYER_GUIDE.md', 'BUYER_GUIDE.uk.md', 'WORKBENCH_RUNTIME.md'):
                    name = 'buyer/docs/commercial/' + filename
                    expected = '../../product/docs/INSTALL.md#personal-skill-roots'
                    self.assertIn('](' + expected + ')', archive.read(name).decode('utf8'))
                install = archive.read('buyer/product/docs/INSTALL.md').decode('utf8')
                self.assertRegex(install, r'<a\s+(?:name|id)=["\']personal-skill-roots["\']')
                canonical = [source / name for name in builder.git_modes(source) if name.startswith('docs/')]
                self.assertTrue(canonical)
                for path in canonical:
                    self.assertEqual(archive.read('buyer/product/' + path.relative_to(source).as_posix()), path.read_bytes(),
                                     'Buyer navigation must not change the canonical source manual: ' + str(path))


class InstallerEntryTests(unittest.TestCase):
    def test_source_entry_links_every_native_download_and_both_languages(self):
        text = builder.render('9.8.7', 'en', False)
        expected = set(builder.LABELS.values()) | {'Universal'}
        found = set(re.findall(r'Agent-System-9\.8\.7-([^"<>]+)\.zip', text))
        self.assertEqual(found, expected)
        self.assertIn('ПОЧАТИ.html', text)
        self.assertIn('Node or npm', text)
        self.assertIn('Codex and its account remain separate', text)

    def test_offline_entry_keeps_real_visuals_and_existing_document_navigation(self):
        source = SCRIPTS.parent
        for ready in (False, True):
            for locale in ('en', 'uk'):
                with self.subTest(ready=ready, locale=locale):
                    text = builder.render('9.8.7', locale, ready)
                    images = re.findall(r'<img\b[^>]*\bsrc="([^"]+)"', text)
                    self.assertTrue(images, 'Preserve the accepted visual material on the entry page.')
                    for image in images:
                        self.assertTrue((source / image).is_file(), 'Missing entry visual: ' + image)
                    for target in re.findall(r'href="([^"]+)"', text):
                        if target.startswith(('https://', 'mailto:', '#')) or target in ('START_HERE.html', 'ПОЧАТИ.html'):
                            continue
                        original = target[len('product/'):] if target.startswith('product/') else target
                        original = {'LICENSE.txt':'commercial/legal/LICENSE.txt','THIRD_PARTY_NOTICES.txt':'commercial/legal/THIRD_PARTY_NOTICES.txt','SALES.html':'commercial/site/sales-en.html','ПРОДУКТ.html':'commercial/site/sales-uk.html'}.get(original,original)
                        self.assertTrue((source / original).is_file(), 'Broken documentation entry: ' + target)
                    if ready:
                        for launcher in ('Start.cmd', 'Start.command', 'Start.sh'):
                            self.assertIn(launcher, text)


if __name__ == '__main__':
    unittest.main()
