#!/usr/bin/env python3
"""Build and verify the canonical English/Ukrainian campaign without changing artwork.

Full PDFs preserve every source RGB pixel. Compact PDFs encode the same full-size
artwork as JPEG for convenient delivery. Each locale HTML embeds its own ten PNGs;
the small entry page opens English by default. No publication or installation.
"""
from __future__ import annotations
import argparse
import base64
from io import BytesIO
import hashlib
import html
import json
from pathlib import Path
import struct
import sys

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[1]
ASSETS=REPO/'assets/marketing/campaign'
OUTPUT=HERE
ARTIFACTS=REPO/'reports/local-campaign-artifacts'
W,H=1600,900
LANGUAGES=('en','uk')


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def load():
    data=json.loads((HERE/'campaign.json').read_text(encoding='utf-8'))
    capabilities=json.loads((HERE/'capabilities.json').read_text(encoding='utf-8'))
    materials=data['materials']
    if len(materials)!=10 or len({x['id'] for x in materials})!=10 or len({x['asset'] for x in materials})!=10:
        raise ValueError('Expected ten unique campaign materials')
    if any(x.get('kind')!='artwork' or Path(x['asset']).name!=x['asset'] for x in materials):
        raise ValueError('Each material must name one complete raster artwork')
    for item in materials:
        if any(not item.get(field,{}).get(lang) for field in ('title','alt') for lang in LANGUAGES):
            raise ValueError('Incomplete bilingual material text: '+item['id'])
    canonical=set(json.loads((REPO/'releases/current.json').read_text())['stable_skill_names'])
    if len(capabilities['skills'])!=33 or {x['name'] for x in capabilities['skills']}!=canonical:
        raise ValueError('Capability directory must match all 33 canonical skills')
    for skill in capabilities['skills']:
        for field in ('title','contribution','outcomes'):
            if any(not skill[field].get(lang) for lang in LANGUAGES):
                raise ValueError('Incomplete bilingual capability: '+skill['name'])
    return data,capabilities


def inspect_assets(data):
    from PIL import Image
    records={};missing=[]
    for lang in LANGUAGES:
        records[lang]={}
        for item in data['materials']:
            name=item['asset'];path=ASSETS/lang/name
            if not path.is_file():missing.append(path.relative_to(REPO).as_posix());continue
            with Image.open(path) as im:im.verify()
            with Image.open(path) as im:width,height=im.size
            if width<1200 or height<675 or not 1.55<=width/height<=1.95:
                raise ValueError('Artwork is not a sufficient widescreen source: '+str(path))
            records[lang][name]={'path':path.relative_to(REPO).as_posix(),'sha256':digest(path),'size':path.stat().st_size,'width':width,'height':height}
    if missing:raise ValueError('Missing campaign artwork: '+', '.join(missing))
    for name,expected in data['uk_source_sha256'].items():
        if records['uk'][name]['sha256']!=expected:raise ValueError('Ukrainian campaign source changed: '+name)
    original=data['original'];record=records['uk']['01-original.png']
    if record['sha256']!=original['sha256'] or (record['width'],record['height'])!=(original['width'],original['height']):
        raise ValueError('Ukrainian recovered original must remain byte-for-byte unchanged')
    for item in data['materials']:
        name=item['asset'];a,b=records['uk'][name],records['en'][name]
        if (a['width'],a['height'])!=(b['width'],b['height']):
            raise ValueError('Localized pair dimensions differ: '+name)
    return records


