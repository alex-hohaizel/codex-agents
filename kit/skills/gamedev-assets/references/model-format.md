# Game model4.0: current format and executable checks

Зміст: commands → envelope → production → evidence → handoff → limits.

## Commands

Визнач фактичний `<SKILL_DIR>` активної навички; не підставляй шлях чужого Mac. Python3.10+ достатній для bundledtools.

```bash
python3 <SKILL_DIR>/scripts/game_model.py --help
python3 <SKILL_DIR>/scripts/game_model.py validate /absolute/model.json --design-only --json
python3 <SKILL_DIR>/scripts/game_model.py plan /absolute/model.json --stage concept --maturity C1 --json
python3 <SKILL_DIR>/scripts/game_model.py validate /absolute/model.json --stage preproduction --maturity T --json
python3 <SKILL_DIR>/scripts/game_model.py impact /absolute/model.json --changed RULE-ID --json
python3 <SKILL_DIR>/scripts/game_model.py portfolio /absolute/portfolio.json --json
python3 <SKILL_DIR>/scripts/production_contract.py /absolute/operations.json --root /absolute/project
python3 <SKILL_DIR>/scripts/reference_math.py <SKILL_DIR>/assets/v4/golden-arithmetic.json
python3 <SKILL_DIR>/scripts/check_suite.py --skill <SKILL_DIR>
```

У `plan/validate` stage: concept/preproduction/slice/beta/release. C0/C1/T — зрілість дизайну, не заміна цих gates. Preproduction і пізніше вимагають T; нижчий override не знижує gate. C0 не буває ready. `--design-only` завжди `stage_ready:false`; exit0 означає тільки pass запитаного структурного authoring scope. Для stage gate missing due evidence дає nonzero. `quality_certified:false` зберігається.

## Чинний envelope

Єдина чинна схема `assets/game-model.schema.json` має `schema_version:"4.0.0"` і обов’язкові `id,title,author_ids,source_requirement_ids,constraints,features,domains,dependencies,scenarios,evidence,production`. [Точний довідник](model-contract.md) описує домени, сценарії та докази. `game_model.schema()` повертає тільки цю схему; інші версії відхиляються.

Одне канонічне `design/game-model.json`; проектні requirements/decisions — чинна authority. Typed refs не створюють нової мови або іншої registry. Власні source/code/data/specs лежать у pinned linkedfiles. Модель не копіює кожний mesh і sample уJSON.

## Productionextension

`production`:

- `maturity:C0|C1|T`;
- `tracks`: рівно TR01…TR20 за `v4_contract.TRACKS` і [systems](v4/systems.md): stable name, enabled/rationale, owner/receiver, requirement_ids, summary, reads/writes, contract_ids, invariants, scenario_ids, progression/content/feedback/persistence/budget, pinnedconcept_refs/spec_refs;
- `applicability`: damage/physics/ai/cloud/procedural/purchases з enabled/rationale. AI узгоджується з autonomousactors; не домислюй combat чиcloud із самого жанру;
- `contracts`: typed behavior/state_machine/numeric/rng/family/generator/ai/persistence/damage/physics/input/presentation/economy/commerce/journey/asset/release/measurement, fields з `assets/v4-model/contract.template.json`;
- `state_fields`: typed Catalogue із classification/owner/scope/authority/storage/encoding/consistency_group/commit/restore/merge/migration/retention/initial;
- `dependencies:[{from,to,reason}]`: upstream→dependent між існуючими IDs;
- `operations`: capabilities/recipes/transformations/attempts/assemblies/obligations за [production](v4/production.md);
- `unresolved:[{id,description,owner,due:C0|C1|T,blocks:[ID]}]`; due unresolved блокує відповідну зрілість.

Шаблони `assets/v4-model/` і деталізовані `assets/v4-domain-templates/` — матеріали authoring, не evidence. Приклади моделей і `production.template.json` починаються з C0/unresolved. Не змінюй placeholders на invented receipts. Machinecontract — мінімум форми; semantic completeness перевіряє предметний owner/receiver/QA.

C1 active tracks мають linkedconcept documents, concrete rule status/invariants/positive і negativecases. T додає pinned specs, all state classifications, detailedbody за kind (mathdomain/round/clamp/overflow; RNGstreams/version/resume; FSMguards/tie; AIknowledge/actiontiming; damagechannels/capture/dedup/commit; solverprofile; purchase/save lifecycle), operationobligations. Numeric tuning має exact initial/min/max/goal/method; немає поведінкового TBD. Readonlychecker не виконує формули/callbacks/engine: validation потребує ordinary code/fixtures/oracle.

## Evidence, assembly та impact

Належні domain checks та незалежні track reviews `v4.TRxx.concept|contract`. `plan` дає actualcheck IDs і scope_sha256. Proofbinds currentbytes/inputs, declareddependencyclosure, сценарій і actualobserver. Зміна authors/toolchain/recipe/input/потрібнихданих інвалідує dependentproof; missinggraph edge вимагає integratortriage. Не оновлюй digest замість повторної перевірки.

T/A/B/R productiongates: Tcontract → actualassembly/slice A → beta B → release R. Slice+ вимагає assembly; native_verified assembly builddigest має збігатися з перевіреним nativeartifactreceipt. Документ і samplevalidity не доводять device/humanfact. `scope_is_product_release` не встановлюй для boundedreview.

`reference_math.py` відтворює чотири погоджені D2arithmeticalillustrations: channelorder/round/barrier/overkill, DoT/capture/resume, TTKdistribution, idealcontactimpulse. Це chosenexamplepolicies; не переносити їх у кожну гру як default. Під actualruntime створюй спільні goldenfixtures і differentialcheck.

## Handoff і продовження

Toolkit **4.3.0**, game-model **4.0.0**, handoff protocol **1.0.0** і runtime state **2.0.0** — окремі чинні версійні області. Handoff і runtime вимагають точний поточний toolkit marker. Попередні формати результатів не читаються й не конвертуються. Для продовження віднови фактичні вимоги, рішення, код, дані, media й стан продукту, потім створи поточні contracts та отримай належні докази. Установлення навички не змінює ці файли або game saves. Scoped QA/liveops/production decision rules — [handoff](handoff-contract.md), [workflow](game-model-workflow.md).

## Limits

Структура/links/bytes/freshness не доводять 100%повноти людського задуму, mathematicalcorrectness усіх algorithmrefs, diversity/fun/comfort/rights/truthofreceipt. Actualgeneration/import/runtime/device/playtest/revenue — окремі операції та модальності. Не роби accepted із countполів або rolelabels.
