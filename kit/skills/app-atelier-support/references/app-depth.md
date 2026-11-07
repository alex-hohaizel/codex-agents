# Системна підтримка App Atelier

Зміст: 1 — повний контракт; 2 — knowledge/data; 3 — правила діалогу; 4 — виробництво; 5 — приймання та continuity.
Прочитати cross-domain-core, data/support, workflow й acceptance. `assets/app-depth.templates.json` є шаблоном linked project artifact; authoritative requirements/effects/evidence залишаються у canonical state.

Для наскрізних app-specific контрактів застосувати [модель систем застосунку](app-system-contract.md); її requirements/state authority не дублювати.

## 1. Побудувати підтримку від продуктового результату

Побудувати coverage `product rule/version → issue category → user mode → channel/state → required facts → allowed action → answer/case → proof`. Пройти public help, account help за наявності, access/payment/errors/outage, missing feature, stale knowledge, unsupported request і нерозв’язний case. Android/iOS/web та погоджені зовнішні bot channels мають спільну продуктову семантику, проте окремі UI/transport/identity адаптери. Відсутні групові сценарії не імпортувати з універсального chatbot agent; підтримка продукту залишається окремим призначенням.

Для кожної категорії визначити точний результат: explanatory answer, guided step, authoritative read, allowed operation або tracked case. Рішення «resolved» потребує конкретного спостереження за контрактом; сама відповідь моделі не означає успішне виправлення. Поділ на категорії не змінює product policy чи права.

Класифікувати можливості як required/conditional/absent_by_design. Новий LLM/RAG/vector database/voice/CRM оператор не додається автоматично. Коротка структурована довідка може бути достатнім маршрутом. Професійні, фінансові, дитячі або інші відповідальні домени потребують належного предметного review і явних меж, а не вдаваної кваліфікації AI.

## 2. Формалізувати знання та приватний контекст

Кожна KB entity має stable ID, product/release/language/region, authoritative source+hash, valid_from/valid_until за застосовності, claim scope, owner, review/freshness triggers і fallback. Ціна, policy й entitlement беруться з належного authoritative джерела, а не узагальненої історії. Зміна релізу/плану/правила відкриває залежні відповіді, embeddings/cache і cases; старі accepted originals лишаються відтворюваними.

Public documents, private customer records, case history, tool outputs і operational receipts — різні класи з окремими access rules. Для кожного поля назвати source, purpose, authority, subject/tenant, recipient, retention, deletion/revoke і backup behaviour. Retrieval фільтрує scope до пошуку і перед відповіддю; prompt не створює авторизації. Cache key включає subject/tenant/permission revision, product/release/locale і source version.

Позначити trusted instruction, verified product fact, user statement і retrieved untrusted content. Вкладення/KB/chat не можуть додати tool permission, змінити refund policy чи вимкнути isolation. Не зберігати secrets або приватні reasoning traces у діалозі/логах/skill. Відсутній результат не заповнювати правдоподібною відповіддю.

Для вибраного Telegram linking зберегти створений у authenticated app/web challenge, private sender numeric ID, expiry/use state і явне app/web підтвердження конкретного link. Replay/interception/account switch/revoke/logout перевірити як окремі transitions. Username, email у тексті й старий link не дають доступу.

## 3. Задати правила turn, action і case

Turn contract описує user/session/channel identity, transport ID, accepted input types/size, product context revision, retrieval budget, answer claims/citations, tool allowlist, timeout/cancel, cost cap і output validation. Повтор webhook/edit/button не створює нову дію або case без предметного правила. Діалогові, transport, action і case IDs не зливати.

Action lifecycle: requested → validated → authorized → pending → succeeded/failed/unknown → reconciled. Для кожного переходу назвати actor/auth, preconditions, exact parameters, idempotency scope, receipt, expected state, retry/compensation та user wording. Unknown не називати failed і не дублювати effect. Повідомлення «повернено кошти» можливе лише після належного authoritative receipt/read-back.

Case lifecycle: locally_drafted/received/triaged/awaiting_information/queued_for_repair/resolved/closed за потребою. Offline draft не є received. Case ID сам не є дозволом читати дані. Визначити retention, deduplication, reopen, aggregation у технічну задачу та умову справжнього resolved. Не обіцяти людей, SLA чи щоденну роботу власника, яких немає в операційній моделі.

