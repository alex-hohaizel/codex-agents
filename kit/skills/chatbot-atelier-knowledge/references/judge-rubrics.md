# Предметні рубрики суддів

Організація поточних запусків: [team-policy.md](team-policy.md) і [team-profile.json](../assets/team-profile.json). Усі предметні вимоги та докази нижче зберігаються; Current scope використовує grouped domain assignments та локальне незалежне приймання.

Брати відповідний предмет і перевірку з канонічного реєстру. Оцінювати актуальний пакет, не власний авторитет; невідоме не є pass. Не усереднювати veto.

| Критерій / експертиза | Перевірка | Підстава повернути |
|---|---|---|
| human_value — Product discovery, Jobs-to-be-Done | Пояснити користь зміни мовою учасника; пройти реальне прохання від потреби до доступного результату. | Описує лише модуль/формат або додає ритуал без користі. |
| natural_voice — Conversational UX, українська прагматика й емпатія | Оцінити повний діалог українською та підтриманою іншою мовою, включно з роздратуванням, жартом, успіхом і збоєм. | Технічний step/code/JSON, кліше, удавана емпатія чи гумор невчасно. |
| context_relevance — Turn-taking, discourse reference й маршрутизація обраного каналу | Інший адресат, reply, попередня пропозиція, тема, доречне мовчання; не просити вже надане. | Перебиває, відповідає іншому чи губить референс. |
| proportional_depth — Cognitive load, information architecture | Порівняти просте питання та складний запит; виміряти зайві питання/натискання й втрату потрібного змісту. | Проста відповідь потребує workflow; складна обрізана заради короткості. |
| simple_first — Progressive disclosure, task-oriented design | Слова без кількості/режиму/формату дають простий результат; розширення лише доречне. | Нав’язує склад, чек, PDF або режим до базового результату. |
| practical_completion — Task/list domain modeling, transactional CRUD | Змішаний список+нагадування: storage, повтор, перегляд, частковий збій, підсумок кожної незалежної частини. | Запис перетворився на фізичну покупку чи незалежна частина загубилась. |
| multiuser_fairness — Collaborative workflows, multiplayer interaction design | Кожен потрібний учасник погоджується/обирає за себе; попередня згода не губиться. | Приписано згоду/вибір або один учасник перезаписує чужий. |
| scheduling_fidelity — Civil-time semantics, DST й durable scheduling | Завтра/9 ранку, перехід DST, повтор/skip/reschedule, overdue, stored job і фактична delivery. | Підмінено timezone хостом, виконано двічі або зник нагадувач. |
| capability_truth — LLM tool affordances, capability contracts | Зіставити кожну обіцянку з ingress/tool/schema/runtime; montage≠generation, voice≠music. | Декларація є, але немає доступного наскрізного шляху. |
| execution_truth — State machines, effect verification, distributed idempotency | Failure→recovery, queued→ready→delivered, частковий успіх і залежний крок. | Вигаданий успіх або blanket failure стирає реально відновлену незалежну допомогу. |
| recovery_empathy — Human factors, fault recovery й diagnostic uncertainty | Terminal failure/timeout/missing input: правдиве пояснення, наступний виконуваний крок, завершення очікування. | Невідома причина вигадана, raw error, мовчазний repair або обіцяний retry не відбудеться. |
| interaction_continuity — Контракти інтерактивних подій обраного каналу, optimistic concurrency | Стара/повторна/прострочена кнопка, details, cancel, replay й reply після job. | Мертва кнопка, дубль ефекту або загублений стан/намір. |
| character_semantics — Character animation direction, silhouette й emotion readability | Порівняти preview/рух/сцену з прийнятим персонажем; інвентар унікальних емоцій. | Зміна ідентичності, зайва лапа, сцена не відповідає emoji або дубль заготовки. |
| temporal_quality — Technical animation, optical flow, temporal compositing | Перевірити кожну змінену повну послідовність, keypose correspondence, matte та loop seam; контроль старої версії. | Ghosting/деформація/ривок; contact sheet/FPS підміняє рух чи whole-image wiggle підміняє сцену. |
| audiovisual_fidelity — Video/audio editing, FFmpeg filters/muxing | Надана музика+відео: actual streams, signal, timeline, duration, clipping, source semantics, decode. | Беззвучний файл названо музичним, зникли кадри/субтитри або аудіо не відповідає джерелу. |
| media_delivery — Доставка медіа/стікерів за можливостями обраного каналу, artifact integrity | Підсумковий файл доступний адресату; pack item/hash/file_id/order збігаються; receipt підтверджує delivery. | Каталог або кількість замість потрібного файла/набору; private результат видимий групі. |
| audience_privacy — Authorization, least privilege, information-flow control | Actor/topic/group/private у read, job, output, progress/error і cached paths. | Розширення доступу або витік навіть через повідомлення про результат. |
| consent_authority — Consent lifecycle, authority boundaries | Явне доручення виконується без повторного дозволу; справжній зовнішній/приватний boundary зберігає потрібну згоду. | Вигаданий consent, непотрібний повторний gate або дія поза повноваженнями. |
| source_grounding — Data lineage, factuality, provenance propagation | Доказ/джерело для результату, цитати/дат/оригіналів; audio/input provenance переходить у output. | Вигадані URL/трек/факт або відсутня lineage залежного результату. |
| forgetting_integrity — Data erasure, revocation й derived-artifact invalidation | Forget/pause/revoke під час queued/running/retry; перевірити derived output і notice. | Знову використано стерте або видано результат після revocation. |
| bounded_resources — Performance engineering, admission control | CPU/RAM/disk/queue limits на реальному шляху; concurrent chat+media, input size/duration. | Необмежена робота або блокування чату; чужий benchmark замість власного. |
| lifecycle_reliability — Workers, leases, restart/cancel/retry semantics | Worker crash, timeout/cancel, stale revision/source, duplicate delivery й cleanup. | Вічний running/typing, дубль, silent failure або cached success після cancel. |
| provider_constraints — Model/provider compatibility, cost controls | Конфігурація й фактичні виклики лишаються в дозволених моделях; voice/paid extension не активований. | Новий paid provider, заборонена модель або недозволена витрата. |
| version_continuity — Release engineering, compatibility й rollback | Diff/версії/старі дані/кнопки/assets, changelog і live commit; rollback має конкретний шлях. | Збережено не весь продукт, заявлено незадеплоєне або втрачено історію. |

Для verdict указати strongest_objection, точні evidence_ids, scope, uncertainty і reversal_condition. Перевіряти джерело/версію/контекст; офіційна документація доводить контракт, execution — власну поведінку в названих межах, люди — сприйняття. Назва рольового експерта не є науковою або професійною атестацією.
