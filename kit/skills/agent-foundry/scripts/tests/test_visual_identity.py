import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('visual_identity',Path(__file__).resolve().parents[1]/'visual_identity.py')
v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)


class IdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(dir=Path(tempfile.gettempdir()).resolve());self.root=Path(self.temp.name)
        (self.root/'agents').mkdir();(self.root/'assets').mkdir()

    def tearDown(self):self.temp.cleanup()

    def yaml(self,text):(self.root/'agents/openai.yaml').write_text(text)

    def test_existing_is_never_recreated(self):
        self.yaml('interface:\n  display_name: Original\n  icon_small: assets/custom.svg\n  icon_large: assets/custom.svg\n  brand_color: "#123456"\npolicy:\n  allow_implicit_invocation: true\n')
        p=self.root/'assets/custom.svg';p.write_text('<svg>custom</svg>')
        before=v.freeze(self.root,'system');result=v.create(self.root,'AB')
        self.assertEqual(result['status'],'preserved');self.assertEqual(before['files'],result['snapshot']['files'])
        self.assertEqual(p.read_text(),'<svg>custom</svg>');self.assertFalse((self.root/'assets/icon.svg').exists())

    def test_missing_referenced_icon_is_conflict(self):
        self.yaml('interface:\n  icon_small: assets/missing.svg\n')
        with self.assertRaises(ValueError):v.create(self.root,'AB')

    def test_new_project_style_and_exclusive_creation(self):
        result=v.create(self.root,'DB');self.assertEqual(result['style'],'project-card-v1')
        self.assertIn('project-card-v1',(self.root/'assets/icon.svg').read_text())
        with self.assertRaises(ValueError):v.create(self.root,'XX')

    def test_unsafe_icon_and_link_are_rejected(self):
        for ref in ['../outside.svg','/tmp/a.svg','scripts/evil.svg','assets/../a.svg']:
            self.yaml('interface:\n  icon_small: '+ref+'\n')
            with self.assertRaises(ValueError):v.freeze(self.root,'system')
        (self.root/'outside.svg').write_text('x');(self.root/'assets/link.svg').symlink_to(self.root/'outside.svg')
        self.yaml('interface:\n  icon_small: assets/link.svg\n')
        with self.assertRaises(ValueError):v.freeze(self.root,'system')

    def test_duplicate_and_complex_yaml_fail_closed(self):
        for text in ['interface:\n  icon_small: assets/a.svg\n  icon_small: assets/b.svg\n','interface: {icon_small: assets/a.svg}\n','interface:\n  <<: *unknown\n']:
            self.yaml(text)
            with self.assertRaises(ValueError):v.freeze(self.root,'system')

    def test_hash_detects_icon_change_json_ui(self):
        self.yaml(json.dumps({'interface':{'icon_small':'assets/a.png','brand_color':'#123456'}}))
        p=self.root/'assets/a.png';p.write_bytes(b'first');a=v.freeze(self.root,'project')
        p.write_bytes(b'second');b=v.freeze(self.root,'project');self.assertNotEqual(a,b)

    def test_actual_portable_dot_paths_keep_raw_bindings(self):
        self.yaml('interface:\n  icon_small: ./assets/custom.svg\n  icon_large: ./assets/custom.svg\n')
        (self.root/'assets/custom.svg').write_text('<svg/>')
        x=v.freeze(self.root,'system')
        self.assertEqual(x['interface']['icon_small'],'./assets/custom.svg')
        self.assertIn('assets/custom.svg',x['files'])
        self.assertEqual(v.create(self.root,'XX')['status'],'preserved')

    def test_quoted_and_spaced_keys_detect_real_icon(self):
        self.yaml('"interface" :\n  "icon_small" : assets/custom.svg\n')
        p=self.root/'assets/custom.svg';p.write_text('one')
        a=v.freeze(self.root,'system');p.write_text('two')
        self.assertNotEqual(a,v.freeze(self.root,'system'))
        self.assertEqual(v.create(self.root,'XX')['status'],'preserved')

    def test_duplicate_json_is_rejected(self):
        self.yaml('{"interface":{"icon_small":"a","icon_small":"b"}}')
        with self.assertRaises(ValueError):v.freeze(self.root,'system')


if __name__=='__main__':unittest.main()
