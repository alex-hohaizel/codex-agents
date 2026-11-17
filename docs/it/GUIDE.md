# Guida a Codex Agent System

Svolgete un compito mirato con Codex, sviluppate un prodotto con specialisti o progettate un agente riutilizzabile. Il sistema collega il lavoro alla fonte effettiva, a un responsabile e a un risultato verificabile.

[English](../en/GUIDE.md) · [Українська](../uk/GUIDE.md) · [Deutsch](../de/GUIDE.md) · [Italiano](../it/GUIDE.md) · [Español](../es/GUIDE.md) · [Français](../fr/GUIDE.md) · [简体中文](../zh-CN/GUIDE.md)

Per la prima sessione, apri la [guida di avvio](../../START_HERE.md#install-and-verify). Poi [segui una richiesta in un progetto completo](../technical/END_TO_END.md), dalla scelta del team alla verifica della pubblicazione. [Apri la mappa del flusso](../../assets/marketing/release-1.7/workflow-en.svg) · [Indice della documentazione](../INDEX.md)

Il candidato commerciale riunisce configurazione e diritti della versione acquistata. Leggi [la guida](../commercial/BUYER_GUIDE.md), [la licenza](../commercial/LICENSING.md) e [i limiti runtime](../commercial/WORKBENCH_RUNTIME.md).

## Da dove iniziare

- **Provate Codex.** [Installazione e verifica](#install) · [Primo compito](#first-task) · [Flussi illustrati](../../marketing/it/README.md)
- **Sviluppate o gestite un progetto.** [Scegliete un flusso di lavoro](#workflow) · [Trovate una skill o un ruolo](#catalog) · [Pannello per Mac](#workbench) · [Operazioni e ripristino](#operations)
- **Capite come funziona il sistema.** [Harness](#harness) · [Subagenti](#subagents) · [Capsule di contesto](#context) · [Modelli e costi](#models)
- **Trovate e verificate le evidenze.** [Ricerca documentale (RAG)](#retrieval) · [Valutazioni (evals)](#evals) · [Strumenti e autorizzazioni](#permissions)

[Argomenti tecnici (in inglese)](../OPERATING_MODEL.md#engineering-topics) · [Esempio pratico di RAG (in inglese)](../technical/RETRIEVAL.md) · [Requisiti del prodotto](../../governance/requirements.csv)

<a name="install"></a>
## Installare e verificare il rilevamento

1. Aprite la versione stabile di `alex-hohaizel/codex-agents`. La procedura da terminale su macOS o Linux usa Bash, Python 3.9+, Git, GitHub CLI (`gh`) con accesso autenticato e Codex. Per un’installazione guidata, chiedete a Codex di spiegare ogni passo in italiano e conservare opzioni e percorsi esatti.
2. Seguite l’installazione con attestazione. Lo strumento confronta l’impronta dell’archivio e l’attestazione GitHub con commit, workflow e manifesto delle fonti. Selezionate la prima installazione in assenza della suite gestita oppure fornite la versione installata che avete verificato. [Versione stabile](https://github.com/alex-hohaizel/codex-agents/releases/latest) · [Comandi esatti](../INSTALL.md#steps)
3. Controllate nell’audit le 33 skill, la destinazione, la conservazione delle icone e dei relativi riferimenti e gli eventuali conflitti. Applicate il piano verificato e controllate i file con il journal restituito. Il profilo gestito e i dodici ruoli hanno un audit e un journal dedicati. [Profilo e ruoli](../INSTALL.md#profile-and-roles)
4. Installate Orchestrator e Maintenance separatamente se vi servono. In Agent Atelier esaminate l’anteprima della fonte precisa, la destinazione e le differenze, poi applicate e verificate. In Codex il gestore delle skill personali può usare la cartella opzionale completa. [Componenti opzionali](../INSTALL.md#optional-components)
5. Aprite una nuova chat Codex nella cartella del prodotto. Richiamate `$agent-foundry` o la skill scelta. Se l’ambiente mostra il percorso risolto, confrontatelo con la fonte installata. Verificate l’uso con un compito il cui risultato è visibile. [Rilevamento in Codex](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)

ChatGPT Work ha un’interfaccia separata per le skill personali. Usate il relativo pacchetto e verificate le voci salvate e caricate in quell’ambiente. L’installazione locale in Codex è un’operazione distinta. [Pacchetti](../../governance/PACKAGES.md)

<a name="first-task"></a>
## Fare la prima modifica

Create una cartella di prova e apritevi una nuova chat Codex. Inserite `# Cheklist` in `README.md` e una riga da preservare in `notes.txt`. Chiedete in italiano:

```text
Correggi l’ortografia del titolo in README.md. Mantieni notes.txt intatto.
Mostra il titolo corretto e come hai verificato entrambi i file.
```

Accettate il risultato dopo aver visto `# Checklist` e il contenuto originale di `notes.txt`. Per questo lavoro basta un intervento diretto. Per un progetto più ampio date a Orchestrator il risultato, la cartella, le modifiche consentite e un criterio di accettazione osservabile. Per esempio, chiedete di verificare il flusso di acquisto preservando il contratto di pagamento e segnalando problemi riproducibili. [Primo compito riproducibile](../../START_HERE.md#install-and-verify)

<a name="workflow"></a>
## Scegliere il percorso e conservare il contesto

Svolgete il compito direttamente, invocate una skill o affidate la scelta a `$atelier-orchestrator`. Selezionate un direttore per il ciclo di vita di un’app, chatbot o gioco. `$agent-foundry` serve per un agente o una squadra che svolge un lavoro ricorrente. Verificate il passaporto prima della costruzione e provate il pacchetto preparato su un compito originale. `$design-specialist-skills` definisce un flusso riutilizzabile con attivazione e criteri di accettazione.

<a name="harness"></a>
### Harness e autorizzazioni

Codex fornisce runtime, strumenti e autorizzazioni. Il repository contiene `AGENTS.md`, descrizioni e risorse delle skill, contratti di dominio, ruoli e verifiche. Confermate quali istruzioni sono state caricate e applicate l’autorizzazione al confine dello strumento effettivo. [Harness e autorizzazioni](../OPERATING_MODEL.md#harness-and-authority)

<a name="subagents"></a>
### Ruoli e subagenti

Delegate un risultato autonomo o una revisione indipendente. Indicate soggetto, revisione delle fonti, percorsi in ingresso, permessi di scrittura, risultato, limiti, condizioni di arresto e dove restituirlo. Assegnate un solo scrittore allo stato condiviso. Raccogliete il risultato effettivo prima di integrarlo. [Percorsi e subagenti](../OPERATING_MODEL.md#routes-and-subagents)

Se il progetto gestisce il backlog con una proiezione locale dei ticket, prepara, esamina e applica il nuovo piano dopo l’approvazione. Rileggi la ricevuta registrata prima di affidare un ticket pronto a chi lo eseguirà. Verifica di nuovo il passaggio nella sessione Codex che riceve il ticket e conserva il risultato per una revisione indipendente. [Piano approvato e passaggio del lavoro](../technical/TICKET_REPLAN.md)

Per il lavoro in parallelo, assegna worktree Git separati sullo stesso commit. Salva un punto di ripresa quando si interrompe il lavoro, verificalo nella nuova sessione e integra i commit revisionati in un worktree dedicato. [Coordinare i worktree e riprendere](../technical/TICKET_WORKTREES.md)

Confronta le GitHub Issues collegate esplicitamente con la proiezione del progetto. Chiedi a un revisore indipendente di collegare i criteri di accettazione e le verifiche dei rischi alle evidenze del candidato esatto. Se l’esito di un’operazione esterna è incerto, controlla il sistema di destinazione prima di prendere una decisione. [Riconciliare le GitHub Issues](../technical/TICKET_GITHUB.md) · [Verificare le evidenze del candidato](../technical/TICKET_QUALITY_GATE.md)

Per una decisione importante, raccogli posizioni di specialisti diversi sulle stesse evidenze. Chiedi loro di rispondere all’obiezione più rilevante. Il responsabile della decisione sceglie il prossimo passo. [Deliberare in gruppo](../../optional-skills/atelier-orchestrator/references/team-deliberation.md)

Conserva il piano originale dello sprint mentre cambia il backlog. Esamina aggiunte e dipendenze prima di modificare il perimetro. Verifica i requisiti applicabili nel PRD e nell’architettura e fai revisionare la nuova versione. [Pianificare lo sprint](../technical/TICKET_TREE.md#keep-a-sprint-plan-while-the-backlog-changes) · [Revisionare la specifica](../technical/TICKET_PRODUCT_SPEC.md)

Riprendi il brainstorming o la verifica di un’idea in una nuova sessione partendo dal registro salvato. Prepara un brief, un PRFAQ o documenti distinti per design ed esperienza, con fonti e decisioni aperte. Verifica skill e ruoli Codex importati prima di prepararli in un nuovo progetto. Per un issue GitHub associato, esamina una modifica proposta e rileggi l’esito prima di ripeterla. [Workshop](../technical/WORKSHOP.md) · [Facilitazione di prodotto](../technical/PRODUCT_FACILITATION.md) · [Importazione con Foundry](../technical/CONSTRUCTOR_IMPORT.md) · [Modifiche GitHub](../technical/TICKET_GITHUB.md#apply-a-reviewed-change-to-a-mapped-issue)

Crea un prototipo interattivo nel browser da DESIGN ed EXPERIENCE revisionati o collega bozze, revisioni e verifiche alle fonti esatte nel registro dei modelli. Verifica un modulo esistente e prepara una migrazione revisionata in una nuova cartella. Per l’albero delle attività, riconcilia un effetto dopo aver esaminato gli stati locale, precedente e remoto. [Prototipo UX](../technical/UX_PROTOTYPE.md) · [Modelli](../technical/DOCUMENT_TEMPLATES.md) · [Migrazione di moduli](../technical/MODULE_MIGRATION.md) · [Albero del tracker](../technical/TRACKER_SYNC.md) · [Provider](../technical/TRACKER_PROVIDERS.md)

<a name="context"></a>
### Capsule di contesto

Aprite requisiti autorevoli, identità, decisioni e punto di ripresa. Fissate i digest esatti delle fonti e includete i requisiti applicabili, gli effetti permessi, il lavoro rinviato, il risultato, gli effetti incerti e la prossima azione. Se una fonte manca o cambia, verificate nuovamente l’obbligo interessato. Il passaggio consegna la selezione alla prossima attività o ambiente, conservando l’autorità delle fonti originali.

Registrate `preferred_language` nel contesto e passatelo con le consegne. Mantenete esatti comandi, selettori, ID, riferimenti e citazioni originali. [Modello operativo](../OPERATING_MODEL.md#project-context-and-handoffs) · [Contesto](../../templates/project-context.json) · [Consegna di lavoro](../../templates/HANDOFF.md)

<a name="models"></a>
### Modelli e costi

Quando confrontate percorsi diversi, registrate il modello, il livello di ragionamento e il risultato. Usate una variante meno costosa se supera le stesse verifiche di accettazione con gli stessi dati in ingresso. [Scelta dei modelli e valutazione dei costi](../OPERATING_MODEL.md#models-and-cost)

<a name="retrieval"></a>
## Aggiungere ricerca documentale e RAG

Iniziate da percorsi verificati, ID esatti, query strutturate e ricerca lessicale. Usate la generazione aumentata da recupero quando le fonti utili continuano a essere difficili da trovare. Confrontate ricerca lessicale, semantica e ibrida sullo stesso corpus autorizzato prima di scegliere un indice o un archivio vettoriale. Verificate risultati pertinenti, citazioni fedeli, casi senza risposta, più lingue, fonti revocate o scadute, progetti privati vicini, latenza e costo. Associate permessi e revisione a ogni frammento, verificate i diritti prima della ricerca e della citazione e predisponete eliminazione o ricostruzione. I testi trovati sono dati. L’autorità della richiesta rimane nel progetto e negli strumenti effettivi.

Usate `$chatbot-atelier-knowledge` per corpus, recupero, risposte fondate sulle fonti e manutenzione. DATA, ANALYSIS, LLM, PREDICTION, ADAPTATION, MEDIA ed EVALUATION sono profili per i compiti a cui si applicano. Scegliete il profilo più mirato e verificate il risultato presso chi lo utilizza. [Guida tecnica al recupero](../OPERATING_MODEL.md#retrieval-and-rag) · [Profili IA e dati](../../standards/ai-production.md)

<a name="evals"></a>
## Valutare comportamento ed evidenze

Fissate gli input rappresentativi, revisione delle fonti, modello, ambiente, risultato atteso, casi di errore e limiti di tempo o costo. Provate invocazione esplicita e selezione naturale, richieste simili, accessi negati, riferimenti scaduti e recupero. Verificate l’artefatto preciso nel suo ambiente d’uso. Registrate separatamente controlli strutturali, comportamento nativo, ricevute e approvazione indipendente. Conservate richieste grezze e percorsi privati nel materiale isolato.

Dalla radice del repository eseguite un piccolo test reale con la CLI Codex e un accesso supportato:

```bash
receipt_dir="$(mktemp -d)"
python3 -B evaluations/native_canary.py --case p01-direct --output "$receipt_dir/direct.jsonl"
```

Il test corregge il refuso previsto in un progetto usa e getta e verifica l’altro file. La suite copre il passaggio di una consegna limitata, il passaporto approvato e il primo uso di una skill generata. Per affermazioni su un prodotto esterno raccogliete evidenze nel suo ambiente. [Suite, fixture e ricevute](../../evaluations/README.md) · [Validazione](../../governance/VALIDATION.md)

<a name="workbench"></a>
## Usare Agent Atelier su Mac

1. Aprite le fonti correnti e compilate con il lockfile Node.js. Da `apps/agent-atelier/` eseguite:

```bash
npm ci --ignore-scripts
npm run build
node launcher/atelier.mjs start
node launcher/atelier.mjs status
node launcher/atelier.mjs doctor
```

2. Nel pannello locale trovate il progetto e controllate la copertura dichiarata. I progetti registrati in Codex possono comparire senza chat. Cronologia e artefatti si caricano all’apertura. Esaminate la cartella esatta e collegatela esplicitamente. La modalità demo mostra dati fittizi.
3. Aprite l’elemento e la prossima azione fondata sulle fonti. Trasferitela nel modulo e verificate obiettivo, accettazione, input, permessi, skill e percorso di Orchestrator. Preparate la richiesta. Avviate il lavoro autorizzato e controllate risultato e ricevuta. Riprendete una chat esistente se contesto e identità sono supportati e il soggetto con diritto di scrittura è libero. Per un contesto non recuperabile preparate un nuovo compito circoscritto.
4. In Connessioni controllate app, plugin e connettori disponibili. Se supportato, il pannello trova la documentazione ufficiale OpenAI, mostra e scarica un PNG prodotto da Codex, cerca immagini e audio Openverse con origine e licenza e legge metadati dei repository tramite un login GitHub CLI esistente. Usate le operazioni consentite dall’ambiente e dall’account effettivi. [Guida del pannello](../../apps/agent-atelier/README.md) · [API e connessioni](../../apps/agent-atelier/shared/API.md)

<a name="operations"></a>
## Gestire, ripristinare e aggiornare

<a name="permissions"></a>
### Strumenti e autorizzazioni

Prima di un’azione di scrittura verificate operazione, destinazione, autorizzazione, costo, limiti e ricevuta attesa. Dopo un timeout o senza ricevuta consultate lo stato autorevole della richiesta esatta. Ripetete l’azione con l’autorizzazione corrente e una protezione verificata contro i duplicati. Conservate gli effetti irrisolti e le evidenze. Valutate il risultato nel prodotto effettivo e registrate preparazione, esecuzione del comando e creazione dei file separatamente. [Effetti degli strumenti ed evidenze](../OPERATING_MODEL.md#tools-evidence-and-recovery)

### Ripristino e aggiornamenti

Per gli aggiornamenti usate il pacchetto stabile e il suo piano. Conservate i journal e lo stato. Dopo un’interruzione esaminate la destinazione effettiva prima di riprendere. Ripristinate nucleo, profilo e skill opzionale dal rispettivo journal. Salvate il database e i file del pannello con la procedura documentata, riavviate con la directory dati appropriata e controllate i progetti e un compito limitato. Dati di prodotto, chat native e account hanno responsabili e procedure di ripristino propri. [Installazione e ripristino](../INSTALL.md#rollback) · [Riprendere il lavoro](../../governance/RESUMABLE_WORK.md)

<a name="catalog"></a>
## Scegliere una skill o una famiglia

| Selettore | Punto di partenza per |
| --- | --- |
| `$atelier-orchestrator` | Scegliere un percorso, continuare e coordinare il lavoro |
| `$agent-foundry` | Progettare un agente o un team per un lavoro ricorrente reale |
| `$design-specialist-skills` | Definire una skill mirata o una famiglia riutilizzabile |
| `$app-atelier-director` | Ricerca, concetti, specifica, UX, sviluppo, supporto, crescita, QA, rilascio e gestione di un’app |
| `$chatbot-atelier-director` | Pubblico e canali, prodotto, conversazioni, conoscenza, integrazioni, media, sviluppo, QA, rilascio e gestione |
| `$gamedev-director` | Studio, concetti, preproduzione, asset, sviluppo, QA, rilascio e gestione di un gioco |
| `$codex-agents-maintenance` | Modifiche autorizzate a skill e documentazione, verifiche e pacchetti di rilascio |

### Inventario completo di specialità e ruoli

**Squadra applicazioni**

- [`$app-atelier-director`](../../kit/skills/app-atelier-director/SKILL.md) · Guida del ciclo di vita
- [`$app-atelier-research`](../../kit/skills/app-atelier-research/SKILL.md) · Ricerca su utenti e mercato
- [`$app-atelier-concepts`](../../kit/skills/app-atelier-concepts/SKILL.md) · Concetti di prodotto
- [`$app-atelier-specification`](../../kit/skills/app-atelier-specification/SKILL.md) · Requisiti e contratti
- [`$app-atelier-experience`](../../kit/skills/app-atelier-experience/SKILL.md) · Esperienza e accessibilità
- [`$app-atelier-build`](../../kit/skills/app-atelier-build/SKILL.md) · Implementazione
- [`$app-atelier-growth`](../../kit/skills/app-atelier-growth/SKILL.md) · Acquisizione
- [`$app-atelier-support`](../../kit/skills/app-atelier-support/SKILL.md) · Flusso di assistenza
- [`$app-atelier-qa`](../../kit/skills/app-atelier-qa/SKILL.md) · Revisione indipendente della qualità
- [`$app-atelier-release`](../../kit/skills/app-atelier-release/SKILL.md) · Pubblicazione
- [`$app-atelier-operations`](../../kit/skills/app-atelier-operations/SKILL.md) · Gestione

**Squadra chatbot**

- [`$chatbot-atelier-director`](../../kit/skills/chatbot-atelier-director/SKILL.md) · Guida del ciclo di vita
- [`$chatbot-atelier-research`](../../kit/skills/chatbot-atelier-research/SKILL.md) · Ricerca su pubblico e canali
- [`$chatbot-atelier-specification`](../../kit/skills/chatbot-atelier-specification/SKILL.md) · Contratti di comportamento e stato
- [`$chatbot-atelier-conversation`](../../kit/skills/chatbot-atelier-conversation/SKILL.md) · Progettazione dei dialoghi
- [`$chatbot-atelier-knowledge`](../../kit/skills/chatbot-atelier-knowledge/SKILL.md) · Conoscenza e recupero
- [`$chatbot-atelier-integrations`](../../kit/skills/chatbot-atelier-integrations/SKILL.md) · Integrazioni e ricevute
- [`$chatbot-atelier-media`](../../kit/skills/chatbot-atelier-media/SKILL.md) · Media
- [`$chatbot-atelier-build`](../../kit/skills/chatbot-atelier-build/SKILL.md) · Implementazione
- [`$chatbot-atelier-qa`](../../kit/skills/chatbot-atelier-qa/SKILL.md) · Revisione della qualità
- [`$chatbot-atelier-release`](../../kit/skills/chatbot-atelier-release/SKILL.md) · Pubblicazione
- [`$chatbot-atelier-operations`](../../kit/skills/chatbot-atelier-operations/SKILL.md) · Gestione e recupero

**Squadra giochi**

- [`$gamedev-director`](../../kit/skills/gamedev-director/SKILL.md) · Guida del ciclo di vita
- [`$gamedev-studio`](../../kit/skills/gamedev-studio/SKILL.md) · Pratiche dello studio
- [`$gamedev-concepts`](../../kit/skills/gamedev-concepts/SKILL.md) · Concetti giocabili
- [`$gamedev-preproduction`](../../kit/skills/gamedev-preproduction/SKILL.md) · Sistemi e pianificazione produttiva
- [`$gamedev-assets`](../../kit/skills/gamedev-assets/SKILL.md) · Produzione di asset
- [`$gamedev-build`](../../kit/skills/gamedev-build/SKILL.md) · Implementazione del gioco
- [`$gamedev-qa`](../../kit/skills/gamedev-qa/SKILL.md) · Revisione della qualità
- [`$gamedev-release`](../../kit/skills/gamedev-release/SKILL.md) · Pubblicazione
- [`$gamedev-liveops`](../../kit/skills/gamedev-liveops/SKILL.md) · Gestione in produzione

**Ruoli specialistici Codex**

- [`foundry-architecture`](../../agent-profiles/foundry-architecture.toml) · Architettura
- [`foundry-backend`](../../agent-profiles/foundry-backend.toml) · Backend
- [`foundry-conversation`](../../agent-profiles/foundry-conversation.toml) · Dialoghi
- [`foundry-cost`](../../agent-profiles/foundry-cost.toml) · Costi
- [`foundry-integrations`](../../agent-profiles/foundry-integrations.toml) · Integrazioni
- [`foundry-judge`](../../agent-profiles/foundry-judge.toml) · Giudizio indipendente
- [`foundry-platform`](../../agent-profiles/foundry-platform.toml) · Piattaforme target
- [`foundry-privacy`](../../agent-profiles/foundry-privacy.toml) · Privacy
- [`foundry-product`](../../agent-profiles/foundry-product.toml) · Prodotto
- [`foundry-qa`](../../agent-profiles/foundry-qa.toml) · Qualità
- [`foundry-reliability`](../../agent-profiles/foundry-reliability.toml) · Affidabilità
- [`foundry-skeptic`](../../agent-profiles/foundry-skeptic.toml) · Revisione critica

Il catalogo elenca le skill con i rispettivi nomi stabili e tutti i dodici ruoli. [Catalogo completo](../CAPABILITIES.md#all-skills-and-roles) · [Esempi visivi](../../marketing/it/README.md) · [Altre lingue](../../START_HERE.md#use-another-language)