COPY={
'en':{'skip':'Skip to materials','nav':'Campaign navigation','map':'33 capabilities','full':'Full PDF','compact':'Compact PDF','print':'Print','edition':'ONE CAMPAIGN / TWO LANGUAGES / TEN MATERIALS','intro':'Your idea. Complete products. Specialists for your task.','intro_body':'The same artwork and product stories in English and Ukrainian. Choose a language without changing the campaign direction.','map_kicker':'CAPABILITY MAP / 2 + 11 + 11 + 9','map_title':'33 capabilities. A team for your scope.','map_body':'Open a family to see the contribution and concrete outputs of each specialist. This is a capability map, not a list of completed customer projects.','specialist':'Specialist','contribution':'Contribution','outputs':'Concrete outputs','source':'Canonical source ↗','top':'Back to the first material'},
'uk':{'skip':'Перейти до матеріалів','nav':'Навігація кампанії','map':'33 компетенції','full':'Повний PDF','compact':'Компактний PDF','print':'Друк','edition':'ОДНА КАМПАНІЯ / ДВІ МОВИ / ДЕСЯТЬ МАТЕРІАЛІВ','intro':'Твій задум. Цілі продукти. Спеціалісти під задачу.','intro_body':'Та сама графіка й продуктові історії англійською та українською. Перемикай мову, зберігаючи напрям кампанії.','map_kicker':'КАРТА МОЖЛИВОСТЕЙ / 2 + 11 + 11 + 9','map_title':'33 компетенції. Команда під твій масштаб.','map_body':'Відкрий сімейство, щоб побачити внесок і предметні результати кожного спеціаліста. Це карта можливостей, а не перелік виконаних клієнтських проєктів.','specialist':'Спеціаліст','contribution':'Внесок','outputs':'Предметні результати','source':'Канонічне джерело ↗','top':'До першого матеріалу'}}
CSS=""":root{color-scheme:dark;--bg:#041924;--paper:#fff0cd;--teal:#00d9cf;--muted:#bbccd0}*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:var(--bg);color:var(--paper);font:16px/1.5 system-ui,sans-serif}button,a{touch-action:manipulation}a{color:var(--teal)}.toolbar{position:sticky;top:0;z-index:5;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px 20px;padding:14px 26px;background:#041924f2;border-bottom:1px solid #244552}.mark{font-weight:750;letter-spacing:.045em}.mark:before{content:'／';font-size:27px;color:var(--teal);margin-right:9px}.tools{display:flex;flex-wrap:wrap;gap:8px;align-items:center}.tools a,.tools button{font:inherit;text-decoration:none;color:var(--paper);padding:7px 12px;border:1px solid #43606c;border-radius:5px;background:#0b2b38}.tools a[aria-current=page]{border-color:var(--teal);color:var(--teal)}.skip{position:absolute;left:15px;top:-80px;z-index:10}.skip:focus{top:10px;background:var(--bg);padding:10px}.intro{max-width:1400px;margin:38px auto 26px;padding:0 28px}.intro h1{font:clamp(29px,3.4vw,52px)/1.12 Georgia,serif;max-width:1100px;margin:0 0 16px}.intro p{color:var(--muted);max-width:900px}.counter{color:var(--teal);font-size:13px;letter-spacing:.08em}.gallery{max-width:1672px;margin:auto}.material{margin:0 0 35px;scroll-margin-top:130px}.artwork{display:block;width:100%;height:auto;background:#041924}.caption{display:flex;gap:16px;align-items:baseline;padding:14px 28px;color:var(--muted);font-size:14px}.caption strong{color:var(--paper);font-size:17px}.number{color:var(--teal);white-space:nowrap}.directory{max-width:1400px;margin:65px auto;padding:0 28px}.directory h2{font:42px/1.1 Georgia,serif}.directory>p{color:var(--muted);max-width:950px}.family{border-top:1px solid #375561;padding:18px 0}.family summary{cursor:pointer;font-size:23px}.family table{width:100%;border-collapse:collapse;margin:20px 0 30px;font-size:14px}.family th,.family td{vertical-align:top;text-align:left;padding:13px 15px 13px 0;border-bottom:1px solid #1c3b48}.family th{color:var(--teal);font-weight:500}.family td:first-child{width:29%}.family td code{font-size:12px;overflow-wrap:anywhere;color:var(--muted)}.family ul{padding-left:18px;margin:0}.boundary{border-top:1px solid #375561;padding:28px;color:var(--muted);max-width:1400px;margin:auto;font-size:13px}.back{position:fixed;bottom:20px;right:20px;border:1px solid #43606c;border-radius:999px;padding:9px 14px;background:#062632ed;color:var(--paper);text-decoration:none}:focus-visible{outline:3px solid var(--teal);outline-offset:4px}@media(max-width:850px){.toolbar{padding:10px 14px}.mark{font-size:13px}.tools a,.tools button{font-size:12px;padding:6px 8px}.intro{padding:0 17px;margin-top:27px}.caption{padding:10px 17px;align-items:flex-start}.directory{padding:0 17px}.directory h2{font-size:32px}.family table,.family tbody,.family tr,.family td{display:block}.family thead{display:none}.family td{border:0;padding:7px 0}.family td:first-child{width:auto}.family tr{border-bottom:1px solid #375561;padding:12px 0}.family summary{font-size:20px}.material{scroll-margin-top:180px}}@media print{.toolbar,.intro,.caption,.directory,.boundary,.back{display:none}.material{margin:0;break-after:page}.artwork{width:100%}@page{size:16in 9in;margin:0}}@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}"""


