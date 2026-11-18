import importlib.util
import base64
import hashlib
import json
import os
from pathlib import Path
import shutil
import stat
import io
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
    # This synthetic buyer fixture exercises the current controller bytes. The
    # release's canonical manifest regeneration is a separate production gate.
    manifest=json.loads((product/'kit/manifest.json').read_text(encoding='utf8'))
    for row in manifest['skills']:
        folder=product/'kit/skills'/row['name']
        old=row['files'];files={}
        for item in sorted(folder.rglob('*')):
            if item.is_file() and '__pycache__' not in item.parts and item.suffix!='.pyc':
                rel=item.relative_to(folder).as_posix();raw=item.read_bytes()
                files[rel]={'sha256':hashlib.sha256(raw).hexdigest(),'size':len(raw),
                            'mode':old.get(rel,{}).get('mode',0o644)}
        row['files']=files
    (product/'kit/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n',encoding='utf8')
    (product/'scripts').mkdir()
    shutil.copy2(REPO/'scripts/install_host_profile.py',product/'scripts/install_host_profile.py')
    shutil.copy2(REPO/'scripts/platform_support.py',product/'scripts/platform_support.py')
    (root/'LICENSE.txt').write_text('Test purchase terms, preserved as exact local fixture.\n')
    files={}
    for file in sorted(root.rglob('*')):
        if file.is_file():
            files[file.relative_to(root).as_posix()]={'sha256':setup.digest(file.read_bytes()),'size':file.stat().st_size,'mode':setup.platform_support.file_mode(file)}
    metadata={'schema':setup.MANIFEST,'product_id':'codex-agent-system','product_version':'1.8.0-rc.1',
              'source_commit':'6eda958692eda18d0c3727e6452a970b5058532e','edition':'solo','components':{},'files':files}
    (root/'product-manifest.json').write_bytes(setup.encoded(metadata))
    return root


class DiscoveryObservationTests(unittest.TestCase):
    def test_saved_roots_reject_any_location_outside_the_two_exact_personal_roots(self):
        home=Path('/selected/buyer')
        plan={'core_plan':'unused','optional':{'target':str(home/'.codex/skills/atelier-orchestrator')}}
        with patch.object(setup,'load',return_value={'destination':str(home/'other/skills'),
                                                   'legacy_root':str(home/'.agents/skills')}):
            with self.assertRaisesRegex(ValueError,'two allowed personal'):
                setup.saved_skill_roots(plan,home)

    def test_cardinality_diagnostics_distinguish_missing_duplicates_and_known_parse_errors(self):
        expected={'managed-a','managed-b','managed-c'}
        path='/isolated/buyer/.agents/skills/managed-b/SKILL.md'
        records={'data':[{'skills':[{'name':'managed-a','path':'/first/managed-a/SKILL.md','enabled':True},
            {'name':'managed-a','path':'/second/managed-a/SKILL.md','enabled':True},
            {'name':'private-custom','path':'PRIVATE-UNKNOWN-PATH','description':'PRIVATE-CONTENT'}],
            'errors':[{'path':path,'message':'Invalid frontmatter: '+path},
                      {'path':'/private/custom/SKILL.md','message':'PRIVATE-ERROR-CONTENT'}]}]}
        rows,summary,private=setup.discovery_observation(records,expected)
        self.assertEqual(len(rows),2)
        self.assertEqual(summary['expected_count'],3)
        self.assertEqual(summary['unique_count'],1)
        self.assertEqual(summary['missing'],['managed-b','managed-c'])
        self.assertEqual(summary['duplicates'],{'managed-a':2})
        self.assertEqual(summary['loader_error_count'],2)
        self.assertEqual(summary['known_loader_errors'],[{'skill':'managed-b','code':'skill-load-error',
            'message':'Invalid frontmatter: managed-b/SKILL.md'}])
        self.assertNotIn('PRIVATE-',json.dumps(private))
        self.assertNotIn('/isolated/buyer',json.dumps(summary))
        self.assertEqual(private['declared_rows'][0]['path'],'/first/managed-a/SKILL.md')

    def test_zero_native_skills_is_reported_without_adopting_unrelated_sources(self):
        rows,summary,private=setup.discovery_observation({'data':[{'skills':[],'errors':[]}]},{'managed'})
        self.assertEqual(rows,[])
        self.assertEqual(summary['observed_count'],0)
        self.assertEqual(summary['missing'],['managed'])
        self.assertEqual(private['declared_rows'],[])


class OptionalLegacyRecoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='optional-legacy-recovery-');self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve()
        self.legacy=self.root/'home/.agents/skills/atelier-orchestrator';self.legacy.mkdir(parents=True)
        (self.legacy/'SKILL.md').write_bytes(b'Known managed skill.\n')
        (self.legacy/'resource.txt').write_bytes(b'Known managed resource.\n')
        self.operation=self.root/'state/operations'/('a'*32);self.operation.mkdir(parents=True)
        self.before=setup.tree(self.legacy)
        self.plan={'optional':{'legacy_retirement':{'target':str(self.legacy),'before':self.before}}}
        self.journal={}
        self.discard=self.legacy.parent.parent/('.buyer-orchestrator-legacy-old-'+self.operation.name)

    def interrupted_cleanup(self):
        real=setup.shutil.rmtree;fired=[False]
        def partial(path,*args,**kwargs):
            if Path(path)==self.discard and not fired[0]:
                fired[0]=True;(self.discard/'SKILL.md').unlink()
                raise InterruptedError('Actual cleanup interruption after one unlink')
            return real(path,*args,**kwargs)
        with patch.object(setup.shutil,'rmtree',side_effect=partial):
            with self.assertRaises(InterruptedError):setup.retire_optional_legacy(self.plan,self.operation,self.journal)
        self.journal=setup.load(self.operation/'journal.json')
        self.assertEqual(self.journal['optional_legacy_phase'],'cleaning')
        self.assertEqual(setup.tree(self.operation/'orchestrator-legacy-before'),self.before)

    def test_owned_partial_cleanup_resumes_with_full_original_recovery_backup(self):
        self.interrupted_cleanup()
        setup.retire_optional_legacy(self.plan,self.operation,self.journal)
        self.assertEqual(self.journal['optional_legacy_phase'],'complete')
        self.assertFalse(self.discard.exists())
        setup.restore_optional_legacy(self.plan,self.operation,self.journal)
        self.assertEqual(setup.tree(self.legacy),self.before)

    def test_unknown_extra_file_is_preserved_and_blocks_cleanup_resume(self):
        self.interrupted_cleanup();extra=self.discard/'new-owner-work.txt';extra.write_bytes(b'New owner work')
        with self.assertRaisesRegex(ValueError,'altered or extra'):
            setup.retire_optional_legacy(self.plan,self.operation,self.journal)
        self.assertEqual(extra.read_bytes(),b'New owner work')

    def test_altered_remaining_file_is_preserved_and_blocks_cleanup_resume(self):
        self.interrupted_cleanup();changed=self.discard/'resource.txt';changed.write_bytes(b'Changed accepted content')
        with self.assertRaisesRegex(ValueError,'altered or extra'):
            setup.retire_optional_legacy(self.plan,self.operation,self.journal)
        self.assertEqual(changed.read_bytes(),b'Changed accepted content')

    def test_unknown_empty_directory_also_blocks_cleanup_resume(self):
        self.interrupted_cleanup();extra=self.discard/'new-owner-folder';extra.mkdir()
        with self.assertRaisesRegex(ValueError,'extra directories'):
            setup.retire_optional_legacy(self.plan,self.operation,self.journal)
        self.assertTrue(extra.is_dir())

    @unittest.skipIf(os.name=='nt','POSIX link injection; native Windows junction boundary covered separately')
    def test_link_in_partial_discard_is_not_followed_or_removed(self):
        self.interrupted_cleanup();outside=self.root/'outside';outside.write_bytes(b'Preserve outside bytes')
        (self.discard/'untrusted-link').symlink_to(outside)
        with self.assertRaises(ValueError):setup.retire_optional_legacy(self.plan,self.operation,self.journal)
        self.assertEqual(outside.read_bytes(),b'Preserve outside bytes')
        self.assertTrue((self.discard/'untrusted-link').is_symlink())


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

    def test_windows_root_migration_resumes_orchestrator_retirement_and_restores_old_journal_rights_and_icons(self):
        oldroot=self.home/'.agents/skills'
        shutil.copytree(self.package/'product/kit/skills',oldroot)
        icon=oldroot/'agent-foundry/assets/owner-root-icon.svg'
        icon.write_bytes(b'<svg>Accepted owner icon across root migration</svg>')
        ui=oldroot/'agent-foundry/agents/openai.yaml'
        raw=ui.read_text(encoding='utf8')
        raw=raw.replace('./assets/family-icon-small.png','./assets/owner-root-icon.svg').replace('./assets/family-icon-large.png','./assets/owner-root-icon.svg')
        ui.write_text(raw,encoding='utf8')
        foreign=oldroot/'owner-notes/notes.txt';foreign.parent.mkdir();foreign.write_bytes(b'Preserve owner notes.\n')
        entitlement=self.root/'original-acquired-rights.json';entitlement.write_bytes(b'{"mode":"test-not-a-purchase","edition":"solo","major":1}\n')
        _,prior=self.installed(entitlement)
        old_journal=Path(prior['journal']);old_profile=(self.home/'.codex/AGENTS.md').read_bytes()
        old_icon=icon.read_bytes();receipt=Path(prior['verification']['license_record_retained'])
        expected_receipt=receipt.read_bytes()
        original_selector=setup.platform_support.personal_skill_roots
        roots=lambda home:original_selector(home,windows=True)
        with patch.object(setup.platform_support,'personal_skill_roots',side_effect=roots):
            self.assertEqual(setup.verify(old_journal)['skills'],33)
            migration=self.root/'native-root-migration-plan.json'
            audit=setup.audit(self.package,self.home,self.state,migration)
            self.assertEqual(audit['status'],'ready',audit)
            saved=setup.load(migration)
            self.assertEqual(saved['optional']['legacy_retirement']['target'],str(oldroot/'atelier-orchestrator'))
            self.assertTrue(any(row['action']=='retire' for row in audit['preview']['components']))
            real_replace=setup.os.replace
            interrupted=[False]
            def stop_after_legacy_rename(source,destination):
                result=real_replace(source,destination)
                if Path(source)==oldroot/'atelier-orchestrator' and not interrupted[0]:
                    interrupted[0]=True
                    raise InterruptedError('Actual stop after optional legacy rename')
                return result
            with patch.object(setup.os,'replace',side_effect=stop_after_legacy_rename):
                with self.assertRaises(InterruptedError):setup.install(migration,audit['plan_sha256'])
            journal=Path(audit['journal'])
            self.assertEqual(setup.load(journal)['optional_legacy_phase'],'prepared')
            result=setup.install(migration,audit['plan_sha256'],resume=journal)
            current=self.home/'.codex/skills'
            self.assertEqual((current/'agent-foundry/assets/owner-root-icon.svg').read_bytes(),old_icon)
            self.assertFalse((oldroot/'agent-foundry').exists())
            self.assertFalse((oldroot/'atelier-orchestrator').exists())
            self.assertEqual(result['verification']['license_record_retained'],str(receipt))
            self.assertEqual(receipt.read_bytes(),expected_receipt)
            self.assertEqual(setup.verify(journal)['skills'],33)
            self.assertEqual(setup.rollback(journal)['status'],'rolled-back')
            self.assertFalse((current/'agent-foundry').exists())
            self.assertFalse((current/'atelier-orchestrator').exists())
            self.assertEqual(icon.read_bytes(),old_icon)
            self.assertTrue((oldroot/'atelier-orchestrator/SKILL.md').is_file())
            self.assertEqual((self.home/'.codex/AGENTS.md').read_bytes(),old_profile)
            self.assertEqual(foreign.read_bytes(),b'Preserve owner notes.\n')
            self.assertEqual(receipt.read_bytes(),expected_receipt)
            self.assertEqual(setup.verify(old_journal)['skills'],33)

    def test_windows_root_migration_blocks_unknown_legacy_orchestrator_before_install(self):
        _,prior=self.installed()
        legacy=self.home/'.agents/skills/atelier-orchestrator/SKILL.md'
        legacy.write_bytes(legacy.read_bytes()+b'Accepted owner policy changes.\n')
        preserved=legacy.read_bytes();selector=setup.platform_support.personal_skill_roots
        with patch.object(setup.platform_support,'personal_skill_roots',side_effect=lambda home:selector(home,windows=True)):
            result=setup.audit(self.package,self.home,self.state,self.root/'blocked-migration.json')
            self.assertEqual(result['status'],'blocked')
            self.assertTrue(any('Legacy Orchestrator has unknown' in row for row in result['blockers']))
        self.assertEqual(legacy.read_bytes(),preserved)
        self.assertFalse((self.home/'.codex/skills/agent-foundry').exists())

    def test_operations_lists_real_interrupted_first_install_and_its_approved_plan(self):
        plan=self.audited()
        self.assertEqual(setup.operations(self.home,self.state)['operations'],[])
        # Terminate the actual child without finally blocks: OS locks must close
        # and the next process must recover the persisted composite journal.
        driver='''import importlib.util,os,sys
from pathlib import Path
s=importlib.util.spec_from_file_location('interrupted_setup',sys.argv[1]);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def stop(*args,**kwargs):os._exit(73)
m.apply_optional=stop
m.install(Path(sys.argv[2]),sys.argv[3])
'''
        child=subprocess.run([sys.executable,'-B','-c',driver,str(REPO/'commercial/setup/setup.py'),str(self.plan),plan['plan_sha256']],capture_output=True,timeout=240)
        self.assertEqual(child.returncode,73,child.stderr.decode('utf8',errors='replace'))
        rows=setup.operations(self.home,self.state)['operations']
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]['plan_sha256'],plan['plan_sha256'])
        self.assertEqual(rows[0]['journal'],plan['journal'])
        self.assertTrue(rows[0]['can_resume'])
        setup.install(self.plan,plan['plan_sha256'],resume=Path(plan['journal']))
        self.assertFalse(setup.operations(self.home,self.state)['operations'][0]['can_resume'])

    def test_prepared_first_task_is_new_owned_utf8_fixture_and_does_not_claim_execution(self):
        a=setup.prepare_first_task(self.package,self.home,self.state,'uk')
        b=setup.prepare_first_task(self.package,self.home,self.state,'en')
        self.assertNotEqual(a['project'],b['project'])
        self.assertFalse(a['execution_performed'])
        self.assertTrue(Path(a['project']).is_relative_to(self.state/'practice'))
        self.assertEqual((Path(a['project'])/'README.md').read_text(encoding='utf8'),'# Cheklist\n')
        self.assertIn('$atelier-orchestrator',(Path(a['project'])/'TASK.txt').read_text(encoding='utf8'))
        self.assertFalse((self.home/'.agents/skills/agent-foundry').exists())

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
        practice=setup.prepare_first_task(self.package,self.home,self.state,'uk')
        self.assertEqual(Path(practice['launcher']).parent,Path(practice['project']))
        self.assertTrue(Path(practice['launcher']).is_file())
        self.assertFalse(practice['execution_performed'])
        same=setup.install(self.plan,plan['plan_sha256'])
        self.assertEqual(same['journal'],result['journal'])
        restored=setup.rollback(Path(result['journal']))
        self.assertEqual(restored['status'],'rolled-back')
        self.assertFalse((self.home/'.agents/skills/agent-foundry').exists())
        self.assertFalse((self.home/'.agents/skills/atelier-orchestrator').exists())
        self.assertEqual((other/'notes.txt').read_text(),'Private local work')
        self.assertEqual((project/'accepted.md').read_text(),'Customer project stays intact')

    def test_existing_receipt_survives_neutral_reinstall_without_a_new_entitlement(self):
        entitlement=self.root/'trusted receipt.json'
        raw=b'{"mode":"test-not-a-purchase","acquired_major":1,"edition":"solo"}\n'
        entitlement.write_bytes(raw)
        _,first=self.installed(entitlement)
        original=Path(first['verification']['license_record_retained'])
        self.assertEqual(original.read_bytes(),raw)
        self.assertTrue(setup.platform_support.assert_private(original)['private'])
        neutral=self.root/'neutral technical package'
        shutil.copytree(self.package,neutral)
        metadata=setup.load(neutral/'product-manifest.json');metadata['edition']='unassigned'
        (neutral/'product-manifest.json').write_bytes(setup.encoded(metadata))
        next_plan=self.root/'neutral reinstallation plan.json'
        audited=setup.audit(neutral,self.home,self.state,next_plan)
        self.assertEqual(audited['status'],'ready')
        saved=setup.load(next_plan)
        self.assertEqual(saved['entitlement']['sha256'],setup.digest(raw))
        installed=setup.install(next_plan,audited['plan_sha256'])
        self.assertEqual(installed['verification']['license_record_retained'],str(original))
        self.assertEqual(setup.verify(Path(installed['journal']))['license_record_retained'],str(original))
        self.assertEqual(original.read_bytes(),raw)
        original.write_bytes(raw+b'Unknown owner change.\n')
        with self.assertRaisesRegex(ValueError,'purchase record changed'):
            setup.audit(neutral,self.home,self.state,self.root/'blocked rights plan.json')
        replacement=self.root/'explicit replacement receipt.json'
        replacement.write_bytes(b'{"mode":"new explicit test receipt","acquired_major":1}\n')
        explicit=setup.audit(neutral,self.home,self.state,self.root/'explicit rights plan.json',replacement)
        self.assertEqual(explicit['status'],'ready')
        explicit_plan=setup.load(Path(explicit['plan']))
        self.assertEqual(explicit_plan['entitlement']['sha256'],setup.digest(replacement.read_bytes()))
        self.assertEqual(original.read_bytes(),raw+b'Unknown owner change.\n')

    def rolled_back_distinct_launcher(self):
        """Recognized predecessor uses another retained package/launcher path.

        This controller fixture reproduces the exact launcher transition found
        with the immutable8b buyer package; native old8b acceptance stays separate.
        """
        prior_package=self.root/'recognized prior package'
        shutil.copytree(self.package,prior_package)
        metadata=setup.load(prior_package/'product-manifest.json')
        metadata['source_commit']='8b78dd38690e44a08099a76255c89cbf06f2bf08'
        (prior_package/'product-manifest.json').write_bytes(setup.encoded(metadata))
        rights=self.root/'original prior rights.json'
        rights.write_bytes(b'{"mode":"test-not-a-purchase","edition":"solo","major":1}\n')
        first=self.root/'prior install plan.json'
        audited=setup.audit(prior_package,self.home,self.state,first,rights)
        prior=setup.install(first,audited['plan_sha256'])
        launcher=Path(prior['launcher']);before=launcher.read_bytes()
        foreign=self.home/'customer-project.txt';foreign.write_bytes(b'Preserve this customer project.\n')
        role=self.home/'.codex/agents/foundry-qa.toml'
        role.write_text('model = "customer-model"\n'+role.read_text(encoding='utf8'),encoding='utf8')
        tuned=role.read_bytes()
        current=self.root/'current upgrade plan.json'
        audited=setup.audit(self.package,self.home,self.state,current)
        self.assertEqual(audited['status'],'ready',audited)
        # A ready native package adds an explicit bundled runtime environment;
        # the source-only fixture has no vendor runtimes. Use this existing
        # environment seam to produce the same meaningful launcher transition
        # without inventing a native binary or executing a fixture runtime.
        with patch.object(setup,'runtime_environment',return_value={'AGENT_SYSTEM_PYTHON':sys.executable}):
            upgraded=setup.install(current,audited['plan_sha256'])
        self.assertNotEqual(launcher.read_bytes(),before)
        journal=Path(upgraded['journal'])
        self.assertEqual(setup.rollback(journal)['status'],'rolled-back')
        self.assertEqual(launcher.read_bytes(),before)
        self.assertEqual(role.read_bytes(),tuned)
        self.assertEqual(foreign.read_bytes(),b'Preserve this customer project.\n')
        return launcher,journal,setup.load(current),Path(prior['verification']['license_record_retained'])

    def test_upgrade_rollback_allows_current_reaudit_and_reinstall_with_original_rights(self):
        launcher,journal,prior,rights=self.rolled_back_distinct_launcher()
        original_rights=rights.read_bytes()
        plan=self.root/'after rollback plan.json'
        audited=setup.audit(self.package,self.home,self.state,plan)
        self.assertEqual(audited['status'],'ready',audited)
        self.assertEqual(setup.load(plan)['launcher_before_sha256'],setup.digest(launcher.read_bytes()))
        self.assertEqual(setup.load(plan)['entitlement']['sha256'],setup.digest(original_rights))
        self.assertEqual(setup.load(self.state/'installed.json')['journal'],str(journal))
        installed=setup.install(plan,audited['plan_sha256'])
        self.assertEqual(setup.verify(Path(installed['journal']))['skills'],33)
        self.assertEqual(rights.read_bytes(),original_rights)

    def test_rollback_launcher_drift_is_preserved_and_blocks_current_reaudit(self):
        launcher,journal,prior,rights=self.rolled_back_distinct_launcher()
        changed=launcher.read_bytes()+b'\n# Customer changed the restored launcher.\n'
        launcher.write_bytes(changed)
        audited=setup.audit(self.package,self.home,self.state,self.root/'drift after rollback plan.json')
        self.assertEqual(audited['status'],'blocked')
        self.assertIn('generated launcher',' '.join(audited['blockers']))
        self.assertEqual(launcher.read_bytes(),changed)

    def test_rollback_record_must_have_checked_plan_scope_and_finished_recovery(self):
        launcher,journal,prior,rights=self.rolled_back_distinct_launcher()
        original=setup.load(journal)
        for field in ('optional_rolled_back','profile_rolled_back','core_rolled_back','launcher_rolled_back'):
            with self.subTest(incomplete=field):
                changed=dict(original);changed[field]=False;setup.write(journal,changed)
                audited=setup.audit(self.package,self.home,self.state,self.root/(field+'-incomplete.json'))
                self.assertEqual(audited['status'],'blocked')
        setup.write(journal,original)
        unresolved=dict(original);unresolved['status']='rolling-back';setup.write(journal,unresolved)
        with self.assertRaisesRegex(ValueError,'unresolved'):
            setup.audit(self.package,self.home,self.state,self.root/'unresolved rollback plan.json')
        setup.write(journal,original)
        checked=setup.checked_journal(journal)
        changed_status=dict(checked[0]);changed_status['status']='complete'
        with patch.object(setup,'checked_journal',return_value=(changed_status,*checked[1:])):
            audited=setup.audit(self.package,self.home,self.state,self.root/'changed checked status.json')
            self.assertEqual(audited['status'],'blocked')
        for label,other_home,other_state in (('home',self.root/'another home',self.state),
                                            ('state',self.home,self.root/'another state')):
            with self.subTest(foreign_scope=label):
                foreign=(*checked[:3],other_home,other_state,checked[5])
                with patch.object(setup,'checked_journal',return_value=foreign):
                    with self.assertRaisesRegex(ValueError,'another installation'):
                        setup.audit(self.package,self.home,self.state,self.root/(label+'-foreign-scope.json'))
        saved=Path(original['plan']);raw=saved.read_bytes()
        altered=setup.load(saved);altered['launcher_before_sha256']='0'*64
        setup.write(saved,altered)
        with self.assertRaisesRegex(ValueError,'Approval does not match'):
            setup.audit(self.package,self.home,self.state,self.root/'tampered prior plan.json')
        saved.write_bytes(raw)
        record=setup.load(self.state/'installed.json')
        altered_record=dict(record);altered_record['source_commit']='f'*40
        setup.write(self.state/'installed.json',altered_record)
        with self.assertRaisesRegex(ValueError,'another installation'):
            setup.audit(self.package,self.home,self.state,self.root/'foreign installed identity.json')
        setup.write(self.state/'installed.json',record)

    def test_rollback_with_no_prior_launcher_does_not_adopt_an_unknown_launcher(self):
        _,installed=self.installed()
        journal=Path(installed['journal'])
        self.assertEqual(setup.rollback(journal)['status'],'rolled-back')
        launcher=Path(installed['launcher']);self.assertFalse(launcher.exists())
        launcher.write_bytes(b'#!/bin/sh\n# Unknown owner launcher after uninstall.\n')
        audited=setup.audit(self.package,self.home,self.state,self.root/'unknown after clean rollback.json')
        self.assertEqual(audited['status'],'blocked')
        self.assertEqual(launcher.read_bytes(),b'#!/bin/sh\n# Unknown owner launcher after uninstall.\n')

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
        skill=skills/'app-atelier-build'
        icon=skill/'assets/buyer-icon.png'
        # A different valid supplied icon is a local visual identity, not executable policy.
        other=skills/'gamedev-build/assets/family-icon-small.png'
        icon.write_bytes(other.read_bytes())
        large=skill/'assets/buyer-icon-large.png'
        large.write_bytes((skills/'gamedev-build/assets/family-icon-large.png').read_bytes())
        ui=skill/'agents/openai.yaml'
        ui.write_text(ui.read_text().replace('icon_small: ./assets/family-icon-small.png','icon_small: ./assets/buyer-icon.png')
                      .replace('icon_large: ./assets/family-icon-large.png','icon_large: ./assets/buyer-icon-large.png'))
        preserved=icon.read_bytes()
        _,result=self.installed()
        self.assertEqual(icon.read_bytes(),preserved)
        self.assertTrue(setup.verify(Path(result['journal']))['icons_preserved'])

    def test_guided_first_task_and_cancel_do_not_mutate(self):
        with patch.object(setup.sys.stdin,'isatty',return_value=True),patch('builtins.input',return_value='7'):
            result=setup.wizard(self.package,self.home,self.state,locale='uk')
        self.assertEqual(result['status'],'ready-to-run')
        self.assertFalse(self.state.exists())



class NativeLaunchContractTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='launcher-contract-')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve()
        self.home=self.root/'Покупець %name% & test';self.home.mkdir()
        self.state=self.home/'state';self.state.mkdir()
        self.product=self.root/'package'/'product';self.product.mkdir(parents=True)

    def test_windows_launcher_keeps_long_arguments_out_of_the_cmd_command_line(self):
        flags=['-c','agents.example.description='+('Useful role description '*2000)]
        with patch.object(setup.platform_support,'WINDOWS',True),patch.object(setup.platform_support,'codex_command',return_value=['C:/Program Files/Codex/codex.exe']),patch.object(setup.platform_support,'set_mode'),patch.object(setup,'launch_arguments',return_value=flags),patch.object(setup,'runtime_environment',return_value={}):
            launcher=Path(setup.make_launcher(self.home,self.state,self.product))
        raw=launcher.read_bytes().decode('utf8')
        invocation=next(line for line in raw.splitlines() if line.startswith('powershell.exe'))
        self.assertLess(len(invocation),8191)
        payload=raw.split(':AGENT_SYSTEM_LAUNCH_DATA\r\n')[1].strip()
        data=json.loads(base64.b64decode(payload))
        self.assertIn(flags[1],data['arguments'])
        self.assertEqual(data['environment']['HOME'],str(self.home))
        self.assertNotIn(str(self.home),invocation)
        self.assertIn('exit /b %ERRORLEVEL%',raw)

    def test_retained_runtime_environment_selects_only_inventory_bound_native_executables(self):
        architecture=setup.platform.machine().lower()
        architecture='arm64' if architecture in ('arm64','aarch64') else 'x64' if architecture in ('amd64','x86_64','x64') else architecture
        python='runtimes/python/python.exe';node='runtimes/node/node.exe'
        for rel in (python,node):
            target=self.product.parent/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b'fixture executable')
        manifest={'files':{python:{},node:{}},'portable_runtimes':{sys.platform+'-'+architecture:{'python_executable':python,'node_executable':node}}}
        (self.product.parent/'product-manifest.json').write_bytes(setup.encoded(manifest))
        original=os.environ.get('PATH','')
        with patch.object(setup.shutil,'which',return_value=str(self.home/'venv/bin/python')):
            env=setup.runtime_environment(self.product.parent)
        self.assertEqual(env['AGENT_SYSTEM_PYTHON'],str(self.product.parent/python))
        self.assertEqual(env['PYTHONIOENCODING'],'utf-8')
        self.assertEqual(env['PATH'],os.pathsep.join(part for part in [original,str((self.product.parent/python).parent),str((self.product.parent/node).parent)] if part))
        del manifest['files'][python]
        (self.product.parent/'product-manifest.json').write_bytes(setup.encoded(manifest))
        with self.assertRaisesRegex(ValueError,'inventory'):setup.runtime_environment(self.product.parent)

    def runtime_fixture(self):
        architecture=setup.platform.machine().lower()
        architecture='arm64' if architecture in ('arm64','aarch64') else 'x64' if architecture in ('amd64','x86_64','x64') else architecture
        paths={'python_executable':'runtimes/python/python.exe','node_executable':'runtimes/node/node.exe'}
        for rel in paths.values():
            target=self.product.parent/rel;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(b'fixture executable')
        manifest={'files':{rel:{} for rel in paths.values()},'portable_runtimes':{sys.platform+'-'+architecture:paths}}
        (self.product.parent/'product-manifest.json').write_bytes(setup.encoded(manifest))
        return [str((self.product.parent/paths[name]).parent) for name in ('python_executable','node_executable')]

    def test_existing_venv_and_node_path_priority_is_preserved(self):
        python_bin,node_bin=self.runtime_fixture()
        venv=self.home/'venv/bin';node=self.home/'project-node/bin'
        original=os.pathsep.join([str(venv),str(node),'host-tools'])
        with patch.dict(os.environ,{'PATH':original}),patch.object(setup.shutil,'which',side_effect=lambda name,**kwargs:str(venv/'python') if name=='python' else None):
            env=setup.runtime_environment(self.product.parent)
        self.assertEqual(env['PATH'],os.pathsep.join([original,python_bin,node_bin]))
        self.assertEqual(env['PATH'].split(os.pathsep)[0],str(venv))
        self.assertEqual(env['AGENT_SYSTEM_PYTHON'],str(Path(python_bin)/'python.exe'))

    def test_clean_host_gets_python_fallback_and_keeps_existing_node_first(self):
        python_bin,node_bin=self.runtime_fixture()
        project_node=str(self.home/'project-node/bin')
        with patch.dict(os.environ,{'PATH':project_node}),patch.object(setup.shutil,'which',return_value=None):
            env=setup.runtime_environment(self.product.parent)
        self.assertEqual(env['PATH'].split(os.pathsep),[python_bin,project_node,node_bin])

    def test_windowsapps_alias_does_not_hide_missing_python_or_a_real_later_python(self):
        python_bin,node_bin=self.runtime_fixture()
        alias=str(self.home/'Microsoft/WindowsApps')
        host=str(self.home/'real-python')
        with patch.object(setup.platform_support,'WINDOWS',True),patch.dict(os.environ,{'PATH':os.pathsep.join([alias,host])}),patch.object(setup.shutil,'which',side_effect=lambda name,**kwargs:str(Path(host)/'python.exe') if host in kwargs['path'].split(os.pathsep) and name=='python' else None) as lookup:
            env=setup.runtime_environment(self.product.parent)
            self.assertTrue(all(alias not in call.kwargs['path'].split(os.pathsep) for call in lookup.call_args_list))
        self.assertEqual(env['PATH'].split(os.pathsep),[alias,host,python_bin,node_bin])
        with patch.object(setup.platform_support,'WINDOWS',True),patch.dict(os.environ,{'PATH':alias}),patch.object(setup.shutil,'which',return_value=None):
            env=setup.runtime_environment(self.product.parent)
        self.assertEqual(env['PATH'].split(os.pathsep),[python_bin,alias,node_bin])

    def test_actual_native_path_resolution_keeps_project_tools_and_supplies_missing_python(self):
        python_bin,node_bin=self.runtime_fixture()
        extension='.exe' if setup.platform_support.WINDOWS else ''
        bundle_alias=Path(python_bin)/('python3'+extension)
        bundle_alias.write_bytes(b'fixture Python executable')
        setup.platform_support.set_mode(bundle_alias,0o755)
        venv=self.home/'venv/bin';venv.mkdir(parents=True)
        venv_python=venv/('python3'+extension);venv_python.write_bytes(b'project Python executable')
        setup.platform_support.set_mode(venv_python,0o755)
        project_node=self.home/'project-node/bin';project_node.mkdir(parents=True)
        native_node=project_node/('node'+extension);native_node.write_bytes(b'project Node executable')
        setup.platform_support.set_mode(native_node,0o755)
        original=os.pathsep.join([str(venv),str(project_node)])
        with patch.dict(os.environ,{'PATH':original}):
            env=setup.runtime_environment(self.product.parent)
        self.assertEqual(Path(shutil.which('python3',path=env['PATH'])),venv_python)
        self.assertEqual(Path(shutil.which('node',path=env['PATH'])),native_node)
        with patch.dict(os.environ,{'PATH':str(project_node)}):
            env=setup.runtime_environment(self.product.parent)
        self.assertEqual(Path(shutil.which('python3',path=env['PATH'])),bundle_alias)
        self.assertEqual(Path(shutil.which('node',path=env['PATH'])),native_node)

    def test_already_appended_setup_python_does_not_count_as_a_project_interpreter(self):
        python_bin,node_bin=self.runtime_fixture()
        installer_python=self.home/'received-package/python/python.exe'
        original=os.pathsep.join([str(installer_python.parent),'host-tools'])
        def lookup(name,**options):
            return str(installer_python) if str(installer_python.parent) in options['path'].split(os.pathsep) else None
        with patch.dict(os.environ,{'PATH':original,'AGENT_SYSTEM_PYTHON':str(installer_python)}),patch.object(setup.shutil,'which',side_effect=lookup):
            env=setup.runtime_environment(self.product.parent)
        self.assertEqual(env['PATH'].split(os.pathsep)[0],python_bin)

    @unittest.skipUnless(setup.platform_support.WINDOWS,'Execute actual Windows cmd and PowerShell launcher')
    def test_native_windows_launcher_preserves_unicode_special_paths_arguments_and_environment(self):
        receipt=self.root/'child receipt.json'
        child="import json,os,pathlib,sys;pathlib.Path(sys.argv[1]).write_text(json.dumps({'args':sys.argv[2:],'home':os.environ['HOME']},ensure_ascii=False),encoding='utf8')"
        args=['-c','agents.example.description='+('Role description '*1500)]
        with patch.object(setup.platform_support,'codex_command',return_value=[sys.executable,'-c',child,str(receipt)]),patch.object(setup,'launch_arguments',return_value=args),patch.object(setup,'runtime_environment',return_value={}):
            launcher=Path(setup.make_launcher(self.home,self.state,self.product))
        result=subprocess.run(['cmd.exe','/d','/c',str(launcher)],capture_output=True,timeout=40)
        self.assertEqual(result.returncode,0,result.stderr.decode('utf8',errors='replace'))
        observed=json.loads(receipt.read_text(encoding='utf8'))
        self.assertEqual(observed['args'],args)
        self.assertEqual(observed['home'],str(self.home))


class PackageReadGuardTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='package-read-guards-')
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve()
        self.package=self.root/'received package';self.package.mkdir()
        self.records={}
        for i in range(34):
            rel='product/kit/manifest.json' if i==0 else 'product/resources/deep/source/tree/member-%02d.txt'%i
            path=self.package/rel;path.parent.mkdir(parents=True,exist_ok=True)
            raw=('Exact UTF-8 source '+str(i)+' Проєкт\n').encode('utf8');path.write_bytes(raw)
            self.records[rel]={'sha256':setup.digest(raw),'size':len(raw),'mode':0o644}
        metadata={'schema':setup.MANIFEST,'product_id':'codex-agent-system','product_version':'1.8.0','source_commit':'a'*40,'files':self.records}
        (self.package/'product-manifest.json').write_bytes(setup.encoded(metadata))

    def test_actual_scan_has_linear_metadata_work_and_rechecks_every_content_hash(self):
        original=Path.lstat;calls=[]
        def counted(path,*args,**kwargs):
            calls.append(path)
            return original(path,*args,**kwargs)
        with patch.object(Path,'lstat',counted):setup.package_info(self.package)
        self.assertLess(len(calls),4*len(self.records)+100)
        path=self.package/'product/resources/deep/source/tree/member-01.txt'
        raw=path.read_bytes();path.write_bytes(b'X'+raw[1:])
        with self.assertRaisesRegex(ValueError,'differs from inventory'):setup.package_info(self.package)

    def test_hardlinked_package_input_is_rejected_without_changing_either_name(self):
        path=self.package/'product/resources/deep/source/tree/member-01.txt'
        linked=self.root/'outside copy';os.link(path,linked)
        before=linked.read_bytes()
        with self.assertRaisesRegex(ValueError,'hard-linked'):setup.package_info(self.package)
        self.assertEqual(path.read_bytes(),before);self.assertEqual(linked.read_bytes(),before)

    def test_parent_swapped_to_junction_or_symlink_cannot_read_moved_source_bytes(self):
        folder=self.package/'product/resources/deep/source/tree'
        path=folder/'member-01.txt';observed=path.lstat();expected=self.records[path.relative_to(self.package).as_posix()]
        outside=self.root/'outside source';folder.rename(outside)
        if setup.platform_support.WINDOWS:
            result=subprocess.run(['cmd.exe','/d','/c','mklink','/J',str(folder),str(outside)],capture_output=True)
            self.assertEqual(result.returncode,0,result.stderr)
            self.addCleanup(lambda:os.rmdir(folder) if folder.exists() else None)
        else:folder.symlink_to(outside,target_is_directory=True)
        real_open=os.fdopen;read_calls=[]
        class GuardedReader:
            def __init__(self,actual):self.actual=actual
            def __enter__(self):return self
            def __exit__(self,*args):self.actual.close()
            def fileno(self):return self.actual.fileno()
            def read(self,*args):read_calls.append(True);raise AssertionError('Outside bytes must not be read')
        def guarded_open(target,*args,**kwargs):return GuardedReader(real_open(target,*args,**kwargs))
        with patch.object(os,'fdopen',guarded_open):
            with self.assertRaisesRegex(ValueError,'path changed'):setup._scanned_member(path,observed,expected)
        self.assertEqual(read_calls,[])

    def test_opt_in_doctor_diagnostics_never_replace_json_result_or_leak_paths(self):
        output=io.StringIO()
        with patch.dict(os.environ,{'AGENT_SYSTEM_SETUP_DIAGNOSTICS':'1'}),patch.object(setup,'host_check',return_value={'ready':False,'next':'Sign in'}),patch.object(setup.sys,'stderr',output):
            result=setup.doctor(self.package,self.root/'isolated HOME')
        self.assertEqual(result['status'],'action-required')
        events=[json.loads(line.removeprefix('agent-system-setup ')) for line in output.getvalue().splitlines()]
        self.assertEqual([row['phase'] for row in events],['package-validation-start','package-validation-complete','host-check-start','host-check-complete'])
        self.assertNotIn(str(self.root),output.getvalue())


if __name__=='__main__':
    unittest.main()
