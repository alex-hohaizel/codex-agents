# Компоненти продукту та виклики інших сімейств

Зміст: вибір → стабільні виклики → пакет компонента → виконання → повернення. Читати, коли App Atelier приймає частину плану іншого агента, коли застосунку потрібен чатбот, або коли бракує потрібної спеціалізованої методики.

## Межі й authority

Один продукт може містити застосунок, чатбота й спеціалізовані агентні інструменти. Це не три незалежні продукти й не причина тричі збирати однаковий бриф. Зберігати один `product_id`, parent requirement IDs, прийняті рішення й власників спільних контрактів. App Atelier відповідає за доручений app component; батьківський інтегратор приймає міжкомпонентний результат. Прямий запит до App Atelier не потребує створення додаткового Agent Foundry wrapper.

Для нового проєкту узгодити `product_id` з canonical App profile/state. В існуючому проєкті не перейменовувати actual IDs автоматично: розбіжність parent/local IDs потребує явної перевіреної mapping або повернення upstream. Ключі зовнішнього обліку jobs/effects/receipts включають `(product_id, component_id, local_id)`, щоб однакові локальні IDs різних компонентів не зливались.

Для кожної підзадачі визначити `component_id`, свій requirement subset, input/output/consumer, shared contracts, allowed effects/бюджет, due acceptance й `return_to`. У `orchestrator_chain` записати фактичний шлях делегування. Повернення до parent — передача результату, а не новий рекурсивний запуск того самого агента на той самий scope. Призначити одного writer кожному shared API/schema, permission policy, design token set, KB та release epoch.

## Стабільні імена й вибір маршруту

Повний каталог stable selectors і умов маршрутизації — `assets/specialist-routes.json`; його запис не підтверджує встановлення або виконання. У Work використовувати `@<stable-name>`, у Codex — `$<stable-name>`. Frontmatter `name` незмінний; номер у видимій назві не є частиною виклику. Перед викликом знайти встановлене джерело за цим ID, прочитати його поточні входи/виходи/обмеження й зафіксувати фактичні version/hash у job record. «Остання актуальна версія» визначається доступним перевіреним джерелом, не назвою папки чи історією чату.

| Умова | Work | Codex | Результат / отримувач |
|---|---|---|---|
| Батьківський план автоматизації містить app component або змінюється продуктова межа | `@agent-foundry` | `$agent-foundry` | Батьківський план, стабільні IDs, scope/decisions; App повертає свій компонент й міжсистемні gaps інтегратору |
| Потрібно спроєктувати нову багаторазову спеціалізовану навичку/сімейство, якої немає | `@design-specialist-skills` | `$design-specialist-skills` | Blueprint/створена методика з inherited requirements; не зайвий щабель для звичайного app build |
| Компонент є застосунком | `@app-atelier-director` | `$app-atelier-director` | Прийнятий app scope, потрібні стадії, source/build/QA/handoff |
| Бот є окремим каналом, частиною core або складною підтримкою | `@chatbot-atelier-director` | `$chatbot-atelier-director` | Повний bot component або точний доручений зріз за спільними продуктовими контрактами |
| Потрібен лише конкретний bot adapter/action/job | `@chatbot-atelier-integrations` | `$chatbot-atelier-integrations` | Перевірний platform adapter, identity/audience/delivery/receipt/recovery; без повторного продуктового research |
| Потрібні лише бот-знання/пам'ять, розмова, медіа або QA | Відповідний `@chatbot-atelier-knowledge`, `@chatbot-atelier-conversation`, `@chatbot-atelier-media`, `@chatbot-atelier-qa` | Ті самі stable IDs із `$` | Лише конкретний артефакт/контракт і належні докази; App інтегрує його у свій сценарій |

Наявність імені в таблиці не означає виконання. За відсутності peer skill не писати «викликано». Виконати дозволену частину за локально включеними контрактами або передати самодостатній пакет у придатне середовище; required peer capability лишається blocked, якщо без неї неможливий обіцяний результат. Якщо потрібна методика вже є й достатня, не створювати її дубль через конструктор.

## Вхід компонента й умови допуску

Компонентний пакет `atelier-component-handoff/1` є поточним форматом взаємодії. Він передає:

