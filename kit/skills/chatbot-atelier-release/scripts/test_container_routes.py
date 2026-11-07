"""Current chat format succeeds; older/unrelated containers are rejected."""
import unittest
from teamctl import require_own_container


class CurrentContainerTests(unittest.TestCase):
    def test_current_chat_container(self):
        require_own_container({'schema_version':'chatbot.round/1','requirements':[],'completion':{}})

    def test_numbered_old_container_rejected(self):
        with self.assertRaises(ValueError):require_own_container({'schema_version':1,'requirements':[],'completion':{}})

    def test_other_product_container_rejected(self):
        for schema in ('iskra.studio/1','iskra.pipeline/1',5,'chatbot.round/0'):
            with self.subTest(schema=schema):
                with self.assertRaises(ValueError):require_own_container({'schema_version':schema,'requirements':[],'completion':{}})

    def test_other_stage_rejected(self):
        with self.assertRaises(ValueError):require_own_container({'schema_version':'chatbot.round/1','requirements':[],'completion':{}},'studio')

    def test_missing_requirements_rejected(self):
        with self.assertRaises(ValueError):require_own_container({'schema_version':'chatbot.round/1','completion':{}})

    def test_nonobject_rejected(self):
        with self.assertRaises(ValueError):require_own_container([])


if __name__=='__main__':unittest.main()
