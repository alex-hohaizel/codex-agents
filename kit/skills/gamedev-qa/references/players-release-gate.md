# Людські тести та рішення про випуск

## Що потребує людей

Fun/feel, зрозумілість керування, змістовна варіативність, бажання ще однієї спроби, тривала мотивація, комфорт haptics/audio і perceived fairness не доводяться самим code/model review. AI може знайти логічний ризик і підготувати тест; actual human observations мають власний статус.

## Playtest protocol

Заздалегідь сформулювати питання й falsifiable criteria. Вибрати relevant audience/accessibility/device mix, describe actual recruitment/consent. Учасникам дати raw game/task без рекламної підказки expected reaction. Не пояснювати механіку під час first-use, якщо це не частина протоколу. Не збирати зайві personal data.

Приклади:
- New player без допомоги розуміє goal/input/failure і знаходить retry/next goal.
- Після кількох runs може описати нові decision tradeoffs, а не лише іншу картинку.
- Після поразки розуміє власну помилку й доступний free improvement path.
- Paid mechanical variant сприймається з ясними tradeoffs; неплатник не відчуває прихованої штучної перешкоди.
- Returning player знаходить нову мету й не губить progress/content context.

Зберігати actual sample size, recruitment bias, session length, build/device, task, observations/timecodes, quotes за згодою, dropoff/assistance, conclusions та limitations. Малий formative тест ловить проблеми, але не прогнозує D7/LTV на ринку. Поздовжній тест потребує реальних повторних заходів у часі; одноразове «я б повернувся» не є retention.

## Монетизація й fairness

Simulation видає acquisition time/price/reward outcomes під assumptions. Людський тест виявляє comprehension/pressure/fairness; live cohort дає фактичні conversion/refunds/revenue/retention. Не змішувати. Жоден рівень не гарантує успіх. Негативні відповіді не переписувати як позитивні; повернути mechanism issue до відповідного design owner.

## Full-stage verdict

Узгодити exact product scope і platforms. Для кожного must є current verdict/evidence або explicit blocker. Прийняття потребує належної незалежності, actual native/platform checks, fidelity/craft review, data/commerce/privacy checks, required human evidence та відсутності unresolved release-blocking defects. Умови по human evidence залежать від claimed stage: beta може збирати невідоме; це не підтверджений market success.

Статуси:
- `accepted_for_named_test`: дозволена конкретна beta/test ціль, remaining hypotheses відкриті.
- `accepted_for_release_review`: технічні/продуктові gates прийняті у названому scope; `gamedev-release` перевіряє актуальний store setup/submission.
- `blocked`: missing required evidence/defects/rights/signing/platform.
- `scoped_complete`: локальна перевірка завершена; не вся гра.

Не створювати вічний цикл «ще одна рада». Після закриття named scope повторно відкривати лише за новою зміною, новим evidence, залежністю або invalid prior claim. User може обрати beta з конкретними невідомостями; не маскувати її як full release-ready.

## Handoff до release

Accepted exact source/build, sanitized evidence manifest, requirement matrix, per-platform status, known issues, store policy snapshot, rights/brand bundle, privacy/data map, store SKU/contracts, migrations/rollback, test-access instructions і next action. Production publish потребує окремо чинного дозволу на external action; QA verdict не створює такий дозвіл.

## Learning transfer і різноманітність 4.0

Для кожного суттєвого навченого вміння виділити teaching/practice/transfer tasks. Transfer — новий контекст із тією самою причинною логікою без повторної інструкції, якщо саме так спроєктовано гру. Фіксувати actual success/error/assistance/time й пояснення гравця; невдалий перенос повертати owner навчання/читабельності, а не переписувати як успіх за tutorial completion. Порогові значення визначати до тесту за ризиком і аудиторією, не нав’язувати універсальні секунди чи sample counts.

Для варіативності показати contexts із різними constraints і спостерігати фактичні рішення/контрдії/компроміси. Не підказувати бажаний build. Відрізняти доступність/вивченість опції від її сили. Для добровільного повернення запропонувати видимі цілі, записати actual вибір і пізніший візит за окремим longitudinal protocol; відсутні повторні візити не вигадувати.

## Failure, reorientation й допомога

Спостерігати, чи учасник розрізняє прочитане правило, доступну контрдію, recognition defect і помилку виконання; failure cause/recovery повинні давати наступний осмислений крок. Після реальної перерви перевірити goal/context/loadout reorientation без повтору всього tutorial.

Assists мають явні semantics/scoring/persistence і compatibility;не припускати універсального позбавлення нагород за доступність. Paying/free participants оцінюють саме погоджену power/time/access policy;допустима перевага документується,а hidden baseline harm не підміняє монетизацію.
