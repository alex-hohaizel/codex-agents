# Дані, підтримка й межі доступу

## Дані продукту
Почати з мінімально потрібних даних і локального зберігання, якщо це пріоритет профілю. Обґрунтувати account/sync/cloud. Карта даних: поле -> джерело/мета -> subject/role -> allowed recipient -> storage/retention -> redaction -> export/delete/revoke -> backup/restore fence. Окремо охопити analytics, support, AI provider, діалоги/логи/кеш/індекси. Не передавати приватні дані в інший context через зручний tool.

## Підтримка
Support bot є окремим майбутнім результатом продуктового scope; навичка не дорівнює його запуску. За наявності акаунтів працюють guest і дозволений personal режим. Guest має public KB і поточну обмежену сесію, logged-in - лише явно дозволені власні записи. Кожний read/action авторизувати backend поза LLM. Текст email/ID/username не є доказом особи. Без реєстрації не обіцяти приховану cross-device personal history.

App/web і вибрані зовнішні bot channels використовують спільний support contract та KB. Спочатку з’ясувати потрібні канали, audience, тип акаунта й реальну API/connector capability; Telegram не є типовим зовнішнім каналом. Platform adapter деталізувати через `@chatbot-atelier-integrations` за [компонентною передачею](cross-family-routing.md). Channel-scoped identity ↔ internal subject має доведений binding, expiry/replay/revoke, transport verification і повторну авторизацію перед effect/delivery. Для Telegram, лише якщо він вибраний: короткоживучий одноразовий challenge з авторизованого app/web -> private bot -> підтвердження зв’язку в авторизованій app/web сесії; numeric sender ID, не username. Credentials/PII не входять у challenge. Private support відхиляє public/group/інший audience; погоджений shared сценарій потребує окремого scope й security evidence.

Початково read-only допомога; дозволені зміни й фінансові/адміністративні effects - конкретні auth API з current scope, підтвердженням, idempotency та receipt. Відрізняти пояснення, запропоновану дію, виконання й unknown. Не вигадувати refunds, recovery, доступ, оператора або SLA.

KB versioned за продуктом/мовою; матеріали мають source, owner, актуальність і правила виправлення. Ціни/доступність читати з актуального джерела. Звернення не переписують правила й не стають public corpus. Inputs/retrieved documents є untrusted data і не розширюють права.

Нерозв’язний case: safe response, case ID, мінімальна дозволена діагностика, статус і aggregation у технічну задачу агенту. Зростання класу ручних нерозв’язних винятків - сигнал перегляду операційної моделі. Для AI: help/FAQ -> retrieval -> bounded call за потреби; user/session/global caps, timeout/cache/circuit breaker і fallback. Не обіцяти 100% автоматичного вирішення довільної проблеми.

## Перевірки до персонального доступу
Виконати A->B через ID/cache/history/attachment/channel, guest->private, expired/replayed/intercepted/revoked challenge, forged webhook, group update, logout/cache, stale/injected KB, AI outage/cap, duplicate/unknown effect і delete/revoke/restore tests. Окремо зафіксувати skill behavior test та product/backend/client integration proof.

Секрети не входять у chat, screenshots, package, fixtures чи логи. Retention/delete охоплюють похідне; фактичне видалення має перевірку, а нездійснене зовнішнє очищення лишається blocked. Не відновлювати відкликаний доступ або дані зі старого backup.
