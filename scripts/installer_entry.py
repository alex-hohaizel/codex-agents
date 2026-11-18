#!/usr/bin/env python3
"""One accessible source/download and extracted-package entry page."""
from __future__ import annotations
import html
import argparse
import json
from pathlib import Path

ASSETS={'Windows x64':'Windows-x64','Windows ARM64':'Windows-arm64','macOS Apple Silicon':'macOS-arm64','macOS Intel':'macOS-x64','Linux x64':'Linux-x64','Linux ARM64':'Linux-arm64'}

def render(version='1.8.0',locale='en',ready=False):
    uk=locale=='uk'; esc=html.escape
    base=f'https://github.com/alex-hohaizel/codex-agents/releases/download/v{version}/Agent-System-{version}-'
    if ready:
        heading='Відкрийте установник для своєї системи' if uk else 'Open the installer for your system'
        steps=('<li><b>Windows:</b> Start.cmd</li><li><b>macOS:</b> Start.command</li><li><b>Linux:</b> Start.sh</li>')
        detail=('Відкрийте відповідний файл у цій самій розпакованій папці. Він запустить локальний майстер у браузері. Якщо система не зберегла дозвіл виконання, дивіться інструкцію нижче.' if uk else 'Open the matching file in this extracted folder. It starts the local browser wizard. If your extractor did not preserve executable permissions, use the documented command below.')
        action=f'<h2>{heading}</h2><ol>{steps}</ol><p>{detail}</p><p class="note">'+('HTML сам по собі не може змінити встановлення. Кнопки перевірки й встановлення з’являться у локальному майстрі після запуску.' if uk else 'This static HTML cannot change your installation. Check and install controls appear in the local wizard after you start the launcher.')+'</p>'
        docs='product/docs/'
    else:
        heading='Завантажте готовий установник' if uk else 'Download the ready installer'
        action=f'<h2>{heading}</h2><a class="primary" href="{base}Universal.zip">'+('Універсальний пакет · усі 6 платформ' if uk else 'Universal package · all 6 platforms')+'</a><p>'+('Або менший пакет саме для вашого комп’ютера:' if uk else 'Or a smaller package for your computer:')+'</p><div class="downloads">'+''.join(f'<a href="{base}{value}.zip">{esc(label)}</a>' for label,value in ASSETS.items())+'</div><p class="note">'+('Source code ZIP — вихідний код. Для встановлення без Python, Node та npm використовуйте готовий пакет вище. Потрібні окремо Codex та його обліковий запис.' if uk else 'Source code ZIP contains development sources. For installation without Python, Node or npm setup, use a ready package above. Codex and its account remain separate prerequisites.')+'</p>'
        docs='docs/'


    # Keep the complete accepted product presentation: illustrations, original
    # screenshots, workflow cards, FAQ and demo. The installer panel augments it.
    template=(Path(__file__).resolve().parents[1]/('commercial/site/start-'+locale+'.html')).read_text(encoding='utf8')
    template=template.replace('1.8.0-rc.1',version)
    template=template.replace('href="Start.command"','href="#universal-setup"')
    template=template.replace('href="#platform-launchers"','href="#universal-setup"')
    template=template.replace('href="https://github.com/alex-hohaizel/codex-agents/blob/main/docs/INDEX.md"',f'href="{docs}INDEX.md"')
    template=template.replace('href="https://github.com/alex-hohaizel/codex-agents/blob/main/docs/uk/GUIDE.md"',f'href="{docs}uk/GUIDE.md"')
    if not ready:
        template=template.replace('href="LICENSE.txt"','href="commercial/legal/LICENSE.txt"')
    panel=f'<section id="universal-setup" class="card"><p class="eyebrow">WINDOWS · macOS · LINUX / x64 + ARM64</p>{action}<nav><a href="{docs}INSTALL.md">'+('Встановлення покроково' if uk else 'Step-by-step installation')+f'</a> · <a href="{docs}INDEX.md">'+('Уся документація' if uk else 'All documentation')+'</a></nav></section>'
    at=template.find('<h2>')
    if at<0:at=template.find('</main>')
    template=template[:at]+panel+template[at:]
    extra='<style>.downloads{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:10px}.downloads a{display:block;padding:12px;border:1px solid #345866;border-radius:8px}.primary{display:inline-block;background:#5be1d3;color:#07252c;padding:14px 20px;border-radius:8px;font-weight:800;text-decoration:none}.note{font-size:14px;color:#bad5dc}#universal-setup{margin-top:32px;scroll-margin-top:24px}</style>'
    return template.replace('</style>', '</style>'+extra,1)

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    version=json.loads((root/'releases/current.json').read_text())['repository_version']
    for locale,name in [('en','START_HERE.html'),('uk','ПОЧАТИ.html')]:
        expected=render(version,locale).encode('utf8');path=root/name
        if args.check:
            if not path.is_file() or path.read_bytes()!=expected:raise SystemExit('Stale root installer entry: '+name)
        else:path.write_bytes(expected)
