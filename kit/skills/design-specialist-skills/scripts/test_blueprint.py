"""Synthetic proposal fixtures; never a declaration of user consent."""
import copy
import unittest
import blueprint as b


def fixture():
    import json
    from pathlib import Path
    path=Path(__file__).resolve().parents[1]/'assets/blueprint-v2.synthetic-example.json'
    return copy.deepcopy(json.loads(path.read_text()))


class BlueprintTests(unittest.TestCase):
    def setUp(self):self.d=fixture()
    def approve(self):
        self.d['approval']={'actor':'user','decision':'approve','proposal_hash':b.proposal_hash(self.d),'proposal_version':self.d['version'],'verbatim':'SYNTHETIC approval fixture','source':'SYNTHETIC test transcript','timestamp':'2026-10-31','scope':'this exact fixture'}
    def test_proposal_can_be_prepared_without_creation_authority(self):
        self.assertEqual(b.check(self.d),[])
        self.assertTrue(b.check(self.d,True))
    def test_matching_explicit_record_passes_structure_only(self):
        self.approve();self.assertEqual(b.check(self.d,True),[])
    def test_changed_quality_invalidates_previous_approval(self):
        self.approve();self.d['brief']['quality']='different';self.assertTrue(b.check(self.d,True))
    def test_changed_team_invalidates_previous_approval(self):
        self.approve();self.d['team']['independence']='changed';self.assertTrue(b.check(self.d,True))
    def test_self_approval_fails(self):
        self.approve();self.d['approval']['actor']='assistant';self.assertTrue(b.check(self.d,True))
    def test_blocking_unknown_prevents_creation(self):
        self.d['open_questions']=[{'blocking':True,'status':'pending','question':'legal ownership'}];self.approve();self.assertTrue(b.check(self.d,True))
    def test_dropped_criterion_prevents_creation(self):
        self.d['stages'][0]['criterion_ids']=[];self.assertTrue(b.check(self.d))
    def test_family_requires_explicit_module_boundaries(self):
        self.d['architecture']['kind']='family';self.assertTrue(any('explicit installable modules' in issue for issue in b.check(self.d)))
    def test_cyclic_stages_fail(self):
        self.d['architecture']['kind']='family';self.d['stages'].append(dict(self.d['stages'][0],id='build',depends_on=['analyze']));self.d['stages'][0]['depends_on']=['build']
        self.d['architecture']['modules']=[{'name':'analysis-agent','stage_ids':['analyze']},{'name':'build-agent','stage_ids':['build']}]
        self.d['specialization_depth']['child_contracts'].append(dict(self.d['specialization_depth']['child_contracts'][0],id='CH2',stage_id='build'))
        self.assertTrue(any('cyclic' in issue for issue in b.check(self.d)))
    def test_stale_version_fails(self):
        self.approve();self.d['version']=2;self.assertTrue(b.check(self.d,True))


if __name__=='__main__':unittest.main()
