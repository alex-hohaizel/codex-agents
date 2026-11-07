#!/usr/bin/env python3
"""Freeze/check existing icon identity; create a project SVG only when absent.

Python3.9+ standard library. No installation, UI rewriting or network access.
Supports JSON UI and conservative block YAML; unknown syntax is a conflict.
"""
import argparse
import hashlib
import html
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat

FIELDS = ('icon_small', 'icon_large', 'brand_color')
SUFFIXES = {'.svg', '.png', '.webp', '.jpg', '.jpeg', '.gif', '.ico'}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def safe_root(value):
    p = Path(os.path.abspath(value))
    for part in [*reversed(p.parents), p]:
        require(not part.is_symlink(), 'symlink path: ' + str(part))
    require(p.is_dir(), 'skill root must exist')
    return p


def asset(root, rel):
    require(isinstance(rel, str) and rel, 'nonempty icon path required')
    normalized = rel[2:] if rel.startswith('./') else rel
    pp = PurePosixPath(normalized)
    require(not pp.is_absolute() and '..' not in pp.parts and '\\' not in rel and ':' not in rel,
            'unsafe icon path')
    require(pp.as_posix() == normalized and pp.parts[0] == 'assets' and pp.suffix.lower() in SUFFIXES,
            'icon must be a canonical image path under assets/')
    p = root.joinpath(*pp.parts)
    for i in range(1, len(pp.parts) + 1):
        require(not root.joinpath(*pp.parts[:i]).is_symlink(), 'linked icon path')
    require(p.is_file() and stat.S_ISREG(p.stat().st_mode), 'missing/irregular icon: ' + rel)
    require(p.stat().st_size <= 8 * 1024 * 1024, 'icon exceeds8MiB')
    return p


def interface(root):
    p = root / 'agents/openai.yaml'
    require(not p.is_symlink() and not p.parent.is_symlink(), 'linked UI metadata')
    if not p.exists():
        return {}
    require(p.is_file() and p.stat().st_size <= 1024 * 1024, 'invalid UI metadata')
    text = p.read_text(encoding='utf-8')
    def unique(pairs):
        d = {}
        for k, value in pairs:
            require(k not in d, 'duplicate UI key')
            d[k] = value
        return d
    if text.lstrip().startswith('{'):
        data = json.loads(text, object_pairs_hook=unique)
        require(isinstance(data,dict) and isinstance(data.get('interface', {}), dict), 'interface must be mapping')
        return {k: data['interface'][k] for k in FIELDS if k in data.get('interface', {})}
    require('\t' not in text, 'tabbed YAML is unsupported; parse actual UI first')
    key_pattern = re.compile(r"(?:([A-Za-z_][A-Za-z0-9_-]*)|(\"(?:[^\"\\]|\\.)*\")|('(?:[^']|'')*'))\s*:\s*(.*)")
    def pair(line):
        match = key_pattern.fullmatch(line)
        require(match is not None, 'unsupported YAML mapping key; preserve by explicit parser')
        raw, double, single, value = match.groups()
        key = raw if raw is not None else json.loads(double) if double is not None else single[1:-1].replace("''", "'")
        return key, value
    lines=text.splitlines(); blocks=[]; roots=set()
    for i,line in enumerate(lines):
        if not line.strip() or line.lstrip().startswith('#') or line in ('---','...') or line.startswith(' '):
            continue
        key,value=pair(line)
        require(key not in roots,'duplicate top-level UI key');roots.add(key)
        if key=='interface':
            require(not value or value.startswith('#'),'flow/complex interface YAML unsupported')
            blocks.append(i)
    if not blocks:
        return {}
    out={};seen=set()
    for line in lines[blocks[0]+1:]:
        if line.strip() and not line.startswith(' ') and not line.lstrip().startswith('#'):
            break
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        require(line.startswith('  '),'unsupported interface indentation')
        if line.startswith('   '):
            continue
        key,value=pair(line[2:]);require(key not in seen,'duplicate interface key');seen.add(key)
        if key not in FIELDS:
            continue
        require(bool(value) and value[0] not in '&*!|>{[', 'complex icon value unsupported')
        if value.startswith('"'):
            value=json.loads(value)
        elif value.startswith("'"):
            require(value.endswith("'"), 'invalid quoted icon value')
            value=value[1:-1].replace("''", "'")
        else:
            value=value.split(' #',1)[0].strip()
        require(isinstance(value,str) and bool(value),'invalid visual scalar')
        if key=='brand_color':
            require(re.fullmatch(r'#[0-9A-Fa-f]{6}',value) is not None,'unsupported brand color')
        out[key]=value
    return out


