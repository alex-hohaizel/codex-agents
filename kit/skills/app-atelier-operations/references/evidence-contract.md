# Перевірки й докази

До початку визначити capability/requirement -> artifact -> test -> потрібний proof -> observer -> due gate. Evidence pin-ить точні artifact/proof/source bytes, метод, середовище, час, фактичного observer і limitations. Artifact має реальний відносний path та hash. Claims окремі від evidence.

Структурна перевірка доводить структуру. Unit fixture доводить свою гілку коду. Синтетичний сценарій не доводить, що людина зрозуміла продукт або заплатить. Твердження постачальника, desk research, розрахунок і власне вимірювання мають різні статуси. Ринкову ціль і власний прибуток не вважати підтвердженими до фактичних відповідних спостережень.

Незалежний reviewer не є автором артефакту. Передати raw request, потрібні джерела й артефакти без gold answer/підказаного діагнозу для первинного forward case. Diagnostic retest після finding може мати repro і є іншим видом перевірки. Зберігати actual actor IDs; назви уявних ролей не є незалежними акторами.

Для продукту прийняти окремо функціональні сценарії, errors/recovery, дані/auth, conditional payments/entitlements, design fidelity, доступність, цільові пристрої, latency/resource/cost, backup/restore і release state. Недоступний фізичний пристрій не замінювати текстовою обіцянкою; показати точний blocked proof і bridge. Синтетичні store-тестувальники не є виконанням вимоги магазину.

Для оплат за застосовності: авторитет провайдера, restore, duplicate/delayed/reordered events, unknown receipt, expiry/cancel/refund, заявлена міжклієнтська політика прав та offline відновлення. Не виконувати live платежі лише заради тесту; використовувати sandbox/fixtures, де вони достатні.

Фіксувати finding/severity/repro/input/output hashes і вплив. Автор усуває причину; незалежний reviewer повторює зачеплені checks. Старий fail не переписувати pass. Зміна source/artifact/proof відкриває відповідний verdict. Не повторювати весь набір після локальної зміни без відповідного impact.

Completion вимагає всіх due must і конкретних outputs; file count, красивий звіт і середній score не закривають незадоволений критерій. Future proof залишається pending із owner/due gate. Чесно розділяти self-check, structural pass, independent review, owner acceptance, device proof і live observation.
