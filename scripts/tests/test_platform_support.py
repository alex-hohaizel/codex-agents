"""Exercise the native platform boundary, not merely a source OS string."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SOURCE=Path(__file__).resolve().parents[1]/'platform_support.py'
spec=importlib.util.spec_from_file_location('native_platform_under_test',SOURCE)
platform=importlib.util.module_from_spec(spec);spec.loader.exec_module(platform)


class PlatformSupportTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='agent-platform-')
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name).resolve()

    def test_portable_paths_reject_windows_aliases_on_every_builder_os(self):
        for name in ('NUL','nul.txt','CON.log','CONIN$','COM1.py','LPT².txt','a:stream','C:/bad','bad.','bad ','../bad','a\\b','a//b','bad?.txt'):
            with self.subTest(name=name),self.assertRaises(ValueError):platform.safe_relative(name)
        self.assertEqual(platform.safe_relative('Проєкт/readme file.md'),'Проєкт/readme file.md')

    def test_real_process_liveness_never_terminates_the_probed_child(self):
        child=subprocess.Popen([sys.executable,'-c','import time;time.sleep(30)'])
        self.addCleanup(lambda:child.kill() if child.poll() is None else None)
        self.assertTrue(platform.process_alive(child.pid))
        self.assertIsNone(child.poll(),'A liveness query must never signal the target process')
        child.terminate();child.wait(timeout=10)
        self.assertFalse(platform.process_alive(child.pid))
        self.assertTrue(platform.process_alive(os.getpid()))

    def test_real_cross_process_lock_and_metadata_preservation(self):
        path=self.root/'writer.lock';path.write_bytes(b'preserve-lock-metadata')
        fd=os.open(path,os.O_RDWR)
        self.addCleanup(lambda:os.close(fd))
        platform.flock(fd,platform.LOCK_EX|platform.LOCK_NB)
        code='''import importlib.util,os,sys
s=importlib.util.spec_from_file_location('boundary',sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
f=os.open(sys.argv[2],os.O_RDWR)
try:
 try:m.flock(f,m.LOCK_EX|m.LOCK_NB)
 except BlockingIOError:sys.exit(23)
finally:os.close(f)
'''
        result=subprocess.run([sys.executable,'-B','-c',code,str(SOURCE),str(path)],capture_output=True,timeout=15)
        self.assertEqual(result.returncode,23,result.stderr)
        platform.flock(fd,platform.LOCK_UN)
        result=subprocess.run([sys.executable,'-B','-c',code,str(SOURCE),str(path)],capture_output=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(path.read_bytes(),b'preserve-lock-metadata')

    def test_actual_private_file_and_mode_policy(self):
        path=self.root/'приватний receipt.json';path.write_text('{"private":true}',encoding='utf8')
        platform.set_mode(path,0o600)
        self.assertTrue(platform.assert_private(path)['private'])
        self.assertTrue(platform.mode_matches(path,0o600))
        payload=self.root/'runner.py';payload.write_text('print("ok")',encoding='utf8')
        platform.set_mode(payload,0o755)
        self.assertTrue(platform.mode_matches(payload,0o755))
        if platform.WINDOWS:
            # NTFS has no executable bit. An executable source remains a valid
            # manifest member under the explicit native projection.
            self.assertEqual(platform.file_mode(payload),0o644)
        else:self.assertEqual(platform.file_mode(payload),0o755)

    def test_link_or_junction_cannot_alias_an_input(self):
        external=self.root/'external';external.mkdir();(external/'secret').write_text('private')
        link=self.root/'alias'
        if platform.WINDOWS:
            result=subprocess.run(['cmd.exe','/d','/c','mklink','/J',str(link),str(external)],capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.addCleanup(lambda:os.rmdir(link) if link.exists() else None)
        else:link.symlink_to(external,target_is_directory=True)
        self.assertTrue(platform.is_link_or_reparse(link))
        source=SOURCE.parents[1]/'standards/context_capsule.py'
        spec=importlib.util.spec_from_file_location('capsule_native_boundary',source)
        capsule=importlib.util.module_from_spec(spec);spec.loader.exec_module(capsule)
        with self.assertRaisesRegex(ValueError,'linked'):capsule.local(self.root,'alias/secret')
        with self.assertRaisesRegex(ValueError,'reparse'):platform.safe_path(link/'secret')

    @unittest.skipUnless(platform.WINDOWS,'Native Windows protected DACL case')
    def test_windows_acl_rejects_broadened_access_then_restores_private_rights(self):
        path=self.root/'private.txt';path.write_text('owned')
        platform.make_private(path);self.assertTrue(platform.private_acl_report(path)['private'])
        broaden=subprocess.run(['icacls.exe',str(path),'/grant','*S-1-5-32-545:(R)'],capture_output=True)
        self.assertEqual(broaden.returncode,0,broaden.stderr)
        with self.assertRaises(PermissionError):platform.assert_private(path)
        platform.make_private(path);self.assertTrue(platform.assert_private(path)['private'])

    def test_descriptor_permission_change_keeps_exact_utf8_bytes(self):
        path=self.root/'utf8.json';fd=os.open(path,os.O_CREAT|os.O_RDWR|os.O_EXCL,0o600)
        try:
            platform.fchmod(fd,0o600)
            payload='{"name":"Покупець"}\n'.encode('utf8');os.write(fd,payload);os.fsync(fd)
        finally:os.close(fd)
        self.assertEqual(path.read_bytes(),payload)
        self.assertTrue(platform.assert_private(path)['private'])


    def test_scanned_hash_uses_exact_fresh_bytes_and_rejects_a_changed_revision(self):
        path=self.root/'fresh source.txt';path.write_bytes('Свіжий source\n'.encode('utf8'))
        observed=path.lstat()
        result=platform.hash_scanned(path,observed,1024)
        import hashlib
        self.assertEqual(result,{'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'size':path.stat().st_size})
        path.write_bytes(b'Different source revision')
        with self.assertRaises(ValueError):platform.hash_scanned(path,observed,1024)

    @unittest.skipUnless(hasattr(os,'mkfifo'),'POSIX nonblocking replacement guard')
    def test_scanned_regular_file_replaced_by_fifo_cannot_block_the_reader(self):
        path=self.root/'replace-me';path.write_bytes(b'Original')
        code="""import importlib.util,os,pathlib,sys
