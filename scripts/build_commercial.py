#!/usr/bin/env python3
"""Build deterministic buyer archives from one clean source commit; no publication."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import zipfile

sys.dont_write_bytecode = True
EXCLUDED = {".git","__pycache__",".DS_Store","node_modules","dist",".atelier-local",".pytest_cache","playwright-report","test-results"}
ROOTS = ("kit","scripts","standards","host-profiles","agent-profiles","optional-skills","templates","releases",
         "apps",".github","governance","docs","evaluations","marketing","assets","commercial","maintenance-skill",
         "README.md","START_HERE.md","START_HERE.html","ПОЧАТИ.html","Start.command","Start.sh","Start.cmd",
         "Start-Workbench.command","Start-Workbench.sh","Start-Workbench.cmd","CHANGELOG.md","RIGHTS.md","AGENTS.md","locales.json")
PRODUCT = "codex-agent-system"


def need(condition, message):
    if not condition:
        raise ValueError(message)


def digest(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for b in iter(lambda:f.read(128*1024), b""):
            h.update(b)
    return h.hexdigest()


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def capture(root):
    sha = subprocess.check_output(["git","rev-parse","HEAD"],cwd=root,text=True).strip()
    need(re.fullmatch("[a-f0-9]{40}",sha), "Full source commit required")
    need(not subprocess.check_output(["git","status","--porcelain","--untracked-files=normal"],cwd=root),
         "Commercial archives require a clean source commit. Commit reviewed sources first.")
    return sha


def paths(root, relative):
    origin=root/relative
    need(origin.exists(),"Missing source "+relative)
    tracked = {os.fsdecode(p) for p in subprocess.check_output(["git","ls-files","-z"],cwd=root).split(b"\0") if p}
    for path in sorted(origin.rglob("*") if origin.is_dir() else [origin]):
        rel=path.relative_to(root)
        if EXCLUDED.intersection(rel.parts) or path.suffix==".pyc":
            continue
        if rel.as_posix() not in tracked:
            continue
        need(not path.is_symlink(),"Linked package member "+str(rel))
        if path.is_file():
            need(not any(p.startswith(".env") or p.endswith((".key",".sqlite",".db")) for p in rel.parts),
                 "Private or state source prohibited "+str(rel))
            yield path


def copy_group(root, stage, relative, prefix=""):
    for source in paths(root,relative):
        if prefix=="product" and source.relative_to(root).parts[:2]==("commercial","site"):
            continue
        target=stage/prefix/source.relative_to(root)
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,target)
        target.chmod(0o755 if source.stat().st_mode & stat.S_IXUSR else 0o644)


def manifest_files(stage):
    return {p.relative_to(stage).as_posix():{"sha256":digest(p),"size":p.stat().st_size,
        "mode":stat.S_IMODE(p.stat().st_mode)} for p in sorted(stage.rglob("*")) if p.is_file()
        and p.relative_to(stage).as_posix() not in ("product-manifest.json","SHA256SUMS")}


def zip_tree(stage, output):
    with zipfile.ZipFile(output,"x",compression=zipfile.ZIP_DEFLATED,compresslevel=9) as archive:
        for p in sorted(stage.rglob("*")):
            if not p.is_file():
                continue
            name=stage.name+"/"+p.relative_to(stage).as_posix()
            info=zipfile.ZipInfo(name,(2026,11,18,0,0,0))
            info.create_system=3
            info.external_attr=(stat.S_IFREG|stat.S_IMODE(p.stat().st_mode))<<16
            info.compress_type=zipfile.ZIP_DEFLATED
            archive.writestr(info,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)


def runtime_inputs(artifacts, source, version):
    selected=[]
    seen=set()
    for artifact in artifacts:
        need(artifact.is_file() and not artifact.is_symlink(),"Runtime artifact must be a regular file")
        with zipfile.ZipFile(artifact) as archive:
            matches=[n for n in archive.namelist() if n.endswith("/runtime-manifest.json")]
            need(len(matches)==1,"Expected one runtime descriptor")
            info=archive.getinfo(matches[0]);need(info.file_size<=4*1024*1024,"Oversized runtime descriptor")
            data=json.loads(archive.read(matches[0]))
        need(data["schema"]=="codex-agents.workbench-runtime/1" and data["source_commit"]==source
             and data["product_version"]==version and data["source_clean"],"Runtime does not match the clean buyer source")
        arch=data["platform"]["arch"]
        need(arch not in seen and arch in ("arm64","x64"),"Unknown or duplicate runtime architecture")
        seen.add(arch)
        selected.append({"path":artifact,"name":artifact.name,"sha256":digest(artifact),"size":artifact.stat().st_size,
                         "arch":arch,"signing":data["developer_id_signature"],"notarization":data["notarization"]})
    return selected


def prepare_buyer_stage(root,stage,release,offer,source,edition,runtime=()):
    """One canonical source/doc/license closure for every buyer distribution."""
    version=release["repository_version"]
    if release.get("managed_model"):
        need(release.get("commercial",{}).get("installer_payments_enabled") is False and
             read(root/"commercial/product.json").get("installer_payments_enabled") is False,
             "Managed installer assembly requires payments disabled in the release and product records")
    stage.mkdir()
    for name in ROOTS:
        copy_group(root,stage,name,"product")
    for name in ("assets/marketing/current","assets/marketing/release-1.7","commercial/media"):
        if (root/name).exists():
            copy_group(root,stage,name)
    # Buyer navigation and the unchanged source manual each keep a complete
    # link closure. Source guides live beside their canonical source roots.
    for source_file in paths(root,"docs/commercial"):
        rel=source_file.relative_to(root)
        target=stage/rel
        target.parent.mkdir(parents=True,exist_ok=True)
        content=source_file.read_text(encoding="utf8")
        content=content.replace("](../../", "](../../product/")
        # Single-parent source-manual links need product/docs; already relocated
        # double-parent links must not acquire a second product prefix.
        content=re.sub(r"\]\(\.\./(?!\.\./)", "](../../product/docs/", content)
        target.write_text(content,encoding="utf8")
    for path in paths(root,"commercial/setup"):
        rel=path.relative_to(root/"commercial/setup")
        to=stage/"setup"/rel;to.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(path,to);to.chmod(0o755 if path.stat().st_mode&stat.S_IXUSR else 0o644)
    shutil.copyfile(root/"commercial/legal/LICENSE.txt",stage/"LICENSE.txt")
    shutil.copyfile(root/"commercial/legal/THIRD_PARTY_NOTICES.txt",stage/"THIRD_PARTY_NOTICES.txt")
    shutil.copyfile(root/"commercial/offer.json",stage/"offer.json")
    shutil.copyfile(root/"commercial/product.json",stage/"product.json")
    (stage/"README.md").write_text("# Codex Agent System buyer candidate\n\nOpen [START_HERE.html](START_HERE.html) or [ПОЧАТИ.html](ПОЧАТИ.html), then use Start.command for the guided setup.\n\n[Buyer guide](docs/commercial/BUYER_GUIDE.md) · [Українська](docs/commercial/BUYER_GUIDE.uk.md) · [Complete product documentation](product/docs/INDEX.md) · [Versioned license](LICENSE.txt)\n\nKeep your trusted delivery receipt and entitlement outside this package. This local candidate is not a public sales offer.\n")
    (stage/"START_HERE.md").write_text("# Start here\n\n[Open the buyer start page](START_HERE.html) · [Українська](ПОЧАТИ.html) · [Original advanced manual](product/START_HERE.md)\n")
    for locale,filename in (("en","START_HERE.html"),("uk","ПОЧАТИ.html")):
        origin=root/f"commercial/site/start-{locale}.html"
        need(origin.is_file(),"Buyer landing absent: "+str(origin))
        shutil.copyfile(origin,stage/filename)
    for locale,filename,other in (("en","SALES.html","ПРОДУКТ.html"),("uk","ПРОДУКТ.html","SALES.html")):
        raw=(root/f"commercial/site/sales-{locale}.html").read_text()
        raw=raw.replace("../../assets/","assets/").replace("../../docs/","docs/")
        raw=raw.replace("../legal/LICENSE.txt","LICENSE.txt")
        raw=raw.replace("../media/","commercial/media/")
        raw=raw.replace("sales-uk.html" if locale=="en" else "sales-en.html",other)
        (stage/filename).write_text(raw)
    example=stage/"examples"/"first-task";example.mkdir(parents=True)
    (example/"README.md").write_text("# Cheklist\n\nKeep this note unchanged.\n")
    (example/"notes.txt").write_text("Original buyer work: preserve this file.\n")
    (example/"TASK.txt").write_text("Use the installed Atelier Orchestrator to correct Cheklist to Checklist in README.md. Keep all other bytes and notes.txt intact. Report changed paths and verification.\n")
    launcher="""#!/bin/sh
