#!/usr/bin/env python3
"""Render EN/UK local buyer and sales pages from the versioned offer."""
import argparse
import html,json
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OFFER=json.loads((ROOT/'commercial/offer.json').read_text())
RELEASE=json.loads((ROOT/'releases/current.json').read_text())
STYLE="""*{box-sizing:border-box}body{margin:0;background:#081b24;color:#e6f6f6;font:17px/1.55 system-ui,-apple-system,sans-serif}main{width:min(1080px,100%);margin:auto;padding:clamp(20px,5vw,64px)}a{color:#64e1d7;text-underline-offset:4px}a:focus-visible,button:focus-visible{outline:3px solid #ffd17a;outline-offset:4px}.top{display:flex;gap:14px;justify-content:space-between;border-bottom:1px solid #325362;padding-bottom:16px;font-weight:700}.eyebrow{font:700 12px/1.5 ui-monospace,monospace;letter-spacing:2px;color:#80d5d1;margin-top:44px}h1{font-size:clamp(38px,7vw,76px);line-height:1.03;letter-spacing:-2px;max-width:14ch;margin:15px 0 24px}h2{font-size:30px;line-height:1.15;margin:48px 0 18px}.lede{font-size:21px;max-width:62ch;color:#bad5dc}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(280px,100%),1fr));gap:16px}.card{padding:24px;border:1px solid #345866;border-radius:15px;background:#112e39}.card h3{margin:0 0 10px}.cta{display:inline-block;color:#07252c;background:#5be1d3;padding:12px 20px;text-decoration:none;border-radius:7px;font-weight:800;margin:10px 10px 10px 0}p,li{max-width:70ch}pre{padding:18px;background:#06121a;border:1px solid #355966;border-radius:8px;overflow:auto;font:13px/1.6 ui-monospace,monospace}code{font:14px/1.4 ui-monospace,monospace}img{width:100%;height:auto;border-radius:14px}.price{font-size:42px;font-weight:800}.muted{color:#a8c3cb;font-size:14px}.banner{border-left:4px solid #ffcc80;padding:16px 20px;background:#2a2d2c;color:#ffe3b4}.steps{counter-reset:step;list-style:none;padding:0}.steps li{counter-increment:step;margin:16px 0;padding:18px 18px 18px 60px;background:#112e39;position:relative;border-radius:8px}.steps li:before{content:counter(step,decimal-leading-zero);position:absolute;left:16px;color:#5be1d3;font-weight:800}.foot{border-top:1px solid #325362;padding-top:18px;margin-top:40px}.plans li{font-size:15px}details{padding:16px 0;border-bottom:1px solid #325362}summary{cursor:pointer;font-weight:750}.workflow{max-width:700px;margin:30px auto}.provenance{overflow-wrap:anywhere}"""
T={'en': {'tag': 'AI TEAM · BUILT FOR CODEX',
        'hero': 'One goal. A complete way to deliver.',
        'intro': 'Plan the work. Bring in the right specialists. Check the result. Pick up where you left off — with '
                 'sources, decisions and recovery in one local toolkit.',
        'candidate': 'Ready technical toolkit for Windows, macOS and Linux. Commercial terms remain a release '
                     'candidate. Payments are disabled for this release. Remaining legal seller facts, support hours and public '
                     'sales approval are still required.',
        'start': 'Open your buyer package',
        'more': 'Read the full product guide',
        'setup': 'Get to your first useful result',
        'steps': ['Download the ready Universal or matching OS/CPU asset from the official Release and extract it '
                  'completely. For authorized commercial delivery, also retain the purchase document and trusted '
                  'signature receipt.',
                  'Read START_HERE.html. Open Start.cmd on Windows, Start.command on macOS, or Start.sh on Linux. The '
                  'local browser wizard checks Codex, shows components and target folders, and reports conflicts. '
                  'Python, Node and the built interface are included in ready assets.',
                  'Prepare and review the audit, approve the exact plan, install and verify the files. Keep the '
                  'journal and check fresh native Codex discovery separately. Installed roles and actual model '
                  'execution have their own evidence.',
                  'Create a practice project in the wizard, open its folder and Codex, and copy the supplied prompt '
                  'into that session. Ask Orchestrator to fix the heading and preserve notes.txt. Verify both files. '
                  'The manual examples/first-task route remains available; the wizard does not execute a model.'],
        'includes': 'One connected toolkit',
        'cards': [('Clarify & decide',
                   'Workshop, brief, PRFAQ and 18 editable templates; keep open decisions and reviews tied to their '
                   'exact sources.'),
                  ('Design & build',
                   'Source-bound UX walkthroughs, product and architecture contracts, App/ChatBot/Game families and '
                   'two reusable constructors.'),
                  ('Coordinate & recover',
                   'Separate Git worktrees, scope, checkpoints and known update journals. Reconcile unknown provider '
                   'effects.'),
                  ('Check & hand off',
                   'Independent reviewer assignments, candidate evidence and exact next action for the next person.')],
        'plans': 'One-time purchase. Your acquired major stays yours.',
        'edition': 'Draft offer in USD. Same major updates included. Next major is a separate offer. Buyer uses their '
                   'own model and API accounts.',
        'faq': 'Before you start',
        'faqrows': [('Is a Codex subscription included?',
                     'No. Use your own supported Codex account. Model usage, APIs, hosting and other services may have '
                     'separate fees.'),
                    ('What runs locally?',
                     '33 core skills, Orchestrator, profile and twelve roles. Ready Windows/macOS/Linux packages '
                     'include Python, Node and the built workbench; no separate Python, Node, npm or TypeScript setup '
                     'is required for this route. Source and advanced build routes remain available.'),
                    ('What is actually supported?',
                     'Ready assets target six OS/CPU combinations, with separate native CI checks defined for each. '
                     'Those checks remain unverified until the exact Release has passing jobs and receipts. One local '
                     'run or a workflow file alone does not prove all targets tested. Graphical interaction, minimum '
                     'OS versions, product signing/notarization, model tasks and sales approval have separate scopes.'),
                    ('Can I use outputs commercially?',
                     'Yes, under the edition and lawful source rights. Original toolkit resources copied into '
                     'generated agents retain their terms. The whole package is not granted for resale.'),
                    ('What happens if the store is offline?',
                     'Keep your acquired version, license document, package and backups. An unavailable store does not '
                     'disable local rights or modify your projects.'),
                    ('How do I get help or a refund?',
                     'The owner-provided support/privacy contact is {seller_name}: {support_contact}. Documentation '
                     'and reproducible package bug help are included; no response SLA is promised. The working '
                     'channel, support hours, remaining seller facts and refund terms must be confirmed before sale.')],
        'trust': 'Verification and recovery',
        'draft': 'Technical distribution · factual checks precede public claims',
        'license': 'License & support',
        'docs': 'Installation and recovery',
        'first': 'First task',
        'locale': 'Українська',
        'launcher_start': 'Choose my system launcher',
        'trust_body': 'Keep the original package and exact setup journal. After interruption, refresh the wizard '
                      'history and select the checked operation for resume, rollback or uninstall. Verify the source '
                      'and read back unknown outcomes before retrying. Workbench data has separate backups and schema '
                      'checks.',
        'demo_body': 'Real workbench screenshots with isolated test data. The video records actual setup, discovery '
                     'and the first task in a labeled test viewer; the viewer is demonstration instrumentation, not '
                     'the product interface. That recording belongs to its candidate environment and does not replace '
                     'acceptance of the new wizard or all six native targets.',
        'platform_title': 'One installer. Your system.',
        'platform_intro': 'The ready Universal archive carries six targets: x64 and ARM64 for Windows, macOS and '
                          'Linux. Smaller platform-specific assets are also available. Static HTML cannot install '
                          'files by itself: use the matching launcher below to start the local browser wizard. Codex '
                          'and your own account remain separate prerequisites.',
        'platform_note': 'The wizard offers English and Ukrainian. Existing project Python/venv and Node retain '
                         'priority; toolkit helpers use the exact AGENT_SYSTEM_PYTHON. No global PATH or registry is '
                         'changed. Maintenance remains a separate owner tool.',
        'platform_docs': 'Step-by-step installation and recovery',
        'screens_caption': 'Earlier workbench screenshots · Agent Atelier 0.7.0 · '
                           'source 87dd0001149d214722b59b9d16793337fae5c01e. Real prebuilt runtime with isolated '
                           'fixture data; these are not screenshots of the new installer.',
        'video_caption': 'Earlier installation and first-result recording · '
                         'source a930d902ba9ab2512cca867a34be33a4ea100e67 · Apple M1/macOS27.0.1, Python3.13 and '
                         'authenticated Codex0.166.0. The labeled process viewer is demonstration instrumentation; '
                         'this recording does not show the new browser wizard.',
        'provenance': 'Exact recording provenance',
        'screens_provenance': 'Exact screenshot provenance'},
 'uk': {'tag': 'AI-КОМАНДА · СУМІСНА З CODEX',
        'hero': 'Одна мета. Цілісний шлях до результату.',
        'intro': 'Сплануйте роботу. Залучіть потрібних спеціалістів. Перевірте результат. Продовжуйте з того самого '
                 'місця — зі джерелами, рішеннями й відновленням в одному локальному комплекті.',
        'candidate': 'Готовий технічний комплект для Windows, macOS і Linux. Комерційні умови залишаються release '
                     'candidate. Оплату для цього релізу вимкнено. Решта юридичних реквізитів продавця, години підтримки '
                     'й дозвіл на публічні продажі ще потрібні.',
        'start': 'Відкрити покупецький комплект',
        'more': 'Повний посібник продукту',
        'setup': 'До першого корисного результату',
        'steps': ['Завантажте готовий Universal або пакет своєї ОС та CPU з офіційного Release й повністю розпакуйте '
                  'його. Для дозволеної комерційної доставки збережіть документ придбання та довірену квитанцію '
                  'підпису.',
                  'Прочитайте ПОЧАТИ.html. Відкрийте Start.cmd у Windows, Start.command у macOS або Start.sh у Linux: '
                  'локальний майстер перевіряє Codex, показує компоненти, папки й конфлікти. Python, Node та зібраний '
                  'інтерфейс уже в готовому пакеті.',
                  'Підготуйте й перегляньте аудит, погодьте точний план, установіть та звірте файли. Збережіть журнал '
                  'і окремо перевірте виявлення у свіжому Codex; встановлені ролі та їх модельне виконання мають '
                  'власні докази.',
                  'Створіть пробний проєкт у майстрі, відкрийте його папку та Codex і скопіюйте запропонований запит у '
                  'цю сесію. Попросіть Orchestrator виправити заголовок і зберегти notes.txt. Перевірте обидва файли. '
                  'Ручний шлях examples/first-task також збережено; майстер не виконує модель самостійно.'],
        'includes': 'Один пов’язаний комплект',
        'cards': [('Уточнюйте й вирішуйте',
                   'Воркшоп, бриф, PRFAQ та 18 редагованих шаблонів; відкриті рішення й огляди прив’язані до точних '
                   'джерел.'),
                  ('Проєктуйте й будуйте',
                   'UX-маршрут із першоджерелами, продуктові й архітектурні контракти, сімейства App/ChatBot/Game і '
                   'два конструктори.'),
                  ('Координуйте й відновлюйте',
                   'Окремі Git worktree, обсяг, контрольні точки й журнали оновлення. Перечитування невизначених '
                   'зовнішніх дій.'),
                  ('Перевіряйте й передавайте',
                   'Окремі завдання для незалежної перевірки, докази кандидата й точний наступний крок для іншої '
                   'людини.')],
        'plans': 'Разова покупка. Придбана major-версія залишається вашою.',
        'edition': 'Робоча пропозиція в USD. Оновлення тієї самої major включені; наступна major — окрема пропозиція. '
                   'Моделі й API використовують акаунти покупця.',
        'faq': 'Перед початком',
        'faqrows': [('Підписка Codex включена?',
                     'Ні. Потрібен ваш сумісний акаунт Codex. Використання моделей, API, хостинг та сторонні сервіси '
                     'можуть оплачуватися окремо.'),
                    ('Що працює локально?',
                     '33 основні навички, Orchestrator, профіль і дванадцять ролей. Готові Windows/macOS/Linux-пакети '
                     'містять Python, Node і зібрану панель; окреме налаштування Python, Node, npm або TypeScript для '
                     'цього шляху не потрібне. Джерела та поглиблене збирання також збережено.'),
                    ('Що фактично підтримується?',
                     'Готові пакети націлені на шість ОС/CPU; CI визначає окремі нативні перевірки для кожної. До '
                     'успішних квитанцій точного Release ці перевірки залишаються непідтвердженими. Один локальний '
                     'прогін чи сам файл workflow не доводить перевірку всіх платформ. Графічна взаємодія, мінімальна '
                     'версія ОС, підпис/notarization, модельні задачі й дозвіл на продаж мають окремі межі.'),
                    ('Чи можна продавати результати?',
                     'Так, у межах редакції та прав на вихідні матеріали. Скопійовані ресурси самого комплекту '
                     'зберігають свої умови; весь комплект не надається для перепродажу.'),
                    ('А якщо магазин недоступний?',
                     'Збережіть придбану версію, ліцензійний документ, пакет і резервні копії. Недоступний магазин не '
                     'вимикає локальних прав і не змінює ваші проєкти.'),
                    ('Як отримати підтримку чи повернення?',
                     'Власник надав контакт підтримки й приватності: {seller_name}, {support_contact}. Документація та '
                     'допомога з відтворюваними помилками включені; гарантованого часу відповіді немає. Роботу каналу, '
                     'години, решту юридичних реквізитів і умови повернення ще треба підтвердити.')],
        'trust': 'Перевірка та відновлення',
        'draft': 'Технічний дистрибутив · фактичні перевірки перед публічними обіцянками',
        'license': 'Ліцензія й підтримка',
        'docs': 'Установка та відновлення',
        'first': 'Перша задача',
        'locale': 'English',
        'launcher_start': 'Обрати запуск для моєї системи',
        'trust_body': 'Збережіть початковий пакет і точний журнал setup. Після переривання оновіть історію в майстрі '
                      'та оберіть перевірену операцію для продовження, відкату чи видалення. Перевірте джерело й '
                      'перечитайте невизначений результат перед повтором. Дані панелі мають окремі резервні копії та '
                      'перевірку схеми.',
        'demo_body': 'Реальні знімки панелі з ізольованими тестовими даними. Відео показує виконання setup, виявлення '
                     'навичок і першу задачу в позначеному тестовому вікні; це інструмент демонстрації, а не інтерфейс '
                     'продукту. Запис стосується свого середовища кандидата та не замінює перевірок нового майстра або '
                     'всіх шести платформ.',
        'platform_title': 'Один інсталятор. Ваша система.',
        'platform_intro': 'Готовий Universal містить шість цілей: x64 та ARM64 для Windows, macOS і Linux. Є й менші '
                          'пакети для окремої платформи. Відкриття статичного HTML саме по собі не встановлює файли: '
                          'локальний майстер запускає відповідний файл нижче. Потрібні окремо Codex і ваш обліковий '
                          'запис.',
        'platform_note': 'Майстер має українську й англійську мови. Python/venv і Node ваших проєктів зберігають '
                         'пріоритет; службові скрипти використовують точний AGENT_SYSTEM_PYTHON. Немає глобальної '
                         'зміни PATH або реєстру. Maintenance залишається окремим інструментом власника.',
        'platform_docs': 'Покрокове встановлення та відновлення',
        'screens_caption': 'Знімки попередньої панелі · Agent Atelier 0.7.0 · '
                           'джерело 87dd0001149d214722b59b9d16793337fae5c01e. Реальний готовий runtime з ізольованими '
                           'пробними даними; це не знімки нового установника.',
        'video_caption': 'Попередній запис встановлення й першого результату · '
                         'джерело a930d902ba9ab2512cca867a34be33a4ea100e67 · Apple M1/macOS27.0.1, Python3.13 та '
                         'авторизований Codex0.166.0. Позначене вікно виконання — інструмент демонстрації; цей запис '
                         'не показує новий майстер у браузері.',
        'provenance': 'Точні дані походження запису',
        'screens_provenance': 'Точні дані походження знімків'}}
