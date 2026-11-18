# Agent Atelier для Mac — готовий runtime-кандидат

Розпакуйте архів у постійну папку та відкрийте **Launch.command**. Node.js і
зібраний інтерфейс уже включені; npm, TypeScript і локальна dev-збірка покупцю
не потрібні. Вхід у Codex, моделі й сторонні інтеграції належать вашому
акаунту. Перш ніж обходити попередження системи, перевірте походження пакета.
Кандидат ще не проходив notarization для публічного розповсюдження.

Прочитайте включені [ліцензію кандидата](../legal/LICENSE.txt),
[нотатки про сторонні компоненти](../legal/THIRD_PARTY_NOTICES.txt),
[права та правила ліцензування](../../RIGHTS.md) і [версійовану пропозицію](../offer.json).
Повні початкові умови, проєкти підтримки й приватності та український виклад
ліцензії збережені в `commercial/legal/`. Повні ліцензійні тексти Node і
зібраних залежностей клієнта містяться в `notices/` та перелічені в `runtime-manifest.json`.

Виберіть правильний архів: `arm64` для Apple Silicon, `x64` для Intel.
Мінімум macOS 13.5 визначений включеним Node.js v24. Виконання на одному
Apple Silicon Mac не доводить роботу на M1 та Intel. Дивіться фактичний звіт
цільового середовища для цієї версії.

Стан за замовчуванням зберігається окремо:
`~/Library/Application Support/Codex Agent System/Agent Atelier`. Попередній
стан Agent Atelier та проєкти автоматично не мігруються.

Розширені команди з розпакованої папки:

```sh
./Runtime.command verify
./Runtime.command start --no-open
./Runtime.command status
./Runtime.command doctor
./Runtime.command stop
```

Для ізольованої перевірки задайте `--data-dir /absolute/private/test-folder`
і вільний `--port`. Панель працює лише на loopback. Не передавайте токени
з URL запуску та приватні файли доступу у screenshots чи підтримку.

Перед оновленням runtime зупиніть панель. Знімок стану створюється лише під
виключним блокуванням, а відновлення — лише в **новій** папці. Оригінал і
знімок зберігаються.

```sh
./Runtime.command snapshot --data-dir /absolute/current-data --output /absolute/new-snapshot
./Runtime.command restore --snapshot /absolute/new-snapshot --sha256 RECEIPT_SHA --output /absolute/new-restored-data
./Runtime.command start --data-dir /absolute/new-restored-data
```

Не видаляйте попередній runtime до перевірки нової версії та стану.
Новішу SQLite schema відновлювати старим runtime заборонено. Звичайні
live-резервні копії використовуйте через підтверджений механізм самої панелі.
Знімки можуть містити приватний стан і залишаються на комп’ютері власника.
