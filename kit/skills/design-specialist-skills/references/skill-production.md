# Виробництво спеціалізованої навички

Чинний контракт. Зміст: записи → алгоритм → рецепти → докази → зміна.

## Записи й алгоритм

В одному project-owned blueprint/linked manifest вести stable IDs: requirement→domain contract→operation→recipe→attempt→assembly→evidence. До зовнішніх JSON/джерел додати digest і залежності; зберігати одну authority задуму. Спільне [ядро](cross-domain-core.md) визначає докази й execution records; поточний файл додає семантику створення навичок.

Для capability вказати exact operation, tool/model/host/target/version, схему параметрів, supported IO, editable source, limits, права/дані/вартість, unsupported flags, спосіб перевірки матеріальних параметрів і fallback. Descriptor/schema/catalog/configured/tested/integrated — окремі факти. Наявність CLI або назва моделі не підтверджує придатність результату.

Recipe містить exact accepted inputs/hash, competence/owner/consumer, ordered steps/DAG, bound argv array/API або numbered GUI actions, output formats/masters/derivatives, transformations, validators/oracles, budget/effect scope, repair/stop. Шаблон не виконується: спочатку bind до конкретного проєкту й фактичного toolchain. API timeout із невідомим зовнішнім outcome спочатку reconcile за request/effect ID, потім вирішувати retry.

Для кожного запуску створити attempt/effect identity перед side effect, зберегти input/toolchain/recipe digests, фактичні arguments, seed лише коли підтримано, job/run refs, append-only observations, actual outputs/hash/cost і achieved proof. Не вбудовувати ці мінливі значення в reusable skill. Assembly фіксує exact пакет/версію/конфігурацію, компоненти, виконаний сценарій, expected/observed, actual authorship/review, modality і unresolved gaps.

## Три виробничі рецепти конструктора

### R-SK1: вимога → предметний контракт → навичка

Вхід: accepted requirement registry, vocabulary, current capabilities, constraints і approval scope. Кроки: перевірити applicability; вибрати первинну методику; написати typed contracts/scenarios; визначити stage/competence/consumer; побудувати child SKILL+resources; звірити local links/CLI й lineage; виконати negative/positive cases; передати cold receiver. Вихід: installable source, child manifest, exact tests/review, gaps, next action. Source→prompt transformation зберігає must, scope, права й заборонені спрощення; стислий текст не має губити зобов'язання. Acceptance: receiver виконує приклад без домисленого правила, контрприклад належно відхилено, успадковані IDs повністю зіставлено. Не створювати runtime замість навички за відсутності такого доручення.

### R-SK2: сімейство → самостійні етапи → handoff

Вхід: точна stage graph і contract ownership. Кроки: виділити справжні межі артефактів/доступів/незалежного повторення; призначити одного owner кожній authority; зробити самодостатні версійовані common resources; для кожного edge визначити input/output format, hashes, consumer validation, failure/reopen; перевірити пакет без sibling paths і без історії чату. Вихід: окремо встановлювані skills, спільний manifest/lineage, positive handoff і negative missing/stale dependency. Acceptance: downstream не повторює вже прийнятий research і не приймає неповний upstream; return upstream зберігає рішення/оригінали, відкриває точні affected IDs. Не встановлювати все сімейство лише заради одного вузького етапу.

### R-SK3: зміна → перевірка → збереження Work/Codex

Вхід: чинна навичка/blueprint, exact user request, accepted originals, versioned backup і operation capabilities. Кроки: inventory перед редагуванням; semantic diff і coverage preservation; скопіювати лише потрібні reusable ресурси; виконати quick_validate/consistency/предметні tests; bounded independent forward-test без підказок; зберегти одну skill operation штатним Skill Creator; verify exact saved content. Codex export пакує ті самі sources з manifest/hash, audit/apply/verify/rollback; не змінює project data/production. Acceptance: немає dropped must, unapproved external mutation, прихованої sibling dependency або непідтвердженого перенесення готовності попереднього результату. Не називати Work update успішним до перевірки збереженої версії.

## Докази й зміни

Зберігати schema/byte/ref/arithmetical PASS окремо від domain semantics, правдивості джерела, UX/perception, actual deployment або operational результату. Незалежність — властивість фактичних actors і artifact provenance, не слова QA у назві файлу. Тести конструктора не доводять працездатність усіх майбутніх дітей; дитяча навичка має власні cases й приймання.

Після зміни пройти dependency closure за semantic inputs, source/model/exporter/toolchain/platform/config versions. Carry-forward дозволено лише для явно незмінної області; stale receipt не покриває новий результат. Дві однакові невдалі repair спроби потребують іншої причинної гіпотези й діагностики; budget/stop запобігає нескінченним генераціям. Після зупинки лишити checkpoint з actual files, version/hash, completed/pending/blocked, external unknown outcome й next action.
