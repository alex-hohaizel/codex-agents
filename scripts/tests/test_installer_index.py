"""Exact release-subject guards, using real Git source and received ZIP bytes."""
import hashlib
import importlib.util
import json
from pathlib import Path
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[2]
sys.dont_write_bytecode=True
_previous_path=list(sys.path)
try:
    sys.path.insert(0,str(ROOT/'scripts'))
    _spec=importlib.util.spec_from_file_location('installer_index_under_test',ROOT/'scripts/installer_index.py')
    index=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(index)
finally:sys.path[:]=_previous_path


def encoded(value):return (json.dumps(value,sort_keys=True,ensure_ascii=False)+'\n').encode('utf8')
def digest(raw):return hashlib.sha256(raw).hexdigest()


class InstallerIndexTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix='installer-index-')
        self.addCleanup(self.temp.cleanup)
        self.base=Path(self.temp.name).resolve()
        self.root=self.base/'source';self.root.mkdir()
        self.artifacts=self.base/'artifacts';self.artifacts.mkdir()
        self.output=self.base/'release'
        self.version='1.8.0'
        files={'releases/current.json':encoded({'repository_version':self.version}),
               'commercial/runtime/portable-sources.json':encoded({'schema':'test-native-input-lock/1'}),
               'commercial/offer.json':encoded({'status':'release-candidate-not-offered-for-sale','editions':{'solo':{'price_minor':4900},'team':{'price_minor':14900}}})}
        for name,raw in files.items():
            path=self.root/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
        for args in [('init','-q'),('config','user.email','fixture@example.invalid'),('config','user.name','Isolated index fixture'),('add','.'),('commit','-q','-m','Reviewed fixture source')]:
            subprocess.run(['git','-C',str(self.root),*args],capture_output=True,check=True)
        self.source=subprocess.check_output(['git','-C',str(self.root),'rev-parse','HEAD'],text=True).strip()
        self.locksha=index.digest(self.root/'commercial/runtime/portable-sources.json')

    def candidate(self,platforms=None,*,changes=None,dirty=False,extra=None,corrupt_member=False,not_zip=False):
        platforms=platforms or ['linux-x64']
        label='Universal' if len(platforms)==6 else index.LABELS[platforms[0]]
        name='Agent-System-'+self.version+'-'+label+'.zip'
        folder=self.artifacts/label;folder.mkdir()
        path=folder/name
        unique=sorted(set(platforms))
        payload={'LICENSE.txt':(b'Fixture terms; no purchase grant.\n',0o644),'control.mjs':(b'// received control fixture\n',0o644)}
        portable={}
        for key in unique:
            system,arch=key.split('-');ext='.exe' if system=='win32' else ''
            node='runtimes/'+key+'/node/'+('node.exe' if ext else 'bin/node')
            python='runtimes/'+key+'/python/'+('python.exe' if ext else 'bin/python3.13')
            descriptor='runtimes/'+key+'/runtime.json'
            payload[node]=(b'Exact Node fixture bytes',0o755);payload[python]=(b'Exact Python fixture bytes',0o755)
            payload[descriptor]=(encoded({'schema':'codex-agents.portable-runtime/1','target':key,'source_commit':self.source,'source_clean':True,'input_lock_sha256':self.locksha}),0o644)
            portable[key]={'os':system,'arch':arch,'node_executable':node,'python_executable':python,'runtime_descriptor':descriptor,'input_lock_sha256':self.locksha}
        for number in range(34):payload['product/resources/fixture-%02d.txt'%number]=(b'Exact product fixture\n',0o644)
        manifest={'schema':'codex-agents.commercial-package/1','product_id':'codex-agent-system','product_version':self.version,
                  'source_commit':self.source,'source_clean':True,'edition':'unassigned','portable_runtimes':portable,
                  'files':{rel:{'sha256':digest(raw),'size':len(raw),'mode':mode} for rel,(raw,mode) in payload.items()}}
        manifest.update(changes or {})
        if not_zip:path.write_bytes(b'This is not an installer ZIP.\n')
        else:
            prefix=name[:-4]+'/'
            manifest_bytes=encoded(manifest)
            sums=''.join(row['sha256']+'  '+rel+'\n' for rel,row in manifest['files'].items())+digest(manifest_bytes)+'  product-manifest.json\n'
            content={**payload,'product-manifest.json':(manifest_bytes,0o644),'SHA256SUMS':(sums.encode('utf8'),0o644)}
            if extra:content.update(extra)
            if corrupt_member:content['control.mjs']=(b'Tampered control fixture bytes',0o644)
            with zipfile.ZipFile(path,'x',compression=zipfile.ZIP_DEFLATED) as archive:
                for rel,(raw,mode) in content.items():
                    item=zipfile.ZipInfo(prefix+rel,(2026,11,18,0,0,0));item.create_system=3
                    item.external_attr=(stat.S_IFREG|mode)<<16;archive.writestr(item,raw)
        receipt={'schema':'codex-agents.installer-build/1','source_commit':self.source,'source_clean':'false' if dirty else True,
                 'product_version':self.version,'input_lock_sha256':self.locksha,
                 'files':[{'name':name,'sha256':index.digest(path),'size':path.stat().st_size,'platforms':platforms}]}
        (folder/(name[:-4]+'.build.json')).write_bytes(encoded(receipt))
        return path

    def test_exact_native_artifact_is_copied_without_changing_commercial_terms(self):
        candidate=self.candidate();offer=(self.root/'commercial/offer.json').read_bytes()
        result=index.build(self.root,self.artifacts,self.output)
        self.assertEqual(result['source_commit'],self.source)
        self.assertEqual((self.output/candidate.name).read_bytes(),candidate.read_bytes())
        self.assertEqual((self.root/'commercial/offer.json').read_bytes(),offer)
        self.assertEqual(len(result['files']),1)

    def test_require_all_accepts_exactly_six_native_and_one_universal_subject(self):
        for key in index.LABELS:self.candidate([key])
        self.candidate(list(index.LABELS))
        result=index.build(self.root,self.artifacts,self.output,require_all=True)
        self.assertEqual(len(result['files']),7)

    def test_receipt_clean_flag_must_be_boolean_true(self):
        self.candidate(dirty=True)
        with self.assertRaises(ValueError):index.build(self.root,self.artifacts,self.output)

    def test_universal_declaration_cannot_repeat_one_platform_six_times(self):
        self.candidate(['linux-x64']*6)
        with self.assertRaises(ValueError):index.build(self.root,self.artifacts,self.output)

    def test_receipt_cannot_index_nonzip_bytes(self):
        self.candidate(not_zip=True)
        with self.assertRaises((ValueError,zipfile.BadZipFile)):index.build(self.root,self.artifacts,self.output)

    def test_embedded_source_must_match_the_current_commit(self):
        self.candidate(changes={'source_commit':'a'*40})
        with self.assertRaises(ValueError):index.build(self.root,self.artifacts,self.output)

    def test_technical_archive_cannot_be_relabelled_as_a_paid_edition(self):
        self.candidate(changes={'edition':'team'})
        with self.assertRaises(ValueError):index.build(self.root,self.artifacts,self.output)

    def test_embedded_runtime_keys_must_match_the_receipt_platforms(self):
        self.candidate(changes={'portable_runtimes':{}})
        with self.assertRaises(ValueError):index.build(self.root,self.artifacts,self.output)

    def test_matching_outer_receipt_does_not_hide_tampered_inner_payload(self):
        self.candidate(corrupt_member=True)
        with self.assertRaises(ValueError):index.build(self.root,self.artifacts,self.output)

    def test_unrecorded_private_extra_file_is_rejected(self):
        self.candidate(extra={'unrecorded-session.json':(b'isolated test extra',0o600)})
        with self.assertRaises(ValueError):index.build(self.root,self.artifacts,self.output)

    def test_modified_archive_no_longer_matches_its_receipt(self):
        path=self.candidate();path.write_bytes(path.read_bytes()+b'Unreviewed bytes')
        with self.assertRaises(ValueError):index.build(self.root,self.artifacts,self.output)

    def test_dirty_source_does_not_produce_a_clean_release_index(self):
        self.candidate();(self.root/'unreviewed.txt').write_bytes(b'Not committed')
        with self.assertRaises(ValueError):index.build(self.root,self.artifacts,self.output)


if __name__=='__main__':unittest.main()
