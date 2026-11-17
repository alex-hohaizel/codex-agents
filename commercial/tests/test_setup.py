import importlib.util
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

sys.dont_write_bytecode = True
REPO = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('buyer_setup', REPO/'commercial/setup/setup.py')
setup = importlib.util.module_from_spec(spec)
spec.loader.exec_module(setup)


def package_fixture(root):
    product=root/'product'
    product.mkdir(parents=True)
    for directory in ('kit','host-profiles','agent-profiles','optional-skills'):
        shutil.copytree(REPO/directory, product/directory)
    (product/'scripts').mkdir()
    shutil.copy2(REPO/'scripts/install_host_profile.py',product/'scripts/install_host_profile.py')
    (root/'LICENSE.txt').write_text('Test purchase terms, preserved as exact local fixture.\n')
    files={}
    for file in sorted(root.rglob('*')):
        if file.is_file():
            files[file.relative_to(root).as_posix()]={'sha256':setup.digest(file.read_bytes()),'size':file.stat().st_size,'mode':stat.S_IMODE(file.stat().st_mode)}
    metadata={'schema':setup.MANIFEST,'product_id':'codex-agent-system','product_version':'1.8.0-rc.1',
              'source_commit':'6eda958692eda18d0c3727e6452a970b5058532e','edition':'solo','components':{},'files':files}
    (root/'product-manifest.json').write_bytes(setup.encoded(metadata))
    return root


class BuyerSetupTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.session=tempfile.TemporaryDirectory(prefix='buyer-setup-fixture-')
        cls.package=package_fixture(Path(cls.session.name).resolve()/'offline package')

    @classmethod
    def tearDownClass(cls):
        cls.session.cleanup()

    def setUp(self):
        self.test=tempfile.TemporaryDirectory(prefix='buyer-lifecycle-')
        self.addCleanup(self.test.cleanup)
        self.root=Path(self.test.name).resolve()
        self.home=self.root/'Покупець Test Home'
        self.home.mkdir()
        self.state=self.home/'.local/share/codex-agent-system'
        self.plan=self.root/'saved plan.json'

    def audited(self, entitlement=None):
        result=setup.audit(self.package,self.home,self.state,self.plan,entitlement)
        self.assertEqual(result['status'],'ready',result)
        return result

    def installed(self, entitlement=None):
        plan=self.audited(entitlement)
        result=setup.install(self.plan,plan['plan_sha256'])
        self.assertEqual(result['status'],'installed')
        return plan,result

    def test_clean_install_repeat_verify_and_rollback_preserve_unrelated(self):
        other=self.home/'.agents/skills/custom-notes'
        other.mkdir(parents=True)
        (other/'notes.txt').write_text('Private local work')
        project=self.home/'My Project'
        project.mkdir();(project/'accepted.md').write_text('Customer project stays intact')
        plan,result=self.installed()
        v=setup.verify(Path(result['journal']))
        self.assertEqual(v['skills'],33)
        self.assertTrue(v['orchestrator'])
        self.assertFalse(v['host_discovery_verified'])
        self.assertTrue(Path(result['launcher']).is_file())
        same=setup.install(self.plan,plan['plan_sha256'])
        self.assertEqual(same['journal'],result['journal'])
        restored=setup.rollback(Path(result['journal']))
        self.assertEqual(restored['status'],'rolled-back')
        self.assertFalse((self.home/'.agents/skills/agent-foundry').exists())
        self.assertFalse((self.home/'.agents/skills/atelier-orchestrator').exists())
        self.assertEqual((other/'notes.txt').read_text(),'Private local work')
        self.assertEqual((project/'accepted.md').read_text(),'Customer project stays intact')

    def test_existing_public_install_and_tuning_are_preserved(self):
        skills=self.home/'.agents/skills'
        shutil.copytree(self.package/'product/kit/skills',skills)
        shutil.copytree(self.package/'product/optional-skills/atelier-orchestrator',skills/'atelier-orchestrator')
        profile=self.home/'.codex'
        profile.mkdir()
        (profile/'AGENTS.md').write_text('# Personal instructions\nPreserve my projects.\n')
        role=(self.package/'product/agent-profiles/foundry-qa.toml').read_text()
        (profile/'agents').mkdir()
        (profile/'agents/foundry-qa.toml').write_text('model = "local-choice"\n'+role)
        plan,result=self.installed()
        self.assertEqual(plan['mode'],'known-current')
        self.assertEqual((profile/'agents/foundry-qa.toml').read_text(),'model = "local-choice"\n'+role)
        self.assertIn('Preserve my projects.',(profile/'AGENTS.md').read_text())
        report=setup.uninstall(Path(result['journal']))
        self.assertEqual(report['status'],'uninstalled')
        self.assertIn('Preserve my projects.',(profile/'AGENTS.md').read_text())
        self.assertNotIn('agent-system-quality:start',(profile/'AGENTS.md').read_text())

    def test_user_change_blocks_uninstall_before_any_deletion(self):
        _,result=self.installed()
        file=self.home/'.agents/skills/app-atelier-build/SKILL.md'
        file.write_text(file.read_text()+'\nLocal refinement\n')
        with self.assertRaises(Exception):
            setup.uninstall(Path(result['journal']))
        self.assertTrue((self.home/'.agents/skills/agent-foundry/SKILL.md').is_file())
        self.assertIn('Local refinement',file.read_text())

    def test_stale_plan_and_foreign_name_block_before_install(self):
        plan=self.audited()
        target=self.home/'.agents/skills/agent-foundry'
        target.mkdir(parents=True)
        (target/'SKILL.md').write_text('---\nname: unrelated\n---\nMy different work\n')
        with self.assertRaisesRegex(ValueError,'changed after audit'):
            setup.install(self.plan,plan['plan_sha256'])
        self.assertEqual((target/'SKILL.md').read_text(),'---\nname: unrelated\n---\nMy different work\n')
        self.assertFalse((self.home/'.codex/AGENTS.md').exists())

    def test_approval_is_exact_and_entitlement_survives_uninstall(self):
        entitlement=self.root/'purchase.json'
        entitlement.write_text('{"order":"test-only-1","edition":"solo","major":1}\n')
        plan=self.audited(entitlement)
        with self.assertRaisesRegex(ValueError,'Approval'):
            setup.install(self.plan,'0'*64)
        result=setup.install(self.plan,plan['plan_sha256'])
        receipt=setup.load(Path(result['journal']))
        retained=Path(receipt['retained_entitlement'])
        entitlement.unlink()
        setup.uninstall(Path(result['journal']))
        self.assertEqual(json.loads(retained.read_text())['order'],'test-only-1')
        self.assertTrue((self.state/'operations').is_dir())

    def test_composite_lock_excludes_second_writer(self):
        plan=self.audited()
        with setup.locked(self.state,self.home):
            with self.assertRaisesRegex(ValueError,'Another buyer setup'):
                setup.install(self.plan,plan['plan_sha256'])
        self.assertFalse((self.home/'.agents/skills/agent-foundry').exists())

    def test_native_failure_after_core_resumes_exact_saved_journal(self):
        plan=self.audited()
        real=setup.apply_optional
        def interrupted(*args):
            raise InterruptedError('Controlled stop before optional component')
        with patch.object(setup,'apply_optional',interrupted):
            with self.assertRaises(InterruptedError):
                setup.install(self.plan,plan['plan_sha256'])
        journal=Path(plan['journal'])
        prior=setup.load(journal)
        self.assertTrue(prior['core_complete'])
        self.assertTrue(prior['profile_complete'])
        self.assertEqual(prior['status'],'interrupted')
        with self.assertRaisesRegex(ValueError,'operation started'):
            setup.install(self.plan,plan['plan_sha256'])
        done=setup.install(self.plan,plan['plan_sha256'],resume=journal)
        self.assertEqual(done['status'],'installed')
        self.assertEqual(len(list((self.home/'.agents/skills').iterdir())),34)
        self.assertEqual(len(list((Path(prior['operation'])/'core-backups').glob('run-*'))),1)

    def test_doctor_missing_dependency_is_actionable(self):
        with patch.object(setup.shutil,'which',return_value=None):
            result=setup.doctor(self.package,self.home,self.state)
        self.assertEqual(result['status'],'action-required')
        self.assertIn('Install Codex',result['host']['next'])
        self.assertTrue(result['components']['orchestrator']['included'])

    def test_changed_package_and_unsafe_state_are_rejected(self):
        target=self.root/'corrupt'
        target.mkdir()
        shutil.copy2(self.package/'product-manifest.json',target/'product-manifest.json')
        (target/'extra.txt').write_text('Unexpected member')
        with self.assertRaisesRegex(ValueError,'unexpected files'):
            setup.package_info(target)
        with self.assertRaisesRegex(ValueError,'outside skill discovery'):
            setup.paths(self.home,self.home/'.agents/skills/runtime-state')

    def test_locale_first_task_equivalence(self):
        en,uk=setup.first_task('en'),setup.first_task('uk')
        self.assertEqual(en['fixture'],uk['fixture'])
        self.assertEqual(en['expected'],uk['expected'])
        self.assertIn('$atelier-orchestrator',uk['prompt'])
        self.assertFalse(uk['execution_performed'])

    def test_moved_downloads_copy_does_not_break_install_recovery(self):
        _,result=self.installed()
        moved=self.package.with_name('temporarily moved downloaded package')
        self.package.rename(moved)
        try:
            self.assertEqual(setup.verify(Path(result['journal']))['skills'],33)
            self.assertEqual(setup.rollback(Path(result['journal']))['status'],'rolled-back')
        finally:
            moved.rename(self.package)

    def test_local_visual_and_model_selections_are_retained(self):
        skills=self.home/'.agents/skills'
        shutil.copytree(self.package/'product/kit/skills',skills)
        icon=skills/'app-atelier-build/assets/family-icon-small.png'
        original=icon.read_bytes()
        # A different valid supplied icon is a local visual identity, not executable policy.
        other=skills/'gamedev-build/assets/family-icon-small.png'
        icon.write_bytes(other.read_bytes())
        self.assertNotEqual(icon.read_bytes(),original)
        preserved=icon.read_bytes()
        _,result=self.installed()
        self.assertEqual(icon.read_bytes(),preserved)
        self.assertTrue(setup.verify(Path(result['journal']))['icons_preserved'])

    def test_guided_first_task_and_cancel_do_not_mutate(self):
        with patch.object(setup.sys.stdin,'isatty',return_value=True),patch('builtins.input',return_value='7'):
            result=setup.wizard(self.package,self.home,self.state,locale='uk')
        self.assertEqual(result['status'],'ready-to-run')
        self.assertFalse(self.state.exists())


if __name__=='__main__':
    unittest.main()
