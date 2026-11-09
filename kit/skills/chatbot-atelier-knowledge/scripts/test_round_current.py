import copy
import concurrent.futures
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import threading
import unittest
from unittest import mock
import check_round
import team_policy
import teamctl


def prepared():
    profile=team_policy.load_profile()
    ids=[r for d in profile['domains'] for r in d['requirement_ids']]
    return {'schema_version':'chatbot.round/1','brief':{'id':'B1','version':'1','user_intent':'synthetic bounded change','baseline':'fixture','constraints':['no live actions'],'authorization':'analysis only'},'requirements':[{'id':rid,'state':'active','reason':'fixture scoped assessment'} for rid in ids],'findings':[],'decisions':[],'changes':[],'evidence':[],'runs':[],'reviews':[],'team_policy':team_policy.scaffold(ids),'completion':{'stage':'prepared','scope':'synthetic only','unresolved_requirement_ids':ids},'checkpoint':{'next_action':'perform actual checks'}}


def extension():
    return {'id': 'patron-membership', 'state': 'active', 'reason': 'explicit synthetic product scope',
            'source_ref': 'SYNTHETIC-owner-message', 'owner': 'patrons-domain', 'domain_id': 'patrons',
            'acceptance': 'Only current members receive the private result',
            'negative_probe': 'Revoked member cannot receive it'}


def extended_prepared():
    d = prepared(); extra = extension(); d['requirements'].append(extra)
    ids = [r['id'] for r in d['requirements']]
    d['completion']['unresolved_requirement_ids'] = ids
    d['team_policy'] = team_policy.scaffold(ids, requirement_domains={extra['id']: extra['domain_id']})
    return d


def independently_reviewed(directory):
    """Current 25-criterion synthetic review, with actual local fixture bytes only."""
    from test_team_policy import fixture
    plan, runs, baseline, profile = fixture(directory)
    d = extended_prepared(); extra = extension(); rid = extra['id']
    plan['scope']['active_requirement_ids'].append(rid)
    plan['assignments'][rid] = {'domain_id': extra['domain_id'], 'status': 'active',
        'component_ids': ['changed'], 'owner_run': 'patron-owner', 'qa_run': 'patron-qa',
        'judge_run': 'patron-judge', 'verdict': 'accept', 'evidence_refs': ['component.txt'],
        'evidence_sha256s': {'component.txt': team_policy.digest((Path(directory) / 'component.txt').read_bytes())}}
    for kind, actor in [('specialist', 'patron-author'), ('qa', 'patron-qa'), ('judge', 'patron-judge')]:
        identity = {'specialist': 'patron-owner', 'qa': 'patron-qa', 'judge': 'patron-judge'}[kind]
        output = Path(directory) / 'audit' / (identity + '.md'); output.write_text('SYNTHETIC: ' + identity)
        run = {'id': identity, 'kind': kind, 'actor_id': actor, 'status': 'completed', 'verdict': 'accept',
               'requirement_ids': [rid], 'domain_ids': ['patrons'], 'output_ref': 'audit/' + output.name,
               'output_sha256': team_policy.digest(output.read_bytes())}
        if kind == 'judge':
            run.update(context_mode='fresh', review_mode='primary', criteria={rid: {'verdict': 'accept',
                'positive_claim': 'SYNTHETIC membership fixture', 'strongest_objection': 'fixture only',
                'uncertainty': 'no provider or humans', 'reversal_condition': 'changed membership rule'}})
        runs.append(run)
    for run in runs:
        if run['id'] in ('guardian', 'root'):
            run['requirement_ids'].append(rid)
    d['team_policy'], d['runs'] = plan, runs
    for run in runs:
        run['input_snapshot'] = team_policy.snapshot_inputs(plan, run, runs, profile, d['requirements'])
    d['evidence'] = [{'id': 'E1', 'version': '1', 'kind': 'execution', 'provenance': 'reproduced synthetic fixture',
                      'artifact': 'component.txt', 'procedure': 'test only', 'result': 'passed', 'limitations': ['SYNTHETIC']}]
    d['completion'].update(stage='independently_reviewed', status='stage_complete', unresolved_requirement_ids=[])
    frozen = team_policy.snapshot_hash(d); d['completion']['package_hash'] = frozen
    for run in runs:
        if run['kind'] == 'judge': run['package_hash'] = frozen
    indexed = {r['id']: r for r in runs}
    d['reviews'] = [{'requirement_id': r, 'verdict': 'accept', 'evidence_ids': ['E1'],
                     'run_id': plan['assignments'][r]['judge_run'],
                     'actor_id': indexed[plan['assignments'][r]['judge_run']]['actor_id'],
                     'package_hash': frozen} for r in baseline + [rid]]
    return d


