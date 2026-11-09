"""Policy/state loaders reject ambiguity before interpreting an input record."""
from pathlib import Path
import types
import unittest


ROOT=Path(__file__).resolve().parents[1]


def module(name):
    path=ROOT/name
    result=types.ModuleType('json_admission_'+path.stem)
    result.__file__=str(path)
    exec(compile(path.read_bytes(),str(path),'exec'),result.__dict__)
    return result


class JsonAdmissionTests(unittest.TestCase):
    def test_core_policy_and_manifest_loaders_reject_nested_duplicate_and_nonfinite(self):
        for name in ('foundry.py','verify_depth.py','check_foundry_depth.py','check_generated_inheritance.py','install_agent.py','update_skill_suite.py',
                     'check_component_handoff.py','discover_specialists.py','package_agent.py','visual_identity.py'):
            with self.subTest(loader=name):
                reader=module(name).strict_json_loads
                self.assertEqual(reader('{"valid":{"value":3}}'),{'valid':{'value':3}})
                for payload in ('{"grant":{"allowed":true,"allowed":false}}','{"value":NaN}','{"value":Infinity}'):
                    with self.subTest(payload=payload),self.assertRaises(ValueError):reader(payload)


if __name__=='__main__':unittest.main()
