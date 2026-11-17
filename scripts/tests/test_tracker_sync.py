import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import tracker_sync as sync
from tracker_providers import ProviderError


class Provider:
    capabilities = frozenset({"list","read","create","update:title","update:status",
                              "update:parent_id","update:blocker_ids"})
    def __init__(self):
        self.items = []
        self.receipts = []
        self.calls = []
        self.error = False
        self.rejected = False
        self.lose_after = False

    def verify_container(self):
        return {"id":"77","key":"team/booking"}

    def list_items(self):
        return self.items

    def read_item(self, id, key):
        return next(i for i in self.items if i["id"] == id and i["key"] == key)

    def find_marker(self, marker):
        return [r for r in self.items if r["marker"] == marker]

    def create_item(self, spec):
        self.calls.append("create")
        if self.rejected:
            raise ProviderError("authentication-required")
        if self.error:
            raise ProviderError("transport-unknown",uncertain=True)
        row = {"id":str(len(self.items)+1),"key":str(len(self.items)+1),"title":spec["title"],
               "marker":spec["marker"],"container_id":"77","status":"open","parent_id":None,"blocker_ids":[]}
        self.items.append(row)
        if self.lose_after:
            raise ProviderError("transport-unknown",uncertain=True)
        return row

    def update_item(self, item, changes):
        self.calls.append("update")
        self.read_item(item["id"], item["key"]).update(changes)


