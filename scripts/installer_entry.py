#!/usr/bin/env python3
"""One accessible source/download and extracted-package entry page."""
from __future__ import annotations
import html
import argparse
import json
import re
from pathlib import Path

ASSETS={'Windows x64':'Windows-x64','Windows ARM64':'Windows-arm64','macOS Apple Silicon':'macOS-arm64','macOS Intel':'macOS-x64','Linux x64':'Linux-x64','Linux ARM64':'Linux-arm64'}
LATEST_RELEASE = 'https://github.com/alex-hohaizel/codex-agents/releases/latest'

def public_installer_version(release):
    version = (release.get('previous_stable', {}).get('repository_version')
               if release.get('release_stage') == 'candidate' else release['repository_version'])
    if not isinstance(version, str) or not re.fullmatch(r'\d+\.\d+\.\d+', version):
        raise ValueError('Candidate pages require a verified previous stable installer version')
    return version


def render(version='1.8.0',locale='en',ready=False,*,download_version=None,previous_version=None):
    uk=locale=='uk'; esc=html.escape
    stable=download_version or version
    base=f'https://github.com/alex-hohaizel/codex-agents/releases/download/v{stable}/Agent-System-{stable}-'
    if ready:
        heading='Відкрийте установник для своєї системи' if uk else 'Open the installer for your system'
        steps=('<li><b>Windows:</b> Start.cmd</li><li><b>macOS:</b> Start.command</li><li><b>Linux:</b> Start.sh</li>')
        detail=('Відкрийте відповідний файл у цій самій розпакованій папці. Він запустить локальний майстер у браузері. Якщо система не зберегла дозвіл виконання, дивіться інструкцію нижче.' if uk else 'Open the matching file in this extracted folder. It starts the local browser wizard. If your extractor did not preserve executable permissions, use the documented command below.')
        action=f'<h2>{heading}</h2><ol>{steps}</ol><p>{detail}</p><p class="note">'+('HTML сам по собі не може змінити встановлення. Кнопки перевірки й встановлення з’являться у локальному майстрі після запуску.' if uk else 'This static HTML cannot change your installation. Check and install controls appear in the local wizard after you start the launcher.')+'</p>'
        docs='product/docs/'
    else:
        heading='Завантажте готовий установник' if uk else 'Download the ready installer'
        latest_label = 'Останній опублікований реліз' if uk else 'Latest published release'
        universal_label = 'Універсальний пакет · усі 6 платформ' if uk else 'Universal package · all 6 platforms'
        exact = (f'Пакети v{stable} доступні після публікації відповідного релізу.' if uk
                 else f'The v{stable} packages become available after that release is published.')
        downloads = ''.join(f'<a href="{base}{value}.zip">{esc(label)}</a>' for label,value in ASSETS.items())
        note = ('Source code ZIP — вихідний код. Для встановлення без Python, Node та npm використовуйте готовий пакет. Потрібні окремо Codex та його обліковий запис.' if uk
                else 'Source code ZIP contains development sources. Use a ready package to install without Python, Node or npm setup. Codex and its account remain separate prerequisites.')
        action = (f'<h2>{heading}</h2><a class="primary" href="{LATEST_RELEASE}">{latest_label}</a>'
                  f'<p>{exact}</p><div class="downloads"><a href="{base}Universal.zip">{universal_label}</a>{downloads}</div>'
                  f'<p class="note">{note}</p>')
        if previous_version and previous_version != stable:
            if not re.fullmatch(r'\d+\.\d+\.\d+', previous_version):
                raise ValueError('Invalid previous stable version')
            previous = f'<a href="https://github.com/alex-hohaizel/codex-agents/releases/tag/v{previous_version}">v{previous_version}</a>'
            note = (f'До публікації v{stable} і для відновлення використовуйте {previous}.' if uk
                    else f'Use {previous} until v{stable} is published or to recover the previous version.')
            action += f'<p class="note">{note}</p>'
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

def render_public(release, locale):
    return render(release['repository_version'], locale,
                  download_version=public_installer_version(release),
                  previous_version=release.get('previous_stable', {}).get('repository_version'))

if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    release=json.loads((root/'releases/current.json').read_text())
    for locale,name in [('en','START_HERE.html'),('uk','ПОЧАТИ.html')]:
        expected=render_public(release,locale).encode('utf8');path=root/name
        if args.check:
            if not path.is_file() or path.read_bytes()!=expected:raise SystemExit('Stale root installer entry: '+name)
        else:path.write_bytes(expected)
