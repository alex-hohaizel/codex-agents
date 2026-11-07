# Лор, знання й реактивна оповідь 4.0

## Навігація

1. Scope і канон
2. Знання та причинність
3. Квести/діалоги/сцени
4. Інтеграція й save
5. Cold receiver і контрприклади

Вести цей напрям як окрему компетенцію, навіть якщо наратив подається через короткі environmental signals. Глибина лору визначається впливом на досвід, не кількістю сторінок. Novel/dialogue/branching campaign не додаються кожній грі автоматично.

## 1. Зафіксувати narrative scope

На C1 визначити fantasy/theme/tone, обіцянку світу, player role/motivation, основний конфлікт, temporal/spatial structure, character/faction identities, важливі world rules, stakes/failure/recovery, progression arc, optional discovery й ending/replay. Пояснити, як це змінює gameplay decisions, середовище/AI/art/audio, а не лише фоновий текст.

На T передати canon/knowledge/state tables, quest/dialogue/scene graphs за обсягом, conditions/priorities/effects, localization resources, interruption/resume, save/migration і fixtures. Для authored сцени exact staging/sequence/camera/input restrictions повинні співіснувати з dynamic-control brief, а не мовчки підміняти його.

Canon fact record: stable ID/version, proposition, truth conditions, relevant time/region, initial state, allowed mutations/owner, cause/effect refs, conflicts, knowledge holders, gameplay dependencies, presentation refs і tests. Відділити незмінний канон від mutable world state, rumor і editor-only note.

Підтримати glossary/voice/style і content restrictions за проєктом. Назви/терміни мають stable localization IDs; переклад не створює новий quest/item identity.

## 2. Відокремити truth і знання

World truth може бути невідомою player/NPC. Knowledge fact: subject, predicate/value, source/channel, observed time, uncertainty/confidence, lifetime, refresh/forget/share rules і disclosure conditions. Непідтверджене припущення персонажа не змінює фактичний стан.

AI perception й narrative knowledge використовують узгоджені факти, але не обов’язково один storage runtime. Розмова не повідомляє NPC таємницю до фактичного dialogue choice. Гравець не отримує spoiler через reason inspector або локалізовану назву locked quest.

Causal edge: condition→player/world action→commit→world change→observation/knowledge→new action/opportunity. Перевірити time travel/flashback/процедурне замовлення лише якщо вони є задумом; unguarded reorder не має створювати суперечність.

Death/revival, repair, scarcity, faction memory, world destruction і repeated attempts повинні мати наративно узгоджену семантику. Quest «останній ресурс» не співіснує з необмеженим сусіднім продажем без пояснення. Boss return не воскресає випадково через restore.

## 3. Описати кожну quest/dialogue/scene

Для node/edge задати:

- ID/version/purpose, source requirements і owner/consumer.
- Prerequisites: world, progression, knowledge, actor availability, content ownership.
- Eligibility/priority/tie-break, mutually exclusive alternatives, repeat/once scope.
- Entry/exit, speaker/participants, location/time, staging/camera/input policy.
- Player choices: preview, commit, irreversible boundary, cancel/timeout/default.
- Exact effects: flags/resources/rewards/relationships/route/unlocks/knowledge.
- Interruption, actor death/missing, scene exit, pause/resume, abandon/retry.
- Localization/voice/subtitles/animation/UI bindings і non-audio alternative.
- Save consistency group, migration/remap і golden cases.

Choice labels мають правдиво сигналізувати commitment/stakes; не вимагати усвідомлення прихованого irreversible effect без задумного й читабельного правила. Не кожний вибір мусить створювати гілку, але його роль і наслідок мають бути визначені.

Scene arbitration має впорядкувати одночасні prompts, quest completion, combat danger, boss intro й tutorial. Визначити, що переривається/відкладається/скасовується, як повертаються камера й input ownership. Late queued line не вимовляє вже неправдивий факт після world change.

Для процедурного наративу задати grammar/templates/variable domains, knowledge guards, canon constraints, localization agreement, novelty/history, bounded generation/repair/fallback. Не дозволяти unconstrained generated text змінювати authoritative world rules або видавати reward. LLM не є обов’язковим NPC runtime.

## 4. Інтегрувати з усіма релевантними системами

Світ: geography/landmarks/routes/return і persistent aftermath. AI: goals/faction knowledge/perception/allowed actions. Каталог: культурна/функціональна причина інструмента й acquisition. Progression: відкриття через досвід, не лише текст. Economy: scarcity/sources/sinks/rewards. Commerce: paid access не породжує канонічну суперечність або неможливий сюжетний state.

Art/audio: silhouettes/material language/architectural rules/leitmotifs/ambient reactions/voice; для кожного canonical meaning є realized resource або визначений виробничий маршрут. UI/learning: спойлерні межі, objective clarity, remind-on-return. Save: flags/relationships/knowledge/consumed choices/rewards причинно узгоджені.

Для content availability/DLC/locale/actor absence зафіксувати fallback, blocking prerequisites і migration. Не змінювати сюжет мовчки при оновленні каталогу. Старий save з removed quest ID проходить явний remap/compensation або зрозумілу несумісність без очищення профілю.

Whole-branch/семантичний merge не має одночасно створювати mutually exclusive endings. Quest reward, resource spend і resulting flag належать одній consistency group. Replayed cutscene не видає reward повторно; narrative animation callback не є authority.

## 5. Холодне приймання й negative cases

Передати новому отримувачу canon, exact state, accepted versions і scene/quest graph без історії чату. Попросити реконструювати: player motivation; що відомо кожному actor; доступні choice; exact outcome; interruption/resume; return reminder; completion і restore. Отримувач називає необґрунтовані знання/додумані правила й власний контрприклад.

Негативні fixtures:

- NPC знає secret до observation/share event.
- Розмова відкладена до смерті адресата; queued line не відтворюється як актуальна.
- Mutually exclusive quest flags з двох offline saves.
- Reward/flag/cost розділилися після kill у commit boundary.
- Boss dead, але faction/route state залишив старе незавершене завдання.
- Paid content відсутній, save має його предмет/quest; fallback зберігає причинність.
- Translation змінила identity/умову або placeholder приховав важливий choice.
- Cutscene interruption залишила locked input/camera або повторно видала grant.
- Player повернувся після перерви: objective ясна без spoiler чи повного tutorial.
- Procedural template створив canon contradiction або invalid knowledge.

Review приймає причинну узгодженість scoped пакета, а не доводить драматичну силу/залучення. Narrative pacing, зрозумілість stakes й emotional experience потребують real human sessions із записаними limits.

## Джерела

Методика є адаптацією P1/D1/D2; опорні матеріали досліджено2026-11-02. Actual runtime/plugin обирається окремо під проєкт.

- MDA, mechanics→dynamics→experience: https://www.cs.northwestern.edu/~hunicke/MDA.pdf
- W3C SCXML, state/event/transition semantics: https://www.w3.org/TR/scxml/
- Dormans, mission/spatial grammar: https://www.pcgworkshop.com/archive/dormans2010adventures.pdf
- Epic AI Perception, knowledge acquisition boundary: https://dev.epicgames.com/documentation/unreal-engine/ai-perception-in-unreal-engine