def e(value):return html.escape(str(value))
def render_pages():
    pages={}
    for lang,t in T.items():
        links={'en':'https://github.com/alex-hohaizel/codex-agents/blob/main/docs/INDEX.md','uk':'https://github.com/alex-hohaizel/codex-agents/blob/main/docs/uk/GUIDE.md'}
        for kind in ('sales','start'):
            # A copied package-root entry uses package-relative targets; site pages use source-relative targets.
            is_start=kind=='start'
            logo='Codex Agent System'
            plans=''
            for key,item in OFFER['editions'].items():
                audience=('One named user · multiple personal devices' if key=='solo' else 'Up to five named users · one organization') if lang=='en' else ('Один іменований користувач · кілька пристроїв' if key=='solo' else 'До п’яти користувачів · одна організація')
                rights='Personal and client commercial projects' if lang=='en' else 'Особисті й клієнтські комерційні проєкти'
                plans+=f'<article class="card"><h3>{e(item["label"])}</h3><div class="price">${item["price_minor"]//100}</div><p>{audience}</p><p>{rights}</p></article>'
            cards=''.join(f'<article class="card"><h3>{e(h)}</h3><p>{e(b)}</p></article>' for h,b in t['cards'])
            steps=''.join(f'<li>{e(x)}</li>' for x in t['steps'])
            faq=''.join(f'<details><summary>{e(q)}</summary><p>{e(a.format(seller_name=OFFER["seller"]["legal_name"],support_contact=OFFER["seller"]["support_contact"]))}</p></details>' for q,a in t['faqrows'])
            startlink='#platform-launchers' if is_start else '../../docs/commercial/BUYER_GUIDE'+('.uk' if lang=='uk' else '')+'.md'
            other=('ПОЧАТИ.html' if lang=='en' else 'START_HERE.html') if is_start else ('sales-uk.html' if lang=='en' else 'sales-en.html')
            image='assets/marketing/current/overview.png' if is_start else '../../assets/marketing/current/overview.png'
            docs='docs/commercial/BUYER_GUIDE'+('.uk' if lang=='uk' else '')+'.md' if is_start else '../../docs/commercial/BUYER_GUIDE'+('.uk' if lang=='uk' else '')+'.md'
            page=f"""<!doctype html><html lang="{lang}"><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{logo} — {e(t['setup'] if is_start else t['hero'])}</title><style>{STYLE}</style>
<main><div class="top"><span>◇ {logo}</span><a href="{other}">{t['locale']}</a></div>
<div class="eyebrow">{t['tag']}</div><h1>{e(t['setup'] if is_start else t['hero'])}</h1><p class="lede">{e(t['intro'])}</p>
<p class="banner">{e(t['candidate'])}</p><a class="cta" href="{startlink}">{e(t['launcher_start'] if is_start else t['start'])}</a><a href="{links[lang]}">{e(t['more'])}</a>
<section id="platform-launchers"><h2>{e(t['platform_title'])}</h2><p>{e(t['platform_intro'])}</p><div class="grid"><article class="card"><h3>Windows · x64 / ARM64</h3><p><code>Start.cmd</code></p><p>Start-Workbench.cmd</p></article><article class="card"><h3>macOS · Intel / Apple Silicon</h3><p><code>Start.command</code></p><p>Start-Workbench.command</p></article><article class="card"><h3>Linux · x64 / ARM64</h3><p><code>Start.sh</code></p><p>Start-Workbench.sh</p></article></div><p class="muted">{e(t['platform_note'])}</p><p><a href="{docs}">{e(t['platform_docs'])}</a></p></section>
<h2>{e(t['setup'])}</h2><ol class="steps">{steps}</ol>
<p><a href="{docs}">{e(t['docs'])}</a> · <a href="{'LICENSE.txt' if is_start else '../legal/LICENSE.txt'}">{e(t['license'])}</a></p>
<h2>{e(t['includes'])}</h2><div class="grid">{cards}</div>
<h2>{e(t['plans'])}</h2><p>{e(t['edition'])}</p><div class="grid">{plans}</div>
<h2>{e(t['faq'])}</h2>{faq}
<h2>{e(t['trust'])}</h2><p>{e(t['trust_body'])}</p>
<img src="{image}" alt="{e('Illustrative product workflows; not a live screenshot' if lang=='en' else 'Ілюстрація можливих продуктових сценаріїв; не знімок живого застосунку')}">
<p class="muted">{e('Original product illustration. Actual installation and task evidence are delivered with the candidate report.' if lang=='en' else 'Оригінальна продуктова ілюстрація. Фактичні докази установки й задач надаються зі звітом кандидата.')}</p>
<h2>{'Recorded walkthroughs' if lang=='en' else 'Записані проходження'}</h2>
<p>{e(t['demo_body'])}</p>
<p class="muted provenance">{e(t['screens_caption'])} <a href="{'commercial/media/' if is_start else '../media/'}WORKBENCH-PROVENANCE.json">{e(t['screens_provenance'])}</a></p>
<div class="grid">
<img src="{'commercial/media/' if is_start else '../media/'}workbench-project-en.png" alt="Actual Agent Atelier: isolated project">
<img src="{'commercial/media/' if is_start else '../media/'}workbench-project-uk.png" alt="Фактичний Agent Atelier: пробний проєкт">
<img src="{'commercial/media/' if is_start else '../media/'}workbench-skills-en.png" alt="Actual skill catalog">
</div>
<p class="muted provenance">{e(t['video_caption'])} <a href="{'commercial/media/' if is_start else '../media/'}BUYER-DEMO-PROVENANCE.json">{e(t['provenance'])}</a></p>
<video style="width:100%;margin-top:24px" controls preload="metadata" poster="{'commercial/media/' if is_start else '../media/'}buyer-demo-result.png"><source src="{'commercial/media/' if is_start else '../media/'}Buyer-Install-and-First-Result.mp4" type="video/mp4"></video>

<div class="foot"><strong>{e(t['draft'])}</strong><p>{e(OFFER['seller']['legal_name'])} · <a href="mailto:{e(OFFER['seller']['support_contact'])}">{e(OFFER['seller']['support_contact'])}</a></p><p class="muted">{e(RELEASE['repository_version'])} · {e(OFFER['license_version'])} · Codex compatibility does not imply OpenAI endorsement.</p></div></main></html>"""
            pages[f'commercial/site/{kind}-{lang}.html']=page.encode('utf-8')
    return pages


def check_pages(root=ROOT):
    """Return stale generated pages without rewriting customer-facing files."""
    return ['Stale commercial page: '+name for name,expected in render_pages().items()
            if not (root/name).is_file() or (root/name).read_bytes()!=expected]


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check',action='store_true',help='Check exact generated bytes without writing')
    args=parser.parse_args(argv)
    if args.check:
        errors=check_pages()
        if errors:
            print('\n'.join(errors),file=sys.stderr)
            return 2
        return 0
    for name,expected in render_pages().items():
        (ROOT/name).write_bytes(expected)
    return 0


if __name__=='__main__':
    sys.exit(main())
