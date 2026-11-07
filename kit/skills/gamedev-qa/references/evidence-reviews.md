# Докази, defects та regression

## Case result

`case_id`, requirement IDs, scope, baseline/source/build hashes, platform/device/OS, preconditions, scenario/seed/input, expected outcome + design ref, procedure/fault, observed outcome, raw artifact refs/hashes, execution actor/time, independent reviewer, verdict, limitations. Зберігати actual result лише після виконання. Templates лишаються clearly examples.

## Defect record

ID; severity/player impact; requirement IDs; exact failing revision/build; reproducible steps/state/seed; expected design/official rule; actual result; raw screenshot/video/audio/log/profile; owner; affected dependency closure; repair revision; retest evidence; closure. «Поганий звук» без cue/timecode/condition — недостатньо; «cue ui.confirm clips на X при duplicate event» — адресна перевірка.

## Інваріанти evidence

- Hashes актуальні для exact bytes; нова revision не успадковує pass автоматично.
- Review actor відрізняється від автора артефакту; actor name сам по собі не доводить actual review.
- Evidence зі старого source/build має carry-forward decision й dependency impact.
- Build receipt, test result, listening acceptance, human observation та market metric — різні types.
- Відсутність evidence відображається `not_tested`/`blocked`, а не порожнім pass.
- Credentials, private keys, raw payment tokens/PII не входять у portable evidence.

## Regression selection

Change → direct dependencies → transitive product effects → required checks. Приклад font change зачіпає all font consumers/layout/localization/screenshots; economy table change — acquisition/save/offer/analytics/migration tests; collision layer change — усі actor/arena contacts; audio bus change — every cue family/interruption/mute/device mix.

Unchanged content з exact hashes і незачепленими dependencies зберігає acceptance. Unknown impact потребує розширення checks, а не повного re-review за звичкою. Локальний defect repair повторно приймає той самий незалежний QA; material redesign вимагає нового target/choice і відповідного review.

## Archive та final report

Використати common handoff schema/validator; включити machine matrix + короткий людський звіт. У звіті: outcome early; tested scope/platform/build; strongest evidence; blocking failures; not-tested/hypotheses; exact repair owner/next action. Не перераховувати сотні успішних tests, якщо вони не пояснюють ризик.

Зберегти immutable accepted packet, відокремивши working repair branch. Release отримує exact accepted revision; після нової зміни release candidate має impact/retest, не тиху підміну bytes під старим pass.

## Binding предметних доказів 4.0

QA plan/case pattern не є execution evidence. Для canonical game-model evidence зберегти точні `domain,stage,modality,proof_path,sha256,observer_id,author_ids,method,observed_at,environment,origin` за `model-format.md`; кейс зв’язати з current requirement/rule/scenario й build/state/seed. Структурний валідатор перевіряє records/bytes, reviewer оцінює достатність actual proof та expected outcome. Приклад-файл не закриває gate; document review не стає device/human/live доказом через назву modality. Не змішувати author і reviewer або model simulation та real players.

## Freshness та незалежність execution evidence

Evidence scope pin semantic inputs, rule/data/recipe/importer/toolchain/build/configversions і actual modality. Зміна input/edge означає selectiveinvalidation за impactclosure; acceptedoriginal не переписується. Зберегти authors/observer/revieweractualIDs та rawoutputs; hash/status самсобою не доводять незалежної роботи.

Operationwitness, production attempt, assembly test, native run, physical observation, human playtest й live query різні outputs. Unknownexternaloutcome передавати з job/requestID/reconciliation, не як failedretriablebydefault.