def make_html(data,capabilities,records,lang,embedded=False):
    c=COPY[lang];images={name:'data:image/png;base64,'+base64.b64encode((ASSETS/lang/name).read_bytes()).decode() for name in records[lang]} if embedded else {}
    materials=[]
    for item in data['materials']:
        n,name=item['id'],item['asset'];record=records[lang][name]
        src=images[name] if embedded else '../../assets/marketing/campaign/'+lang+'/'+name
        art=f'<img class="artwork" loading="lazy" decoding="async" src="{src}" data-asset="{name}" alt="{html.escape(item["alt"][lang])}" width="{record["width"]}" height="{record["height"]}">'
        materials.append(f'<section class="material" id="material-{n}" aria-label="{n}. {html.escape(item["title"][lang])}">{art}<div class="caption"><span class="number">{n} / 10</span><strong>{html.escape(item["title"][lang])}</strong></div></section>')
    directory=[]
    for family in capabilities['families']:
        rows=[]
        for skill in capabilities['skills']:
            if skill['family']!=family['id']:continue
            outcomes=''.join('<li>'+html.escape(x)+'</li>' for x in skill['outcomes'][lang]);source='https://github.com/alex-hohaizel/codex-agents/blob/main/'+skill['sources'][0]
            rows.append(f'<tr><td><strong>{html.escape(skill["title"][lang])}</strong><br><code>{html.escape(skill["name"])}</code></td><td>{html.escape(skill["contribution"][lang])}</td><td><ul>{outcomes}</ul><a href="{source}" target="_blank" rel="noreferrer">{c["source"]}</a></td></tr>')
        directory.append(f'<details class="family"><summary>{html.escape(family["name"][lang])} · {family["count"]}</summary><p>{html.escape(family["promise"][lang])}</p><table><thead><tr><th>{c["specialist"]}</th><th>{c["contribution"]}</th><th>{c["outputs"]}</th></tr></thead><tbody>{"".join(rows)}</tbody></table></details>')
    locale_page=lambda code:('Campaign.'+code if embedded else code)+'.html'
    languages=''.join(f'<a data-language="{code}" href="{locale_page(code)}"'+(' aria-current="page"' if code==lang else '')+'>'+label+'</a>' for code,label in [('en','English'),('uk','Українська')])
    downloads=(f'<a href="Campaign.{lang}.full.pdf" download>{c["full"]} ↓</a><a href="Campaign.{lang}.compact.pdf" download>{c["compact"]} ↓</a>' if embedded else f'<a href="pdf/Campaign.{lang}.pdf" download>{c["compact"]} ↓</a>')
    language_prefix='Campaign.' if embedded else ''
    return f'''<!doctype html><html lang="{lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(data['campaign_title'][lang])} · AGENT SYSTEM 5.0</title><style>{CSS}</style></head><body><a class="skip" href="#main">{c['skip']}</a><header class="toolbar"><span class="mark">AGENT SYSTEM 5.0</span><nav class="tools" aria-label="{c['nav']}">{languages}<a href="#competencies">{c['map']}</a>{downloads}<button id="print" type="button">{c['print']}</button></nav></header><div class="intro"><p class="counter">{c['edition']}</p><h1>{c['intro']}</h1><p>{c['intro_body']}</p></div><main class="gallery" id="main">{''.join(materials)}</main><aside class="directory" id="competencies"><p class="counter">{c['map_kicker']}</p><h2>{c['map_title']}</h2><p>{c['map_body']}</p>{''.join(directory)}</aside><footer class="boundary">{html.escape(data['illustration_boundary'][lang])}</footer><a class="back" href="#main" aria-label="{c['top']}">↑</a><script>document.getElementById('print').addEventListener('click',()=>window.print());document.querySelectorAll('[data-language]').forEach(el=>el.addEventListener('click',()=>{{el.href='{language_prefix}'+el.dataset.language+'.html'+location.hash}}));window.campaignReady=true;</script></body></html>'''