class TreeSyncTests(unittest.TestCase):
    def begin(self, root):
        self.root=root
        self.provider=Provider()
        self.req = {"requirements":[{"id":"R1","priority":"must","text":"Preserve the installed recovery journal."}]}
        self.pin = self.write("requirements.json",self.req)
        self.projection = {"schema_version":sync.trees.PROJECTION,"project_id":"release",
                           "native_revision":"r1","requirement_sources":[{"path":"requirements.json","sha256":self.pin}],
                           "tickets":[{"id":"P","title":"Release recovery","kind":"initiative","status":"planned","requirement_ids":["R1"]},
                                      {"id":"S","title":"Verify the journal","kind":"story","status":"planned","parent":"P","requirement_ids":["R1"]}]}
        self.write("tickets.json",self.projection)
        self.write("config.json",{"provider":"github","container":{"id":"77","key":"team/booking"},"auth":{}})
        self.mapping = {"schema_version":sync.MAPPING,"project_id":"release","provider":"github","container_id":"77",
                        "statuses":{"planned":"open","accepted":"closed:completed"},"tickets":[]}
        self.write("mapping.json",self.mapping)

    def setUp(self):
        folder=tempfile.TemporaryDirectory()
        self.addCleanup(folder.cleanup)
        self.begin(Path(folder.name).resolve())

    def write(self,name,obj):
        raw=sync.encoded(obj)
        (self.root/name).write_bytes(raw)
        return sync.cx.digest(raw)

    def factory(self,config):
        return self.provider

    def plan(self,path):
        obj=sync.preview(self.root,"tickets.json","config.json","mapping.json",self.factory)
        pin=self.write(path,obj)
        return obj,pin

    def run_action(self,path,pin,obj, action=None, apply=True,root=None):
        aid=action or next(iter(obj["actions"]))
        return sync.execute(root or self.root,path,pin,aid,self.factory,apply=apply)

    def test_tree_parent_then_child_and_read_back_after_lost_response(self):
        p,h=self.plan("a.json")
        self.assertEqual([row["ticket_id"] for row in p["actions"].values()],["P"])
        self.assertIn("map-parent-first",[i["code"] for i in p["findings"]])
        self.assertEqual(self.run_action("a.json",h,p,apply=False)["status"],"unattempted")
        self.provider.lose_after=True
        result=self.run_action("a.json",h,p)
        self.assertEqual(result["status"],"observed")
        self.assertEqual(self.run_action("a.json",h,p,apply=False)["writes"],0)
        self.assertEqual(self.run_action("a.json",h,p)["writes"],0)
        self.assertEqual(self.provider.calls,["create"])
        self.mapping["tickets"]=[result["mapping_candidate"]]
        self.write("mapping.json",self.mapping)
        next_p,_=self.plan("b.json")
        self.assertEqual([row["ticket_id"] for row in next_p["actions"].values()],["S"])

    def test_pending_fences_renamed_create_and_readback_survives_local_drift(self):
        p,h=self.plan("a.json")
        self.provider.error=True
        self.assertEqual(self.run_action("a.json",h,p)["status"],"pending")
        self.projection["tickets"][0]["title"]="Release recovery after revision"
        self.write("tickets.json",self.projection)
        new_p,new_h=self.plan("b.json")
        stopped=self.run_action("b.json",new_h,new_p)
        self.assertEqual(stopped["status"],"previous-effect-pending")
        self.assertEqual(self.run_action("a.json",h,p,apply=False)["status"],"pending")
        self.assertEqual(self.provider.calls,["create"])

    def test_wrong_checkout_and_changed_source_block_before_writes(self):
        p,h=self.plan("a.json")
        with tempfile.TemporaryDirectory() as folder:
            target=Path(folder).resolve()
            for f in self.root.glob("*.json"):
                shutil.copyfile(f,target/f.name)
            with self.assertRaisesRegex(ValueError,"another checkout"):
                self.run_action("a.json",h,p,root=target)
        self.req["requirements"][0]["text"]="New outcome"
        self.write("requirements.json",self.req)
        with self.assertRaisesRegex(ValueError,"SOURCE_DRIFT"):
            self.run_action("a.json",h,p)
        self.assertEqual(self.provider.calls,[])

    def test_only_fresh_approval_for_definite_rejection_can_retry(self):
        first,h=self.plan("a.json")
        self.provider.rejected=True
        self.assertEqual(self.run_action("a.json",h,first)["status"],"rejected")
        self.provider.rejected=False
        second,new_hash=self.plan("b.json")
        self.assertEqual(self.run_action("b.json",new_hash,second)["status"],"rejected")
        action=next(iter(second["actions"]))
        res=sync.execute(self.root,"b.json",new_hash,action,self.factory,apply=True,retry_rejected=True)
        self.assertEqual(res["status"],"observed")
        self.assertEqual(self.provider.calls,["create","create"])
        self.assertEqual(len(self.provider.items),1)

    def test_remote_only_and_concurrent_changes_remain_visible(self):
        p,h=self.plan("a.json")
        result=self.run_action("a.json",h,p)
        self.mapping["tickets"]=[result["mapping_candidate"]]
        self.write("mapping.json",self.mapping)
        self.provider.items[0]["title"]="Provider renamed"
        q,_=self.plan("b.json")
        self.assertIn("inbound-proposal",[row["code"] for row in q["findings"]])
        self.projection["tickets"][0]["title"]="Local renamed"
        self.write("tickets.json",self.projection)
        q,_=self.plan("c.json")
        self.assertIn("concurrent-change",[row["code"] for row in q["findings"]])
        self.assertFalse(any(a["ticket_id"]=="P" for a in q["actions"].values()))

    def test_remote_relations_to_unmanaged_items_cannot_be_removed(self):
        p,h=self.plan("a.json")
        receipt=self.run_action("a.json",h,p)
        externally_linked={"parent_id":"901","blocker_ids":["900"]}
        self.provider.items[0].update(externally_linked)
        mapped=receipt["mapping_candidate"]
        mapped["last"].update(externally_linked)
        self.mapping["tickets"]=[mapped]
        self.write("mapping.json",self.mapping)
        q,_=self.plan("b.json")
        held=[r for r in q["findings"] if r["code"]=="unmapped-remote-relationship-held"]
        self.assertEqual({r["field"] for r in held},{"parent_id","blocker_ids"})
        self.assertFalse(any(a["ticket_id"]=="P" for a in q["actions"].values()))

    def test_remote_acceptance_is_not_granted_when_local_lacks_proof(self):
        p,h=self.plan("a.json")
        result=self.run_action("a.json",h,p)
        self.mapping["tickets"]=[result["mapping_candidate"]]
        self.write("mapping.json",self.mapping)
        self.projection["tickets"][0]["status"]="accepted"
        self.write("tickets.json",self.projection)
        q,_=self.plan("a2.json")
        self.assertIn("local-acceptance-unproved",[row["code"] for row in q["findings"]])
        self.assertFalse(any(a["ticket_id"]=="P" for a in q["actions"].values()))


if __name__=="__main__":
    unittest.main()