def freeze(root, kind):
    ui=interface(root); files={}
    for key in ('icon_small','icon_large'):
        if key in ui:
            p=asset(root,ui[key]); files[p.relative_to(root).as_posix()]=hashlib.sha256(p.read_bytes()).hexdigest()
    return {'schema':'visual-identity/1','class':kind,'interface':ui,'files':files,'regenerate_on_update':False}


def create(root,glyph):
    ui=interface(root)
    if any(k in ui for k in ('icon_small','icon_large')):
        return {'status':'preserved','snapshot':freeze(root,'project')}
    p=root/'assets/icon.svg'
    require(not p.exists() and not p.is_symlink(), 'existing icon file must be reconciled; never overwrite')
    require(re.fullmatch(r'[A-Za-z0-9]{1,3}',glyph) is not None,'glyph must be1–3alphanumeric characters chosen for purpose')
    require(not p.parent.is_symlink(), 'linked assets directory')
    p.parent.mkdir(exist_ok=True)
    svg='<svg xmlns="http://www.w3.org/2000/svg" width="96" height="96" viewBox="0 0 96 96"><metadata>agent-style:project-card-v1</metadata><polygon points="4,4 72,4 92,24 92,92 4,92" fill="#F8FAFC" stroke="#0F766E" stroke-width="5"/><path d="M72 4V24H92" fill="none" stroke="#0F766E" stroke-width="3"/><text x="48" y="55" text-anchor="middle" font-family="sans-serif" font-weight="700" font-size="30" fill="#0F172A">'+html.escape(glyph.upper())+'</text><rect x="6" y="68" width="84" height="22" fill="#0F766E"/><text x="48" y="85" text-anchor="middle" font-family="sans-serif" font-size="11" font-weight="700" fill="#FFFFFF">PROJECT</text></svg>\n'
    fd=os.open(p,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_NOFOLLOW',0),0o644)
    with os.fdopen(fd,'w',encoding='utf-8') as f:f.write(svg)
    return {'status':'created','class':'project','style':'project-card-v1','path':'assets/icon.svg','sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'next':'Bind interface.icon_small and icon_large to assets/icon.svg, inspect readability, then freeze.'}


def main():
    p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True)
    for name in ('freeze','check','create-project'):
        q=sub.add_parser(name);q.add_argument('--root',required=True)
        if name=='freeze':q.add_argument('--class',dest='kind',choices=('system','project'),required=True)
        if name=='check':q.add_argument('--lock',type=Path,required=True)
        if name=='create-project':q.add_argument('--glyph',required=True)
    a=p.parse_args()
    try:
        root=safe_root(a.root)
        if a.command=='create-project':out=create(root,a.glyph)
        elif a.command=='freeze':out=freeze(root,a.kind)
        else:
            require(not a.lock.is_symlink(),'linked snapshot');old=json.loads(a.lock.read_text())
            require(old.get('schema')=='visual-identity/1' and old.get('class') in ('system','project'),'unsupported snapshot')
            current=freeze(root,old['class']);require(current==old,'visual identity changed')
            out={'valid':True,'identity_preserved':True,'snapshot':current}
        print(json.dumps(out,ensure_ascii=False,indent=2));return 0
    except (ValueError,OSError,KeyError,TypeError) as e:
        print(json.dumps({'valid':False,'error':str(e)},ensure_ascii=False));return 2


if __name__=='__main__':raise SystemExit(main())
