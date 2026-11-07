# Концепт 4.0: ціла гра, розвиток і комерційна система

Застосовувати [Game Model workflow](game-model-workflow.md) і предметні модулі. Цей reference уточнює concept-stage outputs; Game Model schema й [model format](model-format.md) визначають machine contracts. Чинний systemic passport є linked pre-illustration projection; повні виробничі домени й contracts зберігаються в моделі.

## Шари й застосовність

| Шар | Що визначити до показу кандидата | Що розгорнути до реалізації |
|---|---|---|
| Дія/освоєння | Намір, стабільний input, rule/contact, помилка/feedback/recovery; input now/later/absent | Стани, timing, hitboxes/physics, buffering/cancel, accessibility і tests |
| Спроба | Мета, підготовка, проміжні вибори, кульмінація, кінець/наслідок | State graph, fail/retry/quit/resume, save/authority й UI flow |
| Світ/зустрічі | Topology, маршрути, варіанти ризику/винагороди, поведінкові ролі | Входи/виходи, encounter budget, навігація, агенти, world states і constraints |
| Розвиток/винагороди | Early/mid/late зміна можливостей; бажана наступна мета й винагорода | Unlock graph, prerequisites, формули/stacking, acquire/equip/upgrade/use, pace/duplicates/caps |
| Варіативність/життя | Причина добровільного повтору, authored families, відмінні рішення й launch scope | Контентний inventory, generators/fixtures, endgame/cadence, capacity/cost і telemetry |
| Commerce/магазин | Модель-кандидати, fit, цінність/відмова, earned/paid impact й store journey | Eligibility/catalog/pricing/receipt/grant/restore/refund/ads/expiry failure contracts |

Не вимагати однакових форм для всіх жанрів. Спортивна майстерність може бути провідним розвитком; гра без бою має поведінкові виклики; гра без inventory не потребує штучного loot. Застосовність має предметну причину й requirement refs. Невідоме не означає N/A. Малий production scope обмежує authored capacity, а не якість рішень.

## Правила та причинність

Механіка має state variables, conditions/events, player choice, cost/limit, consequence, counterplay/failure/recovery і cues. Зв'язок зараховувати, коли конкретна зміна A змінює можливість/пріоритет/timing/траєкторію/ризик B. Два контексти з тими самими інструментами мають показувати інший розумний вибір. Перевіряти remove-system, strongest-simple-policy, novice/expert та early/late counterexamples; кількість вузлів не є глибиною.

Характеристика предмета/гравця/супротивника має units/domain, gameplay effect, acquisition/progression, cap/reset, modifiers/stacking/order, conflicts/synergies, readable cue, persistence/authority, scenario/test refs. Для техніки задати family/body/modules/handling/maintenance/customization за fit. Не замінювати різний досвід пасивним +1%. C1 визначає повну архітектуру сімейств, їхній причинний зміст, простір поєднань, розвиток і ризики; preproduction замикає точні executable запускові таблиці/граматики й повний finite inventory T. Кілька демонстраційних рядків не закривають C1 архітектуру.

Ресурс може бути HP, станом тіла, теплом, імпульсом, шумом, інформацією, довірою, позицією чи доступом. Задати sources/sinks/transform, альтернативну витрату, depletion/overuse/recovery, reader cue, persistence/reset і вплив на іншу систему. Не додавати валюту лише для заповнення поля. Якщо дві валюти об'єднуються без втрати рішення, обґрунтувати складність або спростити.

## Світ і поведінкові виклики

Розділити масштаб виробництва, topology світу, локальний encounter і видимий фрагмент. Перехід між authored локаціями має entry/exit, prerequisites, loading/save, navigation feedback і зміст розвитку. Для повернення визначити добровільну ціль, змінений доступ/контекст, drop chance або чесну невизначеність, tracking і reward relevance. Постійні зміни світу не скидати тихо для зручного повтору.

Агент має role/intent, senses/memory, стани/вибір дії, ability preconditions/cost/telegraph/recovery, навігацію, протидію, взаємодії/координацію й difficulty progression. Encounter grammar комбінує ролі, простір, цілі, ресурси й наслідки; сильніший ворог зі збільшеним HP не є новою роллю. Динамічні події мають admission/fairness/compatibility constraints; не читати input приховано й не створювати невідворотний offscreen damage без чесних cues/відповіді.

Процедурні дані розділяти на authored vocabulary і generated instances. Для алгоритму визначити connectors, reachability, skill prerequisites, budgets, заборонені комбінації й validation fixtures. Seed record містить algorithm/version, random streams і rules/content versions. Різні seeds не доводять різні стратегії або нескінченний зміст.

