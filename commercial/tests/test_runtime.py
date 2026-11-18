import hashlib
import importlib.util
import io
import json
import os
from pathlib import Path
import stat
import subprocess
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

    def committed_source(self):
        repo=self.root/"source";repo.mkdir()
        (repo/"scripts").mkdir()
        (repo/"scripts/public.py").write_text("print('public runtime')\n")
        (repo/".gitignore").write_text("private/\n")
        subprocess.run(["git","init","-q",str(repo)],check=True,capture_output=True)
        subprocess.run(["git","-C",str(repo),"add","."],check=True,capture_output=True)
        subprocess.run(["git","-C",str(repo),"-c","user.name=Runtime Test","-c",
                        "user.email=runtime@example.invalid","commit","-qm","test source"],
                       check=True,capture_output=True)
        commit=subprocess.check_output(["git","-C",str(repo),"rev-parse","HEAD"],text=True).strip()
        return repo,commit

    def test_clean_gitignored_private_data_cannot_enter_source_closure(self):
        repo,commit=self.committed_source()
        private=repo/"scripts/private";private.mkdir()
        (private/"customer.json").write_text('{"private":"never distribute"}')
        (private/"credentials.env").write_text("API_TOKEN=private")
        self.assertEqual(subprocess.check_output(["git","-C",str(repo),"status","--porcelain"]),b"")
        out=self.root/"runtime"
        runtime.copy_source_tree(repo,"scripts",out,runtime.git_sources(repo,commit))
        self.assertEqual([p.name for p in out.iterdir()],["public.py"])
        archive=self.root/"runtime.zip";runtime.write_zip(out,archive)
        with zipfile.ZipFile(archive) as package:
            self.assertEqual(package.namelist(),["runtime/public.py"])
            self.assertNotIn(b"private",package.read("runtime/public.py"))

    def test_tracked_file_cannot_be_replaced_by_symlink_or_hardlink(self):
        repo,commit=self.committed_source();tracked=runtime.git_sources(repo,commit)
        source=repo/"scripts/public.py";outside=self.root/"private.txt";outside.write_text("private")
        source.unlink();source.symlink_to(outside)
        with self.assertRaisesRegex(ValueError,"unlinked regular"):
            runtime.copy_source_tree(repo,"scripts",self.root/"runtime",tracked)
        source.unlink();os.link(outside,source)
        with self.assertRaisesRegex(ValueError,"unlinked regular"):
            runtime.copy_source_tree(repo,"scripts",self.root/"runtime",tracked)

    def test_tracked_tree_cannot_be_replaced_by_linked_directory(self):
        repo,commit=self.committed_source();tracked=runtime.git_sources(repo,commit)
        (repo/"scripts/public.py").unlink();(repo/"scripts").rmdir()
        outside=self.root/"private-dir";outside.mkdir();(outside/"public.py").write_text("private")
        (repo/"scripts").symlink_to(outside,target_is_directory=True)
        with self.assertRaisesRegex(ValueError,"Linked runtime directory"):
            runtime.copy_source_tree(repo,"scripts",self.root/"runtime",tracked)

    def test_compiled_closure_ignores_unlisted_private_outputs(self):
        source=self.root/"dist";assets=source/"assets";assets.mkdir(parents=True)
        (source/".vite").mkdir()
        (source/"index.html").write_text('<script src="/assets/index-12345678.js"></script>')
        (assets/"index-12345678.js").write_text("console.log('public client')")
        (assets/"index-12345678.css").write_text("body {color: white}")
        (assets/"private-12345678.js").write_text("private customer data")
        (source/"customer.json").write_text("private")
        (source/".vite/manifest.json").write_text(json.dumps({"index.html":{
            "file":"assets/index-12345678.js","isEntry":True,"css":["assets/index-12345678.css"]}}))
        out=self.root/"runtime"
        result=runtime.copy_compiled_client(self.root,"dist",out)
        self.assertEqual(result["files"],["assets/index-12345678.css","assets/index-12345678.js","index.html"])
        self.assertFalse((out/"customer.json").exists())
        self.assertFalse((out/"assets/private-12345678.js").exists())
        self.assertFalse((out/".vite").exists())
        (source/".vite/manifest.json").write_text(json.dumps({"index.html":{
            "file":"../private.txt","isEntry":True}}))
        with self.assertRaisesRegex(ValueError,"Unsafe"):
            runtime.copy_compiled_client(self.root,"dist",self.root/"bad-runtime")


if __name__=="__main__":
    unittest.main()