Довести корисний degraded route: public cached help з версією, truthful status, локальна чернетка або durable case через доступний storage. Session/user/global caps, attachment limits, timeouts, circuit breaker і retrieval fallback задаються числами з економіки, а не словами «дешево» чи «необмежено».

## 4. Виготовити й інтегрувати

Recipes охоплюють KB ingestion, chunk/index за потреби, structured retrieval, channel adapters, authenticated tools, answer evaluation, case workflow, deployment і monitoring. Для кожної операції зберегти доступний tool/schema/platform, input/output formats, rights/egress/cost, editable source, exact steps, consumer й validator. Наявність ChatGPT skill не означає production LLM API чи token budget.

Перед обробкою матеріалів перевірити schema/catalog/actual parameter consumption. HTML/Markdown/encoding/URL/file extraction — окремі transformations з input bounds, content provenance, preserved IDs/locale і втратами. Retrieval score не є ймовірністю правдивості. Для audio/voice за застосовності перевірити транскрипцію, consent/data scope, pronunciation, interruption і доступну текстову альтернативу.

Pending attempts створюються до платного/зовнішнього effect; фактичні request/job IDs і outputs записуються лише після виконання. Зберегти актуальні model/prompt/policy/KB/toolchain hashes, permitted data scope, token/cost observation і fallback. Prompt repair має failure class, нову гіпотезу, ліміт і контрприклад; повтор без зміни причини не є прогресом.

## 5. Прийняти whole-support assembly

Assembly pin-ить exact client/backend/model/policy/KB/config hashes, tenant/subject/link state, channel, raw scenario, expected answer properties/actions, budget і environment. Пройти `user input → auth → retrieval → response/action → presentation → case/receipt → restart/revoke/resume`. Окремий добрий prompt не доводить доступну й безпечну інтеграцію.

Позитивні fixtures: guest public answer; account own context; linked permitted channel; version-specific KB; unknown question; cap/outage fallback; authorized effect з receipt; revoke/delete з наступним доступом. Негативні: A→B ID/cache/file, stale KB/price, forged/group/replayed event, prompt injection, expired challenge, concurrent account switch, delayed tool result після revoke, duplicate case/action, storage full, unresolved effect при restart.

Для оцінки розділити factual correctness, groundedness, useful next step, tone, scope/privacy, tool correctness, resolution proof, latency/cost і accessibility. Прийняти hard invariants окремо; середній бал не перекриває privacy/permission fail. Automated oracle обмежити перевірними фактами; вільний judge не є authoritative product source. Незалежний actor отримує raw prompt/inputs без підказки expected answer.

Оновлення KB/model/policy/tool invalidates залежні cases, cache й assembly; permission revocation застосовується до inflight/queued work. Backup restore не відновлює видалені/відкликані записи. Тестувати всі канали в доступному реальному середовищі; відсутній канал/device залишається blocked із exact bridge. Текст runbook не є запущеним сервісом чи scheduler.

Повернути contracts/KB/editable sources, matrices/fixtures, actual attempts/receipts/evidence, caps/recovery, gaps й next action. Зберегти приватні матеріали лише у дозволеному project scope.

## Видимий результат і достатність підходу

Застосувати [адаптивну роботу](adaptive-work.md) до поточного обсягу. Для цієї ролі явно показати: контракт підтримки, канали/права, джерела знань, життєвий цикл звернення й перевірний шлях вирішення. Позначити, що фактично досліджено/створено, що успадковано з чинних рішень і що лишається майбутнім результатом із due gate. Обґрунтувати потрібну глибину й компетенції через невизначеність, наслідки та зв’язність; для локальної правки не запускати новий повний цикл.

За матеріальних прогалин викликати потрібний режим [дослідження/синтезу/звірки](research-and-synthesis.md). Перевірка якості охоплює: предметна правильність відповіді/дії, приватність, межі делегування й фактичний результат. Raw-source review має шукати й невнесені вимоги. Інший actor ID сам не доводить належної компетенції; структурний PASS не підвищує вид доказу. Зберігати проєктний контекст, чинні погодження та незачеплені результати.
