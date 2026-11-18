import importlib.util
import hashlib
import json
from pathlib import Path
import shutil
import stat
import subprocess
import tempfile
import unittest
import zipfile

SOURCE=Path(__file__).resolve().parents[1]/"verify_distribution.py"
spec=importlib.util.spec_from_file_location("distribution",SOURCE)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

class DistributionTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve()
        self.openssl=shutil.which("openssl")
        if not self.openssl:self.skipTest("OpenSSL needed for Ed25519")
        self.key=self.root/"private.pem";self.pub=self.root/"public.pem"
        subprocess.run([self.openssl,"genpkey","-algorithm","Ed25519","-out",str(self.key)],check=True,capture_output=True)
        subprocess.run([self.openssl,"pkey","-in",str(self.key),"-pubout","-out",str(self.pub)],check=True,capture_output=True)
        self.commit="a"*40;self.archive=self.root/"buyer.zip"
        self.index=self.root/"BUILD.json";self.signature=self.root/"BUILD.sig"

    def prepare(self,member="README.md"):
        raw=b"actual buyer bytes\n"
        info={"sha256":hashlib.sha256(raw).hexdigest(),"size":len(raw),"mode":0o644}
        manifest={"schema":"codex-agents.commercial-package/1","product_id":"codex-agent-system",
                  "product_version":"1.8.0-rc.1","source_commit":self.commit,"edition":"solo",
                  "files":{"README.md":info}}
        with zipfile.ZipFile(self.archive,"w") as z:
            for name,content in [("buyer/"+member,raw),("buyer/product-manifest.json",json.dumps(manifest).encode()),("buyer/SHA256SUMS",b"")]:
                i=zipfile.ZipInfo(name);i.external_attr=(stat.S_IFREG|0o644)<<16;z.writestr(i,content)
        record={"schema":"codex-agents.commercial-build/1","source_commit":self.commit,"product_id":"codex-agent-system",
                "product_version":"1.8.0-rc.1","files":[{"name":"buyer.zip","size":self.archive.stat().st_size,"sha256":mod.sha(self.archive),
                  "product_version":"1.8.0-rc.1","edition":"solo"}]}
        self.index.write_text(json.dumps(record))
        subprocess.run([self.openssl,"pkeyutl","-sign","-inkey",str(self.key),"-rawin","-in",str(self.index),"-out",str(self.signature)],check=True,capture_output=True)

    def call(self,**kwargs):
        a=dict(archive=self.archive,index=self.index,signature=self.signature,key=self.pub,expected=self.commit,
               output=self.root/"staged",openssl=self.openssl);a.update(kwargs)
        return mod.stage(**a)

    def test_correct_signed_bytes_stage_but_wrong_source_and_corruption_do_not(self):
        self.prepare()
        with self.assertRaisesRegex(ValueError,"Unexpected source"):
            self.call(expected="b"*40)
        result=self.call()
        self.assertEqual(result["status"],"signature-and-inventory-verified")
        self.assertEqual((self.root/"staged/README.md").read_bytes(),b"actual buyer bytes\n")
        self.archive.write_bytes(self.archive.read_bytes()+b"changed")
        with self.assertRaisesRegex(ValueError,"digest"):
            self.call(output=self.root/"second")

    def test_changed_signed_index_and_foreign_key_are_rejected(self):
        self.prepare()
        self.index.write_text(self.index.read_text()+" ")
        with self.assertRaisesRegex(ValueError,"Signature"):
            self.call()

    def test_authenticated_archive_still_cannot_escape_staging(self):
        self.prepare("../../outside.txt")
        with self.assertRaisesRegex(ValueError,"Unsafe archive"):
            self.call()
        self.assertFalse((self.root/"outside.txt").exists())
        self.assertFalse((self.root/"staged").exists())

    def test_linked_trust_source_is_rejected_before_verification(self):
        self.prepare()
        link=self.root/"linked.zip";link.symlink_to(self.archive)
        with self.assertRaisesRegex(ValueError,"Linked"):
            self.call(archive=link)


if __name__=="__main__":unittest.main()