set -eu
folder=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
if ! command -v python3 >/dev/null 2>&1; then
 echo 'Python 3.9+ is required. Install from https://www.python.org/downloads/ then reopen Start.command.'
 printf 'Press Enter to close. '; read answer; exit 1
fi
exec python3 -B "$folder/setup/setup.py" --package "$folder" "$@"
"""
    (stage/"Start.command").write_text(launcher);(stage/"Start.command").chmod(0o755)
    for item in runtime:
        folder=stage/"runtime";folder.mkdir(exist_ok=True)
        shutil.copyfile(item["path"],folder/item["name"])
        need(digest(folder/item["name"])==item["sha256"],"Runtime changed during staging")
    if runtime:
        (stage/"runtime"/"README.md").write_text("# Included Mac workbench candidates\n\nExtract the archive matching your Mac. Open Launch.command in its extracted folder. These artifacts bundle Node and the built client; no npm build is required. Product signing/notarization and Intel execution remain separate RC gates. [Runtime guide](../docs/commercial/WORKBENCH_RUNTIME.md)\n")
    m={"schema":"codex-agents.commercial-package/1","product_id":PRODUCT,"product_version":version,
       "source_commit":source,"edition":edition,"license_version":offer["license_version"],
       "components":{"core":release["suite_version"],"orchestrator":next(s["version"] for s in release["optional_skills"] if s["name"]=="atelier-orchestrator"),
          "profile":release["host_profile"]["version"],"roles":release["role_profiles"]["version"]},
       "entry_point":"START_HERE.html","recommended_setup":"Start.command",
       "runtime":{"status":"included-architecture-archives" if runtime else "separate-optional-artifact",
                  "artifacts":[{k:v for k,v in item.items() if k!="path"} for item in runtime]},
       "build_trust":"Obtain the separately signed release index and public key through trusted seller delivery.",
       "files":manifest_files(stage)}
    if release.get("managed_model"):
        from managed_release_checks import audit_model_sources, buyer_model_sources
        errors = audit_model_sources(root, buyer_model_sources(stage))
        need(not errors,"Managed model assembly audit failed:\n" + "\n".join(errors))
        m["installer_payments_enabled"] = False
    (stage/"product-manifest.json").write_text(json.dumps(m,indent=2,sort_keys=True)+"\n")
    sums="".join(v["sha256"]+"  "+name+"\n" for name,v in m["files"].items())
    sums+=digest(stage/"product-manifest.json")+"  product-manifest.json\n"
    (stage/"SHA256SUMS").write_text(sums)
    return m


def build(root, output, runtime_artifacts=(), portable_runtime_bundles=()):
    root=root.resolve(strict=True);output=output.resolve()
    need(not output.is_relative_to(root),"Output must be outside source checkout")
    source=capture(root)
    descriptor=read(root/"commercial/product.json");release=read(root/descriptor["release_record"])
    offer=read(root/descriptor["offer"])
    version=release["repository_version"]
    runtime=runtime_inputs(runtime_artifacts,source,version)
    need(release.get("release_stage") in ("candidate","stable"),"This builder requires a declared technical release stage")
    need(descriptor["product_id"]==offer["product_id"]==PRODUCT,"Product scope mismatch")
    output.mkdir(parents=True,exist_ok=True)
    artifacts=[]
    if portable_runtime_bundles:
        need(not runtime_artifacts,"Choose portable ready editions or legacy separate runtime artifacts")
        # Lazy import keeps the shared source-stage implementation acyclic.
        from build_installer import build as build_ready
        for edition in ("solo","team"):
            ready=build_ready(root,output,portable_runtime_bundles,edition=edition)
            artifacts.extend(ready['files'])
    else:
        with tempfile.TemporaryDirectory(prefix="commercial-build-") as work:
            for edition in ("solo","team"):
                stage=Path(work)/f"Agent-System-{version}-{edition}"
                prepare_buyer_stage(root,stage,release,offer,source,edition,runtime)
                dest=output/(stage.name+".zip")
                zip_tree(stage,dest)
                artifacts.append({"name":dest.name,"edition":edition,"sha256":digest(dest),"size":dest.stat().st_size,
                                  "entry_point":"START_HERE.html","product_version":version,"source_commit":source})
    exports=export(root,output,version,source)
    result={"schema":"codex-agents.commercial-build/1","product_id":PRODUCT,"product_version":version,
            "source_commit":source,"status":"technical-distribution-commercial-terms-owner-review","files":artifacts,
            "exports":exports,"publication_performed":False}
    (output/"BUILD.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    (output/"SHA256SUMS").write_text("".join(a["sha256"]+"  "+a["name"]+"\n" for a in artifacts))
    need(capture(root)==source,"Source changed during build")
    return result


def export(root,output,version,source):
    # Two small source-defined coaching exports, not a replacement for local runtime.
    result=[]
    for channel in ("promptbase","agensi"):
        origin=root/"commercial/channels"/channel/"SKILL.md"
        need(origin.is_file(),"Self-contained channel skill is missing")
        raw=origin.read_bytes()
        need(len(raw)<20_000 and b"name:" in raw and b"description:" in raw,"Invalid text-only export")
        folder=output/("exports-"+channel);folder.mkdir()
        shutil.copyfile(origin,folder/"SKILL.md")
        if channel=="agensi":
            dest=output/f"Agent-System-{version}-agensi-demo.zip"
            with zipfile.ZipFile(dest,"x",compression=zipfile.ZIP_DEFLATED) as z:
                info=zipfile.ZipInfo("SKILL.md",(2026,11,18,0,0,0));info.external_attr=(stat.S_IFREG|0o644)<<16
                z.writestr(info,raw)
        else:
            dest=output/f"Agent-System-{version}-promptbase-SKILL.md";dest.write_bytes(raw)
        result.append({"channel":channel,"name":dest.name,"sha256":digest(dest),"size":dest.stat().st_size,
                       "source_commit":source,"scope":"self-contained planning demo; no local runtime or installer",
                       "marketplace_acceptance":"unverified; not submitted"})
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1])
    p.add_argument("--output",type=Path,required=True)
    p.add_argument("--runtime-artifact",type=Path,action="append",default=[],help="Exact clean runtime ZIP from this source; repeat per architecture")
    p.add_argument("--portable-runtime-bundle",type=Path,action="append",default=[],help="One or all six exact native runtime bundles; creates ready Solo/Team editions through the shared installer assembly")
    a=p.parse_args()
    try: print(json.dumps(build(a.root,a.output,a.runtime_artifact,a.portable_runtime_bundle),indent=2));return 0
    except (ValueError,OSError,KeyError,subprocess.SubprocessError) as e:
        print(json.dumps({"status":"blocked","reason":str(e)}),file=sys.stderr);return 2


if __name__=="__main__": sys.exit(main())
