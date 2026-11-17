import hashlib
import importlib.util
import io
import json
from pathlib import Path
import stat
import tarfile
import tempfile
import unittest
import zipfile

SOURCE = Path(__file__).resolve().parents[2]/"scripts/build_workbench_runtime.py"
loader = importlib.util.spec_from_file_location("build_workbench_runtime", SOURCE)
runtime = importlib.util.module_from_spec(loader)
loader.loader.exec_module(runtime)


class RuntimePackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def archive(self, records):
        path = self.root/"node.tar.gz"
        with tarfile.open(path,"w:gz") as output:
            for name, payload, kind in records:
                info=tarfile.TarInfo("node-v24.22.2-darwin-arm64/"+name)
                info.type=kind
                if kind==tarfile.SYMTYPE:
                    info.linkname="/outside"
                else:
                    info.size=len(payload)
                output.addfile(info,io.BytesIO(payload) if kind==tarfile.REGTYPE else None)
        return path

    def test_extract_carries_only_binary_and_license_with_explicit_modes(self):
        archive=self.archive([("bin/node",b"node-test",tarfile.REGTYPE),
                              ("LICENSE",b"all upstream notices",tarfile.REGTYPE),
                              ("bin/npm",b"not in buyer runtime",tarfile.REGTYPE)])
        out=self.root/"runtime"
        runtime.extract_node(archive,out,"arm64")
        self.assertEqual((out/"notices/Node-LICENSE.txt").read_bytes(),b"all upstream notices")
        self.assertEqual(stat.S_IMODE((out/"bin/node").stat().st_mode),0o755)
        self.assertFalse((out/"bin/npm").exists())

    def test_upstream_archive_rejects_linked_runtime(self):
        archive=self.archive([("bin/node",b"",tarfile.SYMTYPE),("LICENSE",b"notice",tarfile.REGTYPE)])
        with self.assertRaisesRegex(ValueError,"Invalid or duplicate"):
            runtime.extract_node(archive,self.root/"runtime","arm64")

    def test_upstream_archive_rejects_escape_and_missing_license(self):
        archive=self.archive([("../../escaped",b"x",tarfile.REGTYPE)])
        with self.assertRaisesRegex(ValueError,"Unsafe"):
            runtime.extract_node(archive,self.root/"runtime","arm64")
        archive.unlink()
        archive=self.archive([("bin/node",b"x",tarfile.REGTYPE)])
        with self.assertRaisesRegex(ValueError,"omits"):
            runtime.extract_node(archive,self.root/"runtime","arm64")

    def test_archive_is_deterministic_and_keeps_executable_modes(self):
        folder=self.root/"runtime"
        folder.mkdir(); f=folder/"Runtime.command"; f.write_bytes(b"run\n"); f.chmod(0o755)
        a,b=self.root/"a.zip",self.root/"b.zip"
        runtime.write_zip(folder,a);runtime.write_zip(folder,b)
        self.assertEqual(a.read_bytes(),b.read_bytes())
        with zipfile.ZipFile(a) as archive:
            self.assertEqual(archive.getinfo("runtime/Runtime.command").external_attr>>16 & 0o777,0o755)

    def test_signature_path_cannot_accept_replaced_archive(self):
        package=self.root/"node-v24.22.2-darwin-arm64.tar.gz";package.write_bytes(b"bad archive")
        lock={"archives":{"arm64":{"name":package.name,"sha256":"0"*64}}}
        with self.assertRaisesRegex(ValueError,"Wrong or corrupted"):
            runtime.verify_node(package,self.root/"signed",self.root/"keys",lock,"arm64")


if __name__=="__main__":
    unittest.main()