class CurrentRoundTests(unittest.TestCase):
    def test_prepared_is_not_fake_review(self):self.assertEqual([],check_round.check(prepared()))
    def test_old_numbered_round_is_not_read(self):d=prepared();d['schema_version']=1;self.assertTrue(any('chatbot.round/1' in e for e in check_round.check(d)))
    def test_team_policy_is_always_required(self):d=prepared();d.pop('team_policy');self.assertTrue(any('current team_policy' in e for e in check_round.check(d)))
    def test_fixed_judge_fallback_removed(self):d=prepared();d.pop('team_policy');d['completion']['stage']='independently_reviewed';self.assertTrue(any('current team_policy' in e for e in check_round.check(d)))
    def test_old_team_schema_rejected(self):d=prepared();d['team_policy']['schema_version']='iskra.team/2';self.assertTrue(any('current team_policy' in e for e in check_round.check(d)))
    def test_run_alias_is_not_canonical_field(self):d=prepared();d['runs']=[{'id':'R1','actor_id':'a','agent_id':'a','kind':'specialist','status':'prepared','output_ref':'fixture.txt'}];self.assertTrue(any('unsupported run field alias' in e for e in check_round.check(d)))

    def test_project_criterion_extends_immutable_24_baseline(self):
        self.assertEqual(check_round.check(extended_prepared()), [])

    def test_project_extension_requires_source_owner_acceptance_and_negative_probe(self):
        for field in ('source_ref', 'owner', 'domain_id', 'acceptance', 'negative_probe'):
            with self.subTest(field=field):
                d = extended_prepared(); d['requirements'][-1].pop(field)
                self.assertTrue(any('project requirement' in e and field in e for e in check_round.check(d)))

    def test_project_domain_cannot_differ_between_scope_and_assignment(self):
        d = extended_prepared(); d['team_policy']['assignments']['patron-membership']['domain_id'] = 'unrelated'
        self.assertTrue(any('domain differs' in e for e in check_round.check(d)))

    def test_project_extension_cannot_replace_or_drop_baseline(self):
        d = extended_prepared(); d['requirements'].pop(0)
        self.assertTrue(any('baseline requirement IDs' in e for e in check_round.check(d)))

    def test_project_extension_gets_actual_independent_stage_coverage(self):
        with tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve()) as directory:
            d = independently_reviewed(directory)
            self.assertEqual(check_round.check(d, source_root=directory), [])
            d['reviews'] = [r for r in d['reviews'] if r['requirement_id'] != 'patron-membership']
            self.assertTrue(any('every active criterion' in e for e in check_round.check(d, source_root=directory)))

    def test_planner_preserves_project_domain_without_reassigning_canonical_domains(self):
        d = extended_prepared(); d.pop('team_policy')
        with tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve()) as directory:
            path = Path(directory) / 'round.json'; path.write_text(json.dumps(d))
            env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
            result = subprocess.run([sys.executable, '-B', str(Path(__file__).with_name('teamctl.py')), 'plan', str(path)],
                                    env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            planned = json.loads(path.read_text())
            self.assertEqual(planned['team_policy']['assignments']['patron-membership']['domain_id'], 'patrons')
            self.assertEqual(check_round.check(planned), [])
        profile = team_policy.load_profile(); canonical = profile['domains'][0]['requirement_ids'][0]
        plan = team_policy.scaffold([r['id'] for r in d['requirements']], requirement_domains={canonical: 'wrong'})
        self.assertEqual(plan['assignments'][canonical]['domain_id'], profile['domains'][0]['id'])

    def test_acceptance_cannot_reference_explicit_failed_evidence(self):
        d = prepared(); rid = d['requirements'][0]['id']
        d['evidence'] = [{'id': 'E1', 'version': '1', 'kind': 'execution', 'provenance': 'synthetic',
                          'artifact': 'synthetic.log', 'procedure': 'test', 'result': 'failed', 'limitations': []}]
        d['reviews'] = [{'requirement_id': rid, 'verdict': 'accept', 'evidence_ids': ['E1']}]
        self.assertTrue(any('unsuccessful evidence' in e for e in check_round.check(d)))

    def test_ready_acceptance_requires_explicit_positive_outcome_after_actual_refreeze(self):
        with tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve()) as directory:
            d = independently_reviewed(directory)
            for result in ('fail', 'failed', 'not_run', 'inconclusive', 'blocked', 'observed', 'banana'):
                with self.subTest(result=result):
                    d['evidence'][0]['result'] = result
                    frozen = team_policy.snapshot_hash(d); d['completion']['package_hash'] = frozen
                    for run in d['runs']:
                        if run['kind'] == 'judge': run['package_hash'] = frozen
                    for review in d['reviews']: review['package_hash'] = frozen
                    errors = check_round.check(d, source_root=directory)
                    self.assertTrue(any('unsuccessful evidence' in e for e in errors), errors)
                    if result == 'banana': self.assertTrue(any('invalid evidence result' in e for e in errors), errors)

    def test_negative_outcome_can_be_honestly_recorded_without_accepting_review(self):
        d = prepared(); d['evidence'] = [{'id': 'E1', 'version': '1', 'kind': 'execution', 'provenance': 'synthetic',
            'artifact': 'synthetic.log', 'procedure': 'test', 'result': 'not_run', 'limitations': ['no attempt performed']}]
        self.assertEqual(check_round.check(d), [])

    def test_acceptance_cannot_use_empty_or_untyped_evidence_identity(self):
        d = prepared(); rid = d['requirements'][0]['id']
        d['reviews'] = [{'requirement_id': rid, 'verdict': 'accept', 'evidence_ids': []}]
        self.assertTrue(any('primary evidence IDs' in e for e in check_round.check(d)))
        d['evidence'] = [{'id': None, 'version': '1', 'kind': 'execution', 'provenance': 'synthetic',
            'artifact': 'synthetic.log', 'procedure': 'test', 'result': 'passed', 'limitations': []}]
        d['reviews'][0]['evidence_ids'] = [None]
        self.assertTrue(any('nonempty string IDs' in e for e in check_round.check(d)))

    def test_readiness_axes_do_not_inherit_global_pass(self):
        d = prepared(); d['completion']['assessments'] = {'human': {'status': 'pending', 'scope': 'conversation quality', 'evidence_ids': []}}
        self.assertEqual(check_round.check(d), [])
        d['completion']['assessments']['human']['status'] = 'passed'
        self.assertTrue(any('needs evidence' in e for e in check_round.check(d)))

    def test_source_only_proof_cannot_close_code_or_integration(self):
        for axis in ('code', 'integration'):
            with self.subTest(axis=axis):
                d = prepared()
                d['evidence'] = [{'id': 'E1', 'version': '1', 'kind': 'source', 'provenance': 'SYNTHETIC',
                    'artifact': 'spec.md', 'procedure': 'source read', 'result': 'passed', 'limitations': ['no execution']}]
                d['completion']['assessments'] = {axis: {'status': 'passed', 'scope': 'fixture only', 'evidence_ids': ['E1']}}
                self.assertTrue(any('admissible' in e for e in check_round.check(d)))
                d['evidence'][0].update(kind='code' if axis == 'code' else 'integration',
                    build_ref='SYNTHETIC-build', environment='isolated fixture', actual_observation_ref='SYNTHETIC-run')
                self.assertEqual(check_round.check(d), [])

    def test_stale_round_writer_cannot_lose_committed_decision(self):
        with tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve()) as directory:
            path = Path(directory).resolve() / 'round.json'; path.write_text(json.dumps(prepared()))
            first, second = teamctl.read(path), teamctl.read(path)
            first['decisions'].append({'id': 'D-FIRST'}); teamctl.save(path, first)
            second['decisions'].append({'id': 'D-SECOND'})
            with self.assertRaisesRegex(ValueError, 'revision conflict'):
                teamctl.save(path, second)
            self.assertEqual(teamctl.read(path)['decisions'], [{'id': 'D-FIRST'}])

    def test_raw_round_overwrite_requires_an_explicit_current_revision(self):
        with tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve()) as directory:
            path = Path(directory).resolve() / 'round.json'; path.write_text(json.dumps(prepared()))
            raw = prepared()
            with self.assertRaisesRegex(ValueError, 'revision conflict'):
                teamctl.save(path, raw)
            pin = teamctl.read(path).source_sha256
            teamctl.save(path, raw, expected_sha256=pin)
            self.assertEqual(teamctl.read(path), raw)

    def test_round_replace_failure_preserves_current_bytes_and_cleans_temporary(self):
        with tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve()) as directory:
            path=Path(directory)/'round.json';path.write_text(json.dumps(prepared()))
            before=path.read_bytes();record=teamctl.read(path);record['decisions'].append({'id':'uncommitted'})
            with mock.patch.object(teamctl.os,'replace',side_effect=OSError('synthetic pre-commit failure')):
                with self.assertRaises(OSError):teamctl.save(path,record)
            self.assertEqual(path.read_bytes(),before)
            self.assertEqual({p.name for p in path.parent.iterdir()},{'round.json','.round.json.lock'})

    def test_simultaneous_round_writers_have_one_commit_and_one_conflict(self):
        with tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve()) as directory:
            path=Path(directory)/'round.json';path.write_text(json.dumps(prepared()))
            records=[teamctl.read(path),teamctl.read(path)];barrier=threading.Barrier(2)
            def writer(index):
                records[index]['decisions'].append({'id':'D-'+str(index)})
                barrier.wait(timeout=5)
                try:teamctl.save(path,records[index]);return 'committed'
                except ValueError as error:
                    self.assertIn('revision conflict',str(error));return 'conflict'
            with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
                results=list(executor.map(writer,range(2)))
            self.assertEqual(sorted(results),['committed','conflict'])
            self.assertEqual(len(teamctl.read(path)['decisions']),1)

    def test_human_pass_needs_actual_human_observation(self):
        d = prepared(); d['evidence'] = [{'id': 'H1', 'version': '1', 'kind': 'code', 'provenance': 'synthetic',
            'artifact': 'notes.md', 'procedure': 'test', 'result': 'passed', 'limitations': ['SYNTHETIC']}]
        d['completion']['assessments'] = {'human': {'status': 'passed', 'scope': 'owner-defined conversation task', 'evidence_ids': ['H1']}}
        self.assertTrue(any('actual human observation' in e for e in check_round.check(d)))
        d['evidence'][0].update(kind='human', actual_observation_ref='SYNTHETIC-user-response')
        self.assertEqual(check_round.check(d), [])

    def test_unknown_assessment_and_fake_human_stage_rejected(self):
        d = prepared(); d['completion']['assessments'] = {'banana': {'status': 'passed', 'scope': 'x', 'evidence_ids': []}}
        self.assertTrue(any('unknown readiness axis' in e for e in check_round.check(d)))
        d = prepared(); d['completion']['stage'] = 'human_validated'
        self.assertTrue(any('separate completion.assessments.human' in e for e in check_round.check(d)))

    def test_malformed_round_returns_diagnostics(self):
        for d in (None, [], {'requirements': [None]}, dict(prepared(), requirements=[{'id': []}])):
            with self.subTest(record=type(d).__name__): self.assertTrue(check_round.check(d))

    def test_bind_inputs_prepares_new_qa_without_execution_or_acceptance(self):
        with tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve()) as directory:
            d=independently_reviewed(directory)
            existing=next(r for r in d['runs'] if r['id']=='patron-qa')
            new=copy.deepcopy(existing);new.update(id='SYNTHETIC-new-qa',status='planned',output_ref='audit/new-qa.md')
            for key in ('input_snapshot','output_sha256','verdict'):new.pop(key,None)
            d['runs'].append(new);d['team_policy']['assignments']['patron-membership']['qa_run']=new['id']
            path=Path(directory)/'round.json';path.write_text(json.dumps(d))
            command=[sys.executable,'-B',str(Path(__file__).with_name('teamctl.py')),'bind-inputs',str(path),'--run',new['id']]
            result=subprocess.run(command,env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1'),capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            saved=json.loads(path.read_text());bound=next(r for r in saved['runs'] if r['id']==new['id'])
            self.assertEqual(bound['status'],'planned');self.assertNotIn('verdict',bound)
            self.assertEqual(bound['input_snapshot']['schema_version'],'chatbot.run-inputs/1')
            self.assertIn('patron-owner',bound['input_snapshot']['reviewed_outputs'])
            before=path.read_bytes();again=subprocess.run(command,capture_output=True,text=True)
            self.assertNotEqual(again.returncode,0);self.assertEqual(path.read_bytes(),before)

    def test_hashes_and_bind_do_not_rewrite_completed_run_provenance(self):
        with tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve()) as directory:
            d=independently_reviewed(directory);path=Path(directory)/'round.json';path.write_text(json.dumps(d))
            script=str(Path(__file__).with_name('teamctl.py'));before=path.read_bytes()
            result=subprocess.run([sys.executable,'-B',script,'bind-inputs',str(path),'--run','patron-qa'],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0);self.assertEqual(path.read_bytes(),before)
            self.assertIn('immutable',result.stdout)
            authored=next(r for r in d['runs'] if r['id']=='patron-owner')
            (Path(directory)/authored['output_ref']).write_text('SYNTHETIC mutated completed output')
            result=subprocess.run([sys.executable,'-B',script,'hashes',str(path)],capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0);self.assertEqual(path.read_bytes(),before)
            self.assertIn('Completed run output changed',result.stdout)

    def test_new_producer_can_bind_requirements_without_fabricated_output_component(self):
        d=prepared();rid=d['requirements'][0]['id']
        run={'id':'SYNTHETIC-new-author','actor_id':'SYNTHETIC-author','kind':'specialist','status':'planned',
             'requirement_ids':[rid],'domain_ids':[d['team_policy']['assignments'][rid]['domain_id']],
             'input_component_ids':[],'input_scope_reason':'new output from the accepted requirement, no previous artifact',
             'output_ref':'future-output.md'}
        d['runs']=[run]
        with tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve()) as directory:
            path=Path(directory)/'round.json';path.write_text(json.dumps(d))
            result=subprocess.run([sys.executable,'-B',str(Path(__file__).with_name('teamctl.py')),'bind-inputs',str(path),
                                   '--run',run['id']],capture_output=True,text=True)
            self.assertEqual(result.returncode,0,result.stdout+result.stderr)
            saved=json.loads(path.read_text());self.assertEqual(saved['runs'][0]['input_snapshot']['components'],{})
            self.assertIn(rid,saved['runs'][0]['input_snapshot']['requirements'])
            self.assertFalse((Path(directory)/'future-output.md').exists())
            self.assertEqual(saved['runs'][0]['status'],'planned')


if __name__=='__main__':unittest.main()
