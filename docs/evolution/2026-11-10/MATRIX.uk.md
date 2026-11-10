# Кожна вимога та її шлях реалізації

Усі27 вимог відкриті для цільової реалізації до точного погодження паспорта0.2 і фактичного доказу. Початкові17 можливостей збережено; пріоритет змінює лише черговість.

[Passport / Паспорт](PASSPORT.uk.md) · [JSON](REQUESTS.json) · [Acceptance / Приймання](ACCEPTANCE.uk.md) · [Real tasks / Реальні задачі](REAL-TASKS.uk.md)

| ID | Requirement / Вимога | Owner / Власник | Stages / Етапи | Acceptance / Приймання |
| --- | --- | --- | --- | --- |
| R01 | Будувати AI-інструменти end-to-end: від збору даних і ML/LLM-логіки до бекенду, UI та деплою, щоб нетехнічні команди користувалися ними самостійно; | Current product integrator with backend/integration/QA work packages | S1, S3, S4, S5, S7, S8 | A01, A02, A07, A15, A16, A23, A27 |
| R02 | Налаштовувати надійні системи збору даних із зовнішніх джерел — гнучкий скрейпінг платформ та інтеграції з API; | Current integration/backend/knowledge owner | S4, S5 | A02, A03, A04 |
| R03 | Автоматизувати обробку даних: кластеризація, NLP-аналіз відгуків, моніторинг трендів; | Current research/growth/knowledge owner | S4, S5 | A05, A06 |
| R04 | Розробляти кост-ефективні пайплайни для масштабної генерації ідей, текстів, зображень і відео під бізнес-задачі; | Current creative/product owner with cost review | S4, S6 | A07, A12, A13, A26 |
| R05 | Будувати предиктивні моделі для прогнозування бізнес-метрик — наприклад, CPA рекламного креативу ще до запуску; | Current implementation owner with ML work package and independent QA | S4, S5 | A08, A09, A10 |
| R06 | Доводити внутрішні прототипи, зокрема створені нетехнічними колегами за допомогою AI-асистентів, до production-ready інструментів. | Product integrator + backend/reliability + evaluation | S3, S7, S8 | A15, A16, A17, A23, A27 |
| R07 | Здатність вільно рухатися по всьому стеку: від ML-моделей і бекенду до UI та деплою, без прив’язки до вузької спеціалізації; | Orchestrator + dynamic product team | S3, S4, S5, S6, S7 | A01, A15, A16, A23, A27 |
| R08 | Міцний технічний фундамент: мова чи фреймворк не принципові, важливі системний дизайн, структури даних, дизайн, якість результату, і смак до чистого коду; | Architecture + backend + product craft owners | S1, S2, S3, S4, S5, S6, S7, S8 | A01, A14, A15, A23, A27, A28 |
| R09 | Практичний досвід із LLM (OpenAI API, LangChain або LlamaIndex, prompt engineering) та розуміння ML-концепцій — кластеризація, класифікація, ембеддінги; | Current AI application/knowledge owner | S4, S5 | A05, A06, A07 |
| R10 | Впевнене та постійне використання AI-кодинг-асистентів (Cursor, Claude Code, Codex) як базового стандарту роботи; | Orchestrator + constructors + coding-assistants contract | S1, S4, S7 | A18, A19, A23 |
| R11 | Проактивність і швидкість: здатність взяти задачу на рівні бізнес-ідеї та зібрати з неї MVP, або продукт будь якого рівня складгості і предметної області як без детального ТЗ, так і супроводжувати у його проектуванні протягом розробкт | Orchestrator + existing product integrator + constructors | S1, S3, S7, S8 | A01, A19, A23 |
| R12 | Досвід створення складних AI-агентів (Agentic workflows, LangGraph) або мультимодальних пайплайнів як для згаданих вже видів задач, предметних областей, так і із генерацією зображень, моделей, аудіо будь якої складності і призначення, асетів для додатків, ігор, засутнків, і відео; | Current integration and domain creative owners | S4, S5, S6 | A07, A12, A13, A14, A26 |
| R13 | Практика побудови предиктивних ML-моделей (XGBoost, LightGBM, нейромережі) на табличних даних чи часових рядах; | Current implementation owner with ML work package | S4, S5 | A08, A09, A10 |
| R14 | Досвід оптимізації або донавчання open-source моделей (LoRA тощо); | Current implementation owner with ML adaptation work package | S4, S5 | A11 |
| R15 | Повноцінне створення та запуску власних продуктів з нуля: мікро-SaaS, Telegram-боти чи пет-проєкти, застосунки, ігри для будь якої платформи мобільної з будь яким рівнем складності і якості візуалу з реальними користувачами. | App/ChatBot/Game directors + release/operations | S2, S3, S6, S7, S8, S9 | A01, A14, A16, A23 |
| R16 | Відчуття стилю дизайна створення асетів будь якої складності з повним циклом їх використання і розвитку у продукті згідно усіх сучасних методологій | Existing App experience Game assets or ChatBot media owner | S2, S3, S6, S8 | A12, A13, A14, A15, A26, A27 |
| R17 | Розуміння складу сабагентів необхідних команд у агентах, їх продуктивної взаємодії і спільної роботи з розумінням повного циклу створення, супроводу і розвитку продукту | Existing constructors and current product integrator | S1, S4, S7, S8 | A01, A18, A19, A23, A28 |
| R18 | Зберегти чинні можливості, ідентичність і налаштування. | Maintenance + installers + QA | S0, S1, S2, S3, S4, S7, S8, S9 | A20, A21, A22, A25, A28, A29 |
| R19 | Мені потрібне системне оновлення тебе, усіх агентів, навичок, пов'язаних конструкторів агентів тощо. Усього, що ми зробили. | Orchestrator + constructors + maintenance | S1, S4, S7, S9 | A18, A19, A20, A21, A24, A25, A27, A28, A29 |
| R20 | Повна детальна подробна і головне вичерпна документація щодо кожного елемента, як саме він реалізован, де, і що це дає, як він активується за якими вимогами. Доступною людською не ші мовою. І все це має бути збережено в документацію гіт хаб проекту агентної системи | Documentation owner + independent review | S9 | A24 |
| R21 | Спершу наявні доступи; нові витрати погоджувати | Integrator + cost + provider adapters | S0, S3, S4, S5, S6, S7, S9 | A04, A07, A11, A13, A17 |
| R22 | WORK продовжимо після відновлення доступу. | Maintenance + host bridge | S0, S7, S9 | A18, A24 |
| R23 | Фактична реалізація та окремі докази source/installed/discovered/executed/reviewed/accepted; статична демонстрація не закриває сервіс. | All current artifact owners and independent QA | S1, S2, S3, S4, S5, S6, S7, S8, S9 | A01, A11, A12, A15, A19, A23, A24, A26, A27, A29 |
| R24 | пріоритет — контекст, дизайн і робоча панель | Current product integrator + experience + QA | S0, S1, S2, S3, S8 | A01, A12, A15, A19, A21, A23, A25, A26, A27, A29 |
| R25 | збережи всі можливості, прибери зайву складність | Orchestrator + constructors + architecture | S0, S1, S4, S7, S8 | A01, A07, A11, A18, A19, A20, A24, A28, A29 |
| R26 | Якщо буде мати місце десь щодо регрессії, тоді не треба додавати такі покращення в жертву чомусь іншому, що вже працювало. | Current integrator + independent QA + release | S0, S1, S2, S3, S4, S5, S6, S7, S8, S9 | A01, A02, A03, A04, A05, A06, A07, A08, A09, A10, A11, A12, A13, A14, A15, A16, A17, A18, A19, A20, A21, A22, A23, A24, A25, A26, A27, A28, A29 |
| R27 | Додай перевірку покращень на реальних задачах і збережи все в GitHub. | Current product integrator independent QA and maintenance | S0, S1, S2, S3, S7, S8, S9 | A01, A12, A15, A19, A21, A23, A24, A25, A26, A27, A28, A29 |