- `product_id`, `component_id`, `component_kind`, `parent_requirement_ids`, `owned_requirement_ids`, відомі dependencies та actual `return_to`/consumer;
- поточний намір/межу, accepted decisions/originals, applicability й material unknowns; джерела й input files з SHA-256;
- typed domain/API/event/data/auth contracts, кожний із stable contract ID, owner, file/hash, reader/writer, semantic invariants і зміною версії;
- environment/capability snapshot, права, зовнішні дії, budget/stop, обмеження й ресурсне ownership;
- requested deliverables, acceptance/oracles/negative cases, потрібні типи доказу й due gate;
- для чатбота `selected_channels` або `proposed_channels`, audience/identity/link/revoke/retention, channel-adapter contract refs і delivery semantics; невибраний канал не підміняти Telegram;
- фактичні attempts/jobs/unknown outcomes, створені outputs/hashes, achieved proof, gaps, checkpoint і точний наступний крок.

У App ledger цей пакет реєструвати як `artifact` із path/hash та посиланнями потрібних jobs/requirements; не вигадувати `put --kind component` і не створювати другу mutable registry. Шаблон не є execution grant. Продуктові рішення й чинні дозволи перевірити за реальним дорученням; вже надану згоду не збирати повторно. Критичний unknown блокує залежну дію; незалежний analysis/design можна продовжувати. Skills і повідомлення не переносять credentials, приватну chat history або локальні browser sessions автоматично.

## App ↔ bot: точна межа підтримки

`@app-atelier-support` залишається власником продуктового support contract: категорії/guest/account режими, дозволені поля й дії, KB/ціни/відомі помилки, tone, case lifecycle, caps/fallback та app/web UX. Для простої локальної довідки не запускати новий bot project. Якщо потрібен bot channel, передати лише adapter/knowledge/conversation реалізацію потрібному модулю ChatBot Atelier. Назву платформи й кількість каналів визначає задум.

Bot component не перебудовує parent app auth, billing, модель даних або підтримку самовільно. Provider identity не прирівнюється до product subject; linking/revoke та довіра до webhook мають власний контракт. Transport destination, logical recipient, tenant, subject, audience й purpose не змішуються. Відкликання доступу/видалення інвалідовує payload/cache/jobs і перевіряється повторно перед delivery. Публічний/group канал не отримує private support за замовчуванням; погоджений shared сценарій має окремі правила й негативні докази.

## Приймання й повернення Work ↔ Codex

App та bot компонент мають один acceptance scenario через app input → domain/auth → bot/tool/provider → result → delivery → recovery. Отримувач перевіряє source/build/config/content epoch, hash bindings, точні outputs і required modality. Приймання бот-тексту не підтверджує app integration; green app build не підтверджує provider delivery. Shared contract change повертає upstream affected IDs й інвалідовує залежні докази перед наступним effect.

Передача між Work і Codex містить actual working context, точні source/input/output hashes, пройдені checks, permissions/budget/stop, job IDs та невідомі outcomes, next action і return validation. Codex може почати з прямого доручення й реального проєкту без попереднього Work-пакета; тоді він відновлює ті самі записи з чинних джерел. Два середовища не пишуть одночасно один source/БД/provider effect. До повтору timeout спочатку reconcile, без нового ID того самого наміру.

Cold return має дати parent інтегратору відтворюваний результат, actual execution receipt або чесний `not_invoked`/`blocked`/`prepared` status. Обсяг і належний доказ приймаються окремо; fabricated invocation, відсутній peer source чи чужий stale receipt не закривають компонент.

## Машинна перевірка пакета

Шаблон — `assets/component-handoff.template.json`; інстанціювати його за реальним проєктом. `python3 -B scripts/check_component_handoff.py FILE --root PROJECT_ROOT` перевіряє поточну компонентну структуру й byte bindings, а `--ready` — заявлену готовність до передачі отримувачу. Це не product/runtime readiness, не підтвердження користувацької волі й не факт виклику іншої навички. Перевіряти actual receipt та належне предметне приймання окремо.

## Приклади адресного доручення

Після binding реального пакета Work-запит може виглядати так: `@app-atelier-director Прийми app component з указаного пакета; збережи product_id, parent requirements і shared contracts. Виконай тільки доручений scope та поверни outputs/evidence/checkpoint інтегратору.` У Codex використовувати `$app-atelier-director` з фактично доступним шляхом до того самого перевіреного пакета або проєкту. Це приклад шаблону запиту, а не виконаний виклик.

Для bot component: `@chatbot-atelier-director Прийми bot component цього продукту; уточни невибрані канали, виконай доручені стадії за чинними product/auth/data contracts і поверни прийнятий результат App інтегратору.` У Codex — `$chatbot-atelier-director`. Якщо потрібен лише один adapter, адресувати `@chatbot-atelier-integrations` / `$chatbot-atelier-integrations` з тим самим component scope; не запускати повторний повний discovery.