def make_index(embedded=False):
    en='Campaign.en.html' if embedded else 'en.html';uk='Campaign.uk.html' if embedded else 'uk.html'
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="refresh" content="0;url={en}"><title>Agent System campaign · English / Українська</title><style>body{{background:#041924;color:#fff0cd;font:20px/1.6 system-ui,sans-serif;max-width:800px;margin:10vh auto;padding:24px}}a{{color:#00d9cf;margin-right:24px}}</style></head><body><h1>Think bigger.</h1><p><a href="{en}">English</a><a href="{uk}">Українська</a></p><p>English opens by default. Each language page preserves the same campaign composition.</p></body></html>'''


def png_idat(image):
    """Encode source RGB pixels with PNG filtering; embed its zlib stream in PDF."""
    buffer=BytesIO();image.convert('RGB').save(buffer,format='PNG',compress_level=9)
    blob=buffer.getvalue();offset=8;parts=[]
    while offset<len(blob):
        size=struct.unpack('>I',blob[offset:offset+4])[0];kind=blob[offset+4:offset+8];data=blob[offset+8:offset+8+size]
        if kind==b'IDAT':parts.append(data)
        offset+=size+12
    if not parts:raise ValueError('PNG encoding produced no image stream')
    return b''.join(parts)


def make_pdf(path,data,lang,compact=False):
    from PIL import Image
    from pypdf import PdfWriter
    from pypdf.generic import BooleanObject,DecodedStreamObject,DictionaryObject,NameObject,NumberObject
    writer=PdfWriter();writer.add_metadata({'/Title':data['campaign_title'][lang]+' · Agent System campaign','/Author':'Agent System','/Subject':'Compact JPEG delivery copy' if compact else 'Lossless complete campaign artwork'})
    placements=[]
    for item in data['materials']:
        source=ASSETS/lang/item['asset']
        with Image.open(source) as original:
            image=original.convert('RGB');iw,ih=image.size
            if compact:
                buffer=BytesIO();image.save(buffer,format='JPEG',quality=95,subsampling=0,optimize=True);encoded=buffer.getvalue();filter_name='/DCTDecode'
            else:encoded=png_idat(image);filter_name='/FlateDecode'
        image_obj=DecodedStreamObject();image_obj.set_data(encoded)
        image_obj.update({NameObject('/Type'):NameObject('/XObject'),NameObject('/Subtype'):NameObject('/Image'),NameObject('/Width'):NumberObject(iw),NameObject('/Height'):NumberObject(ih),NameObject('/ColorSpace'):NameObject('/DeviceRGB'),NameObject('/BitsPerComponent'):NumberObject(8),NameObject('/Filter'):NameObject(filter_name),NameObject('/Interpolate'):BooleanObject(False)})
        if not compact:image_obj[NameObject('/DecodeParms')]=DictionaryObject({NameObject('/Predictor'):NumberObject(15),NameObject('/Colors'):NumberObject(3),NameObject('/BitsPerComponent'):NumberObject(8),NameObject('/Columns'):NumberObject(iw)})
        image_ref=writer._add_object(image_obj)
        page=writer.add_blank_page(width=W,height=H);scale=min(W/iw,H/ih);dw,dh=iw*scale,ih*scale;x,y=(W-dw)/2,(H-dh)/2
        content=DecodedStreamObject();content.set_data(f'q\n0.015686 0.098039 0.141176 rg\n0 0 {W} {H} re f\n{dw:.8f} 0 0 {dh:.8f} {x:.8f} {y:.8f} cm\n/Artwork Do\nQ\n'.encode())
        page[NameObject('/Resources')]=DictionaryObject({NameObject('/XObject'):DictionaryObject({NameObject('/Artwork'):image_ref})})
        page[NameObject('/Contents')]=writer._add_object(content)
        placements.append({'page':int(item['id']),'asset':item['asset'],'whole_image':True,'crop':False,'placement_points':[x,y,dw,dh]})
    with path.open('wb') as stream:writer.write(stream)
    return placements


def validate_source():
    data,capabilities=load();records=inspect_assets(data)
    translations=json.loads((HERE/'translations.json').read_text())
    if digest(HERE/translations['source'])!=translations['source_sha256']:raise ValueError('English campaign README hash is stale')
    for entry in translations['translations']:
        if digest(HERE/entry['path'])!=entry['sha256']:raise ValueError('Campaign translation hash is stale: '+entry['path'])
    for doc in translations.get('documents',[]):
        if digest(HERE/doc['source'])!=doc['source_sha256'] or digest(HERE/doc['translation'])!=doc['translation_sha256']:raise ValueError('Campaign provenance translation hash is stale')
    return data,capabilities,records


def check_pdf(path,data,lang,lossless=False):
    from PIL import Image
    from pypdf import PdfReader
    reader=PdfReader(path)
    if len(reader.pages)!=10:raise ValueError('Expected ten PDF pages: '+path.name)
    for pdf_page,item in zip(reader.pages,data['materials']):
        if len(pdf_page.images)!=1:raise ValueError('Expected one full artwork per PDF page')
        artwork=pdf_page.images[0].image
        with Image.open(ASSETS/lang/item['asset']) as original:
            if artwork.size!=original.size:raise ValueError('PDF changed source dimensions')
            if lossless and artwork.convert('RGB').tobytes()!=original.convert('RGB').tobytes():raise ValueError('Lossless PDF altered source pixels: '+lang+'/'+item['asset'])


def check_receipt(directory,records):
    receipt=json.loads((directory/'exports.json').read_text())
    expected=({'index.html','en.html','uk.html','pdf/Campaign.en.pdf','pdf/Campaign.uk.pdf'} if receipt.get('kind')=='repository-relative-galleries-and-compact-pdfs' else {'index.html',*[f'Campaign.{lang}.{suffix}' for lang in LANGUAGES for suffix in ('full.pdf','compact.pdf','html')]})
    if len(receipt.get('files',[]))!=len(expected) or {x.get('path') for x in receipt['files']}!=expected:raise ValueError('Export receipt has an incomplete or unexpected file set')
    for entry in receipt['files']:
        path=directory/entry['path']
        if not path.resolve().is_relative_to(directory.resolve()):raise ValueError('Export receipt path leaves its directory')
        if not path.is_file() or digest(path)!=entry['sha256'] or path.stat().st_size!=entry['size']:raise ValueError('Export receipt mismatch: '+entry['path'])
    if receipt['artworks']!=records:raise ValueError('Source artwork receipt is stale')
    return receipt


def validate(output=OUTPUT,artifacts_output=ARTIFACTS,require_artifacts=False):
    import re
    data,capabilities,records=validate_source()
    if (output/'index.html').read_text()!=make_index():raise ValueError('English-default entry page is stale')
    for lang in LANGUAGES:
        page=(output/f'{lang}.html').read_text()
        if page!=make_html(data,capabilities,records,lang):raise ValueError('Localized HTML is stale: '+lang)
        if len(re.findall(r'<section class="material"',page))!=10 or len(re.findall(r'<code>',page))!=33:raise ValueError('Localized HTML lacks complete materials/capabilities: '+lang)
        if '<script src=' in page or '<link ' in page:raise ValueError('Localized HTML loads external executable/style assets')
        check_pdf(output/f'pdf/Campaign.{lang}.pdf',data,lang)
    check_receipt(output,records)
    private_checked=bool(artifacts_output and (artifacts_output/'exports.json').exists())
    if require_artifacts and not private_checked:raise ValueError('Required private artifact receipt is missing')
    if private_checked:
        for lang in LANGUAGES:
            if (artifacts_output/f'Campaign.{lang}.html').read_text()!=make_html(data,capabilities,records,lang,embedded=True):raise ValueError('Self-contained locale HTML is stale: '+lang)
            check_pdf(artifacts_output/f'Campaign.{lang}.full.pdf',data,lang,lossless=True)
            check_pdf(artifacts_output/f'Campaign.{lang}.compact.pdf',data,lang)
        check_receipt(artifacts_output,records)
    return {'ok':True,'languages':list(LANGUAGES),'materials_per_language':10,'artwork_pairs':10,'pdf_pages_per_file':10,'lossless_pdf_source_pixels_match':True if private_checked else 'not-checked-no-private-artifacts','localized_pair_dimensions_match':True,'all_ten_uk_source_hashes_preserved':True,'capabilities':33,'browser_layout_verified':False,'language_pair_pixel_identity_claimed':False}


def write_receipt(directory,files,data,records,placements,kind):
    receipt={'schema':'codex-agents.bilingual-campaign-export/1','kind':kind,'suite_version':data['suite_version'],'languages':list(LANGUAGES),'materials_per_language':10,'all_ten_uk_source_hashes_preserved':True,'original_uk_sha256':data['original']['sha256'],'artworks':records,'files':[{'path':p.relative_to(directory).as_posix(),'sha256':digest(p),'size':p.stat().st_size} for p in files],'pdf_image_placements':placements,'compact_encoding':'Full-resolution JPEG quality95 4:4:4; separate delivery copy, not canonical source pixels','language_pair_pixel_identity_claimed':False,'publication_performed':False,'browser_layout_verified':False}
    (directory/'exports.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')


def build(output,artifacts_output=ARTIFACTS):
    import shutil
    if artifacts_output:
        protected=('kit','assets','docs','marketing','governance','releases','scripts','templates','maintenance-skill')
        if any(artifacts_output.resolve().is_relative_to((REPO/name).resolve()) for name in protected):raise ValueError('Keep private campaign artifacts outside reusable source roots, for example reports/local-campaign-artifacts')
    data,capabilities,records=validate_source();output.mkdir(parents=True,exist_ok=True);(output/'pdf').mkdir(exist_ok=True);files=[];placements={}
    for lang in LANGUAGES:
        pdf=output/f'pdf/Campaign.{lang}.pdf';placements[pdf.relative_to(output).as_posix()]=make_pdf(pdf,data,lang,compact=True);files.append(pdf)
        page=output/f'{lang}.html';page.write_text(make_html(data,capabilities,records,lang),encoding='utf-8');files.append(page)
    index=output/'index.html';index.write_text(make_index(),encoding='utf-8');files.append(index)
    write_receipt(output,files,data,records,placements,'repository-relative-galleries-and-compact-pdfs')
    if artifacts_output:
        artifacts_output.mkdir(parents=True,exist_ok=True);private=[];boxes={}
        for lang in LANGUAGES:
            full=artifacts_output/f'Campaign.{lang}.full.pdf';boxes[full.name]=make_pdf(full,data,lang,compact=False);private.append(full)
            compact=artifacts_output/f'Campaign.{lang}.compact.pdf';shutil.copyfile(output/f'pdf/Campaign.{lang}.pdf',compact);private.append(compact)
            page=artifacts_output/f'Campaign.{lang}.html';page.write_text(make_html(data,capabilities,records,lang,embedded=True),encoding='utf-8');private.append(page)
        entry=artifacts_output/'index.html';entry.write_text(make_index(embedded=True),encoding='utf-8');private.append(entry)
        write_receipt(artifacts_output,private,data,records,boxes,'private-full-pdfs-and-self-contained-delivery')
    return validate(output,artifacts_output,require_artifacts=bool(artifacts_output))


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',type=Path,default=OUTPUT);parser.add_argument('--artifacts-output',type=Path,default=ARTIFACTS);parser.add_argument('--check-assets','--check-source',action='store_true');parser.add_argument('--check',action='store_true');args=parser.parse_args()
    try:
        if args.check_assets:
            data,_,records=validate_source();result={'ok':True,'languages':list(LANGUAGES),'artworks':sum(map(len,records.values())),'localized_pairs':10,'all_ten_uk_source_hashes_preserved':True,'original_uk_sha256':data['original']['sha256']}
        elif args.check:result=validate(args.output.resolve(),args.artifacts_output.resolve(),require_artifacts=any(a=='--artifacts-output' or a.startswith('--artifacts-output=') for a in sys.argv))
        else:result=build(args.output.resolve(),args.artifacts_output.resolve())
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0
    except (OSError,ValueError,KeyError,IndexError) as exc:
        print(json.dumps({'ok':False,'error':str(exc)},ensure_ascii=False,indent=2),file=sys.stderr);return 1

if __name__=='__main__':raise SystemExit(main())