s=importlib.util.spec_from_file_location('guarded_boundary',sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
p=pathlib.Path(sys.argv[2]);observed=p.lstat();p.unlink();os.mkfifo(p)
try:m.hash_scanned(p,observed,1024)
except ValueError:sys.exit(0)
sys.exit(5)
"""
        result=subprocess.run([sys.executable,'-B','-c',code,str(SOURCE),str(path)],capture_output=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)


    @unittest.skipIf(platform.WINDOWS,'POSIX npm symlink command contract')
    def test_official_posix_npm_entry_uses_bundled_node_without_replacing_project_path(self):
        package=self.root/'node_modules/@openai/codex'
        script=package/'bin/codex.js';script.parent.mkdir(parents=True)
        script.write_text('#!/usr/bin/env node\n',encoding='utf8')
        (package/'package.json').write_text(json.dumps({'name':'@openai/codex','bin':{'codex':'bin/codex.js'}}),encoding='utf8')
        entry=self.root/'tools/codex';entry.parent.mkdir();entry.symlink_to(script)
        node=self.root/'bundled node';node.write_bytes(b'toolkit interpreter')
        with patch.dict(os.environ,{'AGENT_SYSTEM_NODE':str(node),'PATH':'project-interpreter-directory'}):
            self.assertEqual(platform.codex_command(str(entry)),[str(node),str(script)])
            self.assertEqual(os.environ['PATH'],'project-interpreter-directory')
            self.assertEqual(platform.codex_command(sys.executable),[sys.executable])
        (package/'package.json').write_text(json.dumps({'name':'different-package','bin':{'codex':'bin/codex.js'}}),encoding='utf8')
        with patch.dict(os.environ,{'AGENT_SYSTEM_NODE':str(node)}):
            self.assertEqual(platform.codex_command(str(entry)),[str(entry)])


if __name__=='__main__':unittest.main()