## Нагороди й навчання

Reward contract пов'язує trigger/eligibility, exact reward або table/odds, delivery/claim, duplicates/cap/expiry, persistence, cue, next use/choice й recovery. Покращення/колекція/здібність/маршрут має видиму користь, а не лише число. Розвиток має дальню ціль з prerequisites і pace; повернення не перетворювати на примусове відпрацювання старих арен.

Навчання має knowledge prerequisites, safe discovery, guided/unguided action, evidence of comprehension, transfer, optional help/re-entry і skip для вже освоєного. Для кожної ключової комбінації показати шлях від простої дії до її застосування під тиском. Зв'язувати input→rule/contact→animation/VFX→audio/music→haptic→cost/reward/world change→next decision; зберігати predictive/confirmation/error/recovery і mute/no-haptic parity.

## Комерційний fit без універсального kit

Порівнювати придатні моделі на їхній функції в конкретному loop, audience, session arc, прогресії та content capacity. Premium/content/expansion, collections/playstyles, pass/season, limited attempts/rewarded, consumables/currency, convenience/acceleration — кандидати для аналізу, не обов'язковий набір. Альтернативний досвід і відмова від cosmetic-only залишаються вимогами відповідного brief; це не доводить, що кожна гра має продавати одну роль назавжди. Latest user instructions уточнюють попередні вимоги шаблон.

Для chosen hypothesis визначити sources/sinks/exchanges, earn/spend, authority/persistence, free/paid/earned pace, caps/expiry/replenishment, cumulative access/power/synergies, next meaningful goal та production/recurring costs. Paid attempts не нескінченні за замовчуванням; rewarded ad не гарантовано завантажується; no-fill/offline/cancel не повинні ламати основний прогрес. Для alternative playstyle порівняти ту саму ситуацію в поточному проходженні, tradeoffs і спільні стани без невказаного refill/reset.

Магазин має discovery/offer/trial/compare/price/confirmation/grant/use/restore/refund/failure/recovery. До реалізації кожна offer задає exact contents/benefit, eligibility, localized price source, purchase type/recurrence, duration/expiry, decline/free path, grant semantics і player-readable outcome. Ads потребують opt-in, natural pause, cap, no-fill/cancel/reward exactly once/audio lifecycle. Pass — free/paid tracks, objectives, start/end/timezone, reachable pace, late join/catchup, unclaimed rewards. Paid randomness — окремий вибір, versioned odds/guarantees/pity/duplicates/disclosures й актуальна перевірка ринків/store policy.

No-offer control, повна free арка за F2P hypothesis, shortest/longest/rare scenarios, dominant portfolio та strongest paid-advantage counterexample — частини оцінки, не автоматична обіцянка балансу. Однакова DPS не доводить горизонтальності. One-time purchase не моделювати щомісячним recurring revenue. Conversion/eCPM/LTV лишаються assumptions/ranges із source, доки нема own observed evidence.

## Приймання

Design coherence, simulation, human replay desire, native feel, sandbox payment, observed revenue й sustainable contribution — окремі висновки. Результат концепта містить mechanism, strongest objection, evidence/limits і next discriminating test для всіх due must. Незакритий must не усереднюється score. Повний концептуальний документ C1 належить кожному завершеному кандидату; виробничий TDD T, actual device/human/commercial proof мають свої наступні gates; заповнення документа не робить їх виконаними.

## C1 як завершена продуктова архітектура

Пройти всі 20виробничих напрямів із предметним applicability rationale. Для активних систем віддати purpose/owner/consumer, causal rules/state, залежності, сімейства/variation envelope, progression/opportunity, full journey, art/audio/input, save/authority, production route й acceptance scenarios. У C1 можна лишити T-level tuning з owner/метою/межами/due stage; не можна лишити невідомими механізм, довгу арку, ціну помилки або значущий state.

Для damage/death/crash визначити contact/delivery/effect/defense/resource/part/lifecycle architecture, доступну контрдію, failure recovery, kept/lost costs, retry й persistent consequences. Для AI вказати knowledge channels/memory, decisions/actions, encounter legality та boss-phase purpose за fit. Для світу — authored macro, progression, space, encounters, persistent reactions і генеративні constraints/fallback.

Consumer preproduction має відтворити first/normal/peak/late/failure/retry/return/completion і назвати всі потрібні T-level уточнення без вигадування продуктового задуму. C0 називати ескізом; число previews або розмір гри не дають автоматичного C1.
