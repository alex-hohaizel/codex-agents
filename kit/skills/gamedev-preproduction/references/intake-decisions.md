# Вхід і рішення

## Прийняти повний контекст

Перевірити джерело студії: назва, permitted developer/legal display names, stable studio ID, package/application ID namespace, approved logo variants і bytes, brand tokens, ліцензії, support/privacy URLs, ownership та actual setup state. Не вигадувати юридичну особу, D-U-N-S, країну, платіжний аккаунт чи готовність store. Бренд ігор може мати власну палітру; studio sign-off використовується лише в дозволених місцях: splash/about/credits/store/developer identification. Не фарбувати весь світ у корпоративні кольори без творчого рішення.

Прочитати актуальний manifest/entrypoint upstream; архівувати exact input. Знайти active concept, прийнятий golden frame, playable rules, всі відмови/слабкості, реальні тестові дані й відсутні докази. Старий partial пакет приймати як матеріал для ремонту, не як implicit approval.

## Матеріальні розвилки

| Питання | Чому змінює результат | Що показати до вибору |
|---|---|---|
| Android / iOS / обидві; min devices | API/SDK, QA, UI, touch, payments, бюджет | Matrix supported/tested/blocked, requirements та фактичні toolchains |
| Portrait/landscape, one/two hands | Камера, UI safe zones, input vocabulary | Однаковий action sample в обох релевантних layouts |
| 2D/2.5D/3D; camera type | Asset sources, rig, physics, performance | Однакова сцена з production/import feasibility |
| Offline-first / online-required / co-op/PvP | Save authority, backend, cheating, latency, accounts | Sequence diagrams і disconnect/recovery user experience |
| Runs/campaign/endless/seasonal | Content cadence, progression, ending, monetization | First 3 runs і late-game loop на конкретних даних |
| Free/premium/hybrid, ads/IAP, minors | Economy, store compliance, reach, support | Цілісні альтернативні player journeys з ціною/правами/обмеженнями |
| Content scope and cadence | Реальна вартість варіативності | Authored vocabulary, generation rules, cost model, scope floor |
| Engine/toolchain/backend | Native feasibility, license, lock-in | Official docs, actual small PoC, total recurring cost |
| Canonical target fidelity and quality floor | Scope, art/audio effort, device budget | Exact visual/audio/motion samples + measurement plan |

Не ставити універсальну анкету з усіх можливих питань. Якщо вхід уже вирішує питання — послатися на нього. Технічні деталі всередині прийнятого envelope вибирати автономно. «Обидві платформи» не означає «вже перевірені обидві». Не змінювати матеріальну опцію через недоступність інструмента мовчки.

## Запис рішення

Для матеріальної розвилки зберегти decision ID, scope, question, feasible options, sample refs/hashes, recommendation with trade-offs, cost/rights/device implications, user's exact response/source, timestamp, fixed properties, permitted derivatives, reopen conditions. AI evaluation не замінює user choice. Уточнення правила не є дозволом платити або публікувати.

Коли scope неприйнятий, працювати над незалежними contracts, аудитом, tool discovery, безкоштовним малим PoC. У status report позначити конкретну залежну частину як pending. Не блокувати всі можливі роботи одним невідомим.
