# Concept 4.0: дослідження й доказова різноманітність

Читати [research domain](domains/research.md) та [Game Model workflow](game-model-workflow.md). Дослідження має змінювати рішення, а не лише додавати список джерел до вже згенерованої ідеї.

## Доказ для конкретної задачі

Для кожної суттєвої тези записати питання, primary source/дата/версія/регіон, спостережений факт, дизайнерський висновок, невідоме, applicability до кандидата, strongest alternative explanation і наступний discriminating test. Позначати direct observation, developer claim, estimate, own hypothesis і measured own result окремо. Чужий revenue/retention не стає показником кандидата; installation count не доводить причину успіху.

Порівнювати релевантні успішні та контрприклади за audience, core action, session loop, knowledge/progression/reward structure, world/content grammar, camera/input, art production, monetization/store journey, content cadence/operating cost і distribution/IP/marketing. Публічна інформація може не розкривати odds, prices, cohorts чи всю економіку; пропуск залишати explicit, а не заповнювати здогадом. Не обіцяти буквально exhaustive survey усіх існуючих ігор.

Вивчати механізми commerce докладно: що/коли відкриває бажання, earned/paid/capped path, currency sources/sinks, recurrence/expiry, presentation/confirmation/grant/use, restore/refund/decline/offline/no-fill. Потім порівнювати моделі за fit до гри та production capacity. Жодна одна sidegrade/skin/booster модель не є універсальною. Store/payment/ads/privacy/age/market rules перевіряти актуальними офіційними джерелами перед залежним design/release.

## Портфель концептів

Використовувати [portfolio authoring aid](../assets/domain-templates/portfolio-review.template.json). Спочатку визначити незалежні осі й потенційні прогалини; потім створювати coherent candidates, які мають причину існування. Genre × camera × art × commerce не перемножувати як randomizer. Числа квот можуть бути constraint користувача, але не доказом різноманітності.

Розрізняти:

- **Ідентичність:** чи повторює кандидат core causal kernel/фантазію/цілі іншого під новою назвою/декором.
- **Різноманітність:** чи різняться дії/рішення/ритм, camera/framing/input, розвиток/світ, художня мова й комерційний fit у всьому наборі.
- **Здійсненність:** чи підтримується обіцянка конкретним маршрутом у реальних ресурсах.
- **Привабливість:** чи хочуть реальні люди цей досвід; AI review не є людським доказом.

Для кожного найближчого сусіда пояснити meaningful differences і спільні мотиви. Semantic novelty review порівнює actual content, не тільки names/keywords чи точні JSON duplicates. Не вимагати штучної абсолютної новизни: доведені патерни можна комбінувати, якщо складена гра цілісна й не копіює чужу IP/арт/персонажів. Shared motif визнавати чесно. Review портфеля окремий від individual must-readiness; pass відсутності копії не закриває одноманітності camera/art/controls.

Фактичний R6 демонструє корисні negative controls: різні genre labels із подібною композицією, повторене finite scope число, один repeated offer family й camera-size default. Використовувати історичні originals як джерела тестів із lineage; не переписувати старі approvals і не оголошувати всіх старих кандидатів неякісними одним score.

## Первинні приклади для відновлення контексту

Нижче історичні методичні посилання з комплекту 2.1, перевіреного 01.11.2026. Перед новим предметним висновком перевірити актуальну сторінку/версію; це не live каталог і не підтвердження нинішньої комерційної ефективності.

- Dead Cells: https://deadcells.com/ — зміни замку, pattern-based combat, різні weapons/spells, nonlinear routes/exploration як приклад сплетення mastery/інструментів/світу, без копіювання їхньої структури кожній грі.
- Vampire Survivors: https://poncle.games/vampire-survivors і https://poncle.itch.io/vampire-survivors — розрізнення run choices/snowball і persistent upgrades, без нав'язування жанру.
- Acecraft developer listing: https://play.google.com/store/apps/details?hl=en_US&id=com.vizta.weflyam — заявлені random skills, absorption, stages/co-op; developer claim не є нашим playtest.
- Moonton seasonal descriptions: https://en.moonton.com/news/275.html і https://en.moonton.com/news/284.html — історичні pilots/world/co-pilots, сезонні playstyles/resources/banner guarantees. Не переносити поточні odds/доступність на іншу версію/регіон.
- Official storefront: https://apps.apple.com/us/app/acecraft-sky-hero/id6746043251 — offer families/version notes, без гарантії повної економіки або «не P2W».

Офіційний media asset не дає права копіювати його в production. Web search/metadata не називати переглядом відео або грою. Технічні способи реалізації перевіряти за документацією виробника/рушія й actual capability, не статтею про зовні схожу гру.

## Review і human tests

Для кожного due must надати mechanism, strongest objection, actual evidence/limitations, unresolved gap і next test. Independent review виконує інший actual actor; roles у тексті не створюють доказ. У skill forward tests давати task-local prompt/raw inputs і оновлену навичку без бажаного висновку; перевіряти переносимість на різні жанри/масштаби/камери/commerce, не один підготовлений приклад.

Human protocol визначає objective, recruitment/consent, n/відмови, horizon, help/reminders, raw outputs, критерій спростування й limits до висновку. Friendly sample не доводить mass market. Immediate retry, самостійна нова спроба й return after pause — різні events. Синтетичні visits1/5/20/50 — модель, не observed cohorts.

Для commerce/retention experiments формулювати causal question/control, randomization за можливості, зрілі cohorts, guardrails/stop/uncertainty. Не встановлювати універсальний D1/ARPU threshold як факт без контексту. Публікація, платний acquisition або external player outreach потребує відповідного scope; план дослідження сам не виконує ці дії.

## Порівняння систем, а не лише genre labels

Для кожного дослідженого прикладу розділити спостережувані gameplay/AI/failure/progression/commerce mechanics, документовану реалізацію, комерційний результат і власний inference. Відсутня інформація — gap, не нульове значення. Вивести testable design hypothesis і counterexample для нашої гри.

Перед дорогим generation порівняти C1 кандидатів за decision space, session/topology/camera/input/art, системами розвитку/ризику/нагород і operating cost. Бібліотека monetization охоплює метасистеми, functional bundles/partial ownership та cumulative portfolio; не змушувати всі ігри продавати одну sidegrade чи мати магазин.
