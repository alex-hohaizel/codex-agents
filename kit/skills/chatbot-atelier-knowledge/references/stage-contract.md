# Контракт етапу chatbot-atelier-knowledge

## Видимий результат і застосовність

Визначити доречний scope й достатній спосіб роботи за [адаптивною роботою](adaptive-work.md); адресне [дослідження та синтез](research-and-synthesis.md) доступні на будь-якому етапі. Нижче наведено предметний метод ролі, а набір активних функцій/платформ/персони задає погоджений project profile. Зберігати чинні IDs, права, прийняті результати й повний намір; нові правила не створюють заднім числом reviews. Для local repair застосувати лише зачеплений маршрут і належне чинному gate приймання.

Показати карту джерел і власників, правила audience/ACL/freshness/retention, альтернативи retrieval та належні evals. Перенесення між чатами/проєктами перевіряти за фактичним доступом; summary або embedding не розширює права і не підміняє первинний контекст.

## Обов’язковий предметний маршрут

## Модель пам’яті

Розділити session/task/durable personal/group/workspace knowledge. На факт: authoritative source IDs/versions, observed vs inferred, author/actor/audience/purpose, validFrom/Until, timezone за потреби, correction chain, confidence/verification, retention/consent/privacyEpoch. Похідні summaries/views/embeddings не створюють ширшого дозволу. Разове/денне побажання не стає постійним профілем; цитата/питання/заперечення не автоматичне право запису.

Для correction/conflict визначити owner і precedence: пряме authoritative виправлення проти старого summary, freshness/expiry, ambiguous identity. Природний запит «пам’ятай/забудь/не зараз» пов’язати зі scope й actual state; не нав’язувати технічний режим. Не заявляти, що бот бачить Work/Codex/Telegram контекст без фактичної lineage/доступу.

## Retrieval лише за потреби

Почати з питань/corpus/ground truth і перевірити, чи достатньо current context/звичайного search/SQL. Якщо RAG active: ingestion/parse/chunk/index/filter/rerank/citation/abstention/delete/reindex lifecycle, ACL до exposure, source freshness і units/language. Framework/vector DB — кандидати, не критерії якості. Tool result/document prompt injection не підміняє policy/permissions.

Вимірювати retrieval relevance/recall/precision, answer attribution/factuality, abstention й cost/latency окремо на frozen cases. Cache keys включають source/parser/chunker/model/ACL/version; version change інвалідує залежні claims. Source-access revocation і private DM мають негативні probes для cache/search/summary/export.

## Erasure/restore та перевірка

Lineage cascade primary data→summaries→embeddings→indexes/views/cache→pending/running jobs→prompts→outputs/media/exports. Privacy epoch/tombstone guards перевіряються перед commit і delivery пізнього result. Старий backup при restore має застосувати current tombstones; фізичне стирання immutable backup за фактичною retention policy, не вигадане миттєве.

Позитивні/негативні сценарії: cross-chat/tenant/topic read/write, corrected fact, temporary preference, forget during running, late embedding, cached deleted snippet, revoked tool source, old restore. Вихід: data/ACL/retention/schema/migration contracts, actual deletion trace, retrieval evals, backup/restore limits й receiver. Не використовувати production private transcripts за тестову базу.

## Контракт передачі

Передавати stage_id/requirement IDs/source IDs/exact version/hash, applicability із причиною, formal typed rules/states/перетини, capabilities/rights, operation passports/recipes/effective params, actual attempts/jobIDs, outputs/consumer, evidence/proof limits, negative scenarios, unresolved, receiver і next acceptance. Отримувач відтворює висновок без історії чату; несумісний input або нездійсненний requirement повертається upstream адресно.

## Критерії та завершення

Першочергові criterion IDs для перевірки застосовності: audience_privacy, source_grounding, forgetting_integrity, consent_authority. Зберегти всі24 IDs як карту перевірки впливу; active/carried/out_of_scope визначати за чинним profile і scope з доказовою причиною, без видалення погодженого must. Для кожного active must: owner/artifact/positive/negative check/evidence kind/verdict/strongest objection/limitations; unknown критичного claim блокує цей readiness. Автор не незалежний QA. Модельна оцінка не людська/production proof.

Вихід у повному потрібному scope, а не список рекомендацій або stub. Ескіз/специфікація/виробнича передача/інтеграція/live/human proof розрізняються. Після двох повторів без нових доказів змінити diagnostic hypothesis; не знижувати критерій через вичерпаний бюджет.
