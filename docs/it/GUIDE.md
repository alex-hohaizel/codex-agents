# Agent System — la guida completa a Work + Codex

[English](../en/GUIDE.md) · [Українська](../uk/GUIDE.md) · [Deutsch](../de/GUIDE.md) · [Italiano](../it/GUIDE.md) · [Español](../es/GUIDE.md) · [Français](../fr/GUIDE.md) · [中文](../zh-CN/GUIDE.md)

**Suite riutilizzabile** — 33 competenze. Questa guida spiega la prima installazione, il lavoro quotidiano, la collaborazione tra Work e Codex e l’aggiornamento dei progetti esistenti. Documentazione, edizioni del repository e versioni dei componenti possono cambiare in modo indipendente.


Il registro riporta l’edizione del repository, la suite principale, le competenze facoltative, i profili dei ruoli e dell’ambiente, l’applicazione locale, lo stato della versione e le relative migrazioni. Consultalo per scegliere la versione di destinazione. Il registro storico di rc.5 conserva le verifiche per il nucleo 6.1.0, Atelier Orchestrator 1.2.0, la competenza di manutenzione 1.1.0 e Agent Atelier 0.5.0. [Registro delle versioni attuale](../../releases/current.json) · [Verifiche storiche di rc.5](../../releases/repository-1.4.0-rc.5.md) · [Aggiornamento storico alla 6.1](../../releases/migrations/6.1.0.md)

La precedente campagna 1.1.0 resta invariata: [pubblicità inglese](../../marketing/campaign/README.md) e [pubblicità ucraina](../../marketing/campaign/README.uk.md), dieci materiali per lingua. La pubblicità è EN/UK; guide e interfaccia del servizio coprono tutte e sette le lingue dichiarate. Audit, aggiornamento, installazione e controllo reali di Work restano un’attività separata nell’ambiente pertinente; un archivio delle fonti o il collegamento al repository non è una ricevuta di installazione.

**Il passaporto 0.2 è approvato per la realizzazione.** Tutte le 17 capacità, R01–R27 e A01–A29 restano comprese con le stesse 35 fonti riutilizzabili e 12 ruoli. Priorità a contesto, design professionale e pannello operativo. Sono state eseguite verifiche reali circoscritte di contesto/UI/Codex; non completano tutti i casi integrali, non dimostrano addestramento dei modelli né accettazione del proprietario. Ogni regressione confermata impedisce l’adozione; le prove necessarie mancanti restano aperte. Leggere [lo stato della realizzazione](../evolution/2026-11-10/IMPLEMENTATION.en.md). Installazione finale, adozione operativa, pubblicazione e CI sono fatti distinti. WORK resta rinviato. La documentazione dettagliata è EN/UK.

**Candidato storico rc.3.** Agent Atelier 0.3.1 corregge il focus da tastiera e mantiene la selezione degli artefatti per progetto/percorso con metadati aggiornati; core 6.1.0, Orchestrator 1.2.0, manutenzione 1.1.0 e 35 fonti/12 ruoli restano invariati. Un aggiornamento in background non riuscito nasconde i dati del progetto non disponibili e offre il recupero invece di conservare prove obsolete. Gli artefatti Markdown si aprono come resoconti leggibili con l’hash osservato del file originale; gli hash dichiarati vengono verificati, mentre i file non collegati restano semplici osservazioni della fonte. I percorsi relativi distinguono i file omonimi. Gli esempi facoltativi comprendono acquisizione di dati con licenza, baseline/candidati realmente addestrati, inferenza HTTP protetta dalle fonti, adattamento/esportazione nativi Metal e PDF/rendering/cache della campagna bilingue esistente. I candidati recensioni/LoRA peggiorativi, la copertura insufficiente degli intervalli e l’equivalenza quantizzata sono stati rifiutati; i percorsi accettati sufficienti restano disponibili. Le fixture controllate sono dichiarate e non diventano verità umana o accuratezza commerciale. Leggere il [manuale delle attività reali](../evolution/2026-11-10/REAL-WORLD.en.md), disponibile EN/UK. Non significa 29 PASS, versione stabile finale 1.4.0 o prova della sostituzione del servizio attivo. L’accuratezza CPA resta non verificata senza dati rappresentativi; il proprietario ha approvato controlli e astensione per l’attuale caso A10. Riconciliazione completa del contesto, runtime/proprietario LIGHT BOT e approvazioni finali del proprietario/rilascio restano aperti dove mancano prove. WORK resta rinviato.

**API avanzata delle attività: memoria locale.** Il parametro facoltativo `memory_mode` usa `inherit` come valore predefinito, mantenendo attività ordinarie e preferenze globali. Una richiesta esplicita `disabled` richiede una nuova chat del servizio, impostazioni della memoria disattivate dal primo avvio, conferma nativa e divieti di lettura dei file di memoria limitati all’attività. L’adozione di una chat esistente dell’utente rifiuta `disabled` per conservarne l’impostazione. Il protocollo nativo non espone una lettura indipendente della modalità di memoria né una misura diretta del contesto inserito. Le prove iniziali, R2 e R3 conservano il verdetto NOT_ADMITTED. Tutte e tre le continuazioni R4 circoscritte hanno superato G01–G10 in Codex. Il parametro limita la memoria dell’host; le fonti dichiarate definiscono ancora le prove dell’attività. I file delle competenze selezionate usano uno spazio di esecuzione separato e immutabile; il loro archivio di controllo resta privato. Il backup JSON del servizio contiene metadati, non questi file. Vedere il [contratto EN/UK](../evolution/2026-11-10/REAL-WORLD.en.md), [Memories](https://learn.chatgpt.com/docs/customization/memories) e [permessi](https://learn.chatgpt.com/docs/permissions).

In Agent Atelier, aggiorna il portafoglio per trovare i progetti Codex locali registrati e sfogliare le pagine delle chat attive e archiviate. I progetti senza chat compaiono se l'host li restituisce. Apri un progetto per leggerne la cronologia di lavoro. Connessioni mostra lo stato dei plugin e delle app native, la ricerca di contenuti pubblici con fonte e licenza e come proseguire in Codex per le operazioni che richiedono l'host. Le fonti remote o inaccessibili sono segnalate come lacune. Con un accesso GitHub CLI già attivo puoi leggere i metadati del repository. [Modifiche al portafoglio in rc.4](../../releases/migrations/repository-1.4.0-rc.4.md).

Apri la prossima azione mostrata per riportarne il testo completo nel modulo. Modifica l’obiettivo e i criteri di accettazione, poi controlla il percorso prima di preparare l’attività. In Connessioni, OpenAI Docs MCP restituisce link alla documentazione ufficiale. Codex Image mostra l’anteprima e consente di scaricare il PNG quando l’accesso ChatGPT esistente e l’host Codex supportano l’operazione. La generazione usa i limiti inclusi di Codex. Per i plugin gestiti i cui strumenti non sono stati verificati, prosegui tramite il percorso previsto in Codex. [Aggiornamento da 0.4.0 a 0.5.0 e rollback](../../releases/migrations/repository-1.4.0-rc.5.md)

## 0. Aggiorna le competenze gestite in Codex e apri lo spazio di lavoro locale

Per un’installazione gestita, usa la versione stabile selezionata con le fonti e l’archivio esatti approvati. Puoi provare una versione candidata in un ambiente di test isolato. [Aggiornamento Codex con verifica della firma e ripristino](../../releases/migrations/6.2.0.md)

1. Scegli il commit esatto della versione e il corrispondente archivio. Conserva le fonti delle 33 competenze installate, i file e i riferimenti delle icone, i colori, le modifiche locali e i dati di proprietà. Salva requisiti del progetto, identità e personalità approvate, decisioni, autorizzazioni, attività in sospeso ed effetti esterni dall’esito incerto. L’adozione nel progetto segue una migrazione separata.
2. Segui la migrazione con verifica della firma da una copia di lavoro separata e fidata. Verifica l’attestazione di GitHub Actions e gli hash esatti dell’archivio e del manifesto. Usa il percorso indicato nella ricevuta di verifica e confronta prima di apply l’hash del manifesto nel piano con quello approvato. Controlla tutte le 33 voci, i conflitti e la conservazione dell’identità visiva. I comandi sotto provano audit, apply e verify da `kit/` con percorsi di test isolati. Conserva piani e copie di sicurezza fuori dalle directory di rilevamento delle competenze.

```bash
python3 portable/update_skill_suite.py --help
fixture_root=/absolute/path/to/isolated-test
mkdir -p "$fixture_root"
python3 portable/update_skill_suite.py audit --kit . --destination "$fixture_root/.agents/skills" --legacy-root "$fixture_root/.codex/skills" --backup-root "$fixture_root/backups" --plan "$fixture_root/core-plan.json"
python3 portable/update_skill_suite.py apply --plan "$fixture_root/core-plan.json"
python3 portable/update_skill_suite.py verify --kit . --destination "$fixture_root/.agents/skills" --legacy-root "$fixture_root/.codex/skills" --journal /actual/apply/journal.json
```

3. Sostituisci il segnaposto del registro solo con il percorso effettivamente restituito da apply. Le differenze sconosciute vanno chiarite; non forzare la sovrascrittura. Verifica separatamente il rilevamento/caricamento reale della fonte e una singola attività circoscritta. Le icone esistenti e le competenze estranee all’aggiornamento restano conservate.
4. Verifica separatamente il profilo dell’ambiente Codex dalla radice del repository: `python3 scripts/install_host_profile.py audit --plan /absolute/host-plan.json`. Applica con `apply --plan /absolute/host-plan.json --journal /absolute/host-journal.json`, poi verifica con `verify --journal /absolute/host-journal.json`. Il blocco gestito conserva le istruzioni globali esistenti; i dodici ruoli circoscritti mantengono modelli e restrizioni sugli effetti esterni. Il caricamento nell’ambiente reale richiede una verifica separata.
5. Aggiorna un `atelier-orchestrator` esistente con il gestore di competenze supportato da `optional-skills/atelier-orchestrator` nella versione scelta. Lo strumento di aggiornamento del nucleo gestisce le 33 competenze di base. Anche la manutenzione è un componente facoltativo. Installa una competenza facoltativa assente solo su richiesta. Verifica il rilevamento e l’esecuzione effettivi.

Atelier Orchestrator è il punto di accesso unico facoltativo: descrivi il risultato una volta e sceglierà l’esecuzione diretta, uno specialista esistente, un agente di progetto, un direttore, il coordinamento dei componenti o Foundry. Le richieste semplici restano semplici. Un unico brief e le autorizzazioni esistenti accompagnano il lavoro. Dopo la creazione, verifica e rilevazione di un agente di progetto da parte dell’ambiente, consiglia di proseguire tramite quell’agente e mantiene il collegamento quando torni all’orchestratore. La creazione dell’agente e l’attività di prodotto originale hanno accettazioni distinte; un pacchetto agente non completa il prodotto richiesto.

Le richieste di migliorare o riscrivere l’orchestratore stesso, una competenza, un costruttore, una famiglia o un agente esistente seguono il percorso di manutenzione: leggere fonti e impostazioni effettive, esaminare impatto e differenze, conservare identità e modifiche locali, mantenere una copia precedente e verificare il risultato salvato. Un’anteprima del percorso e il verificatore di routing facoltativo non certificano idoneità specialistica, consenso umano, esecuzione o qualità. Le invocazioni dirette delle competenze esistenti restano disponibili.

Apri Agent Atelier con il suo launcher locale. Lo spazio di lavoro e le competenze hanno versioni indipendenti. Controlla la build in esecuzione con `status` e `doctor`. In caso di aggiornamento, verifica SVG originale, riferimenti PNG e colore del marchio. Un’istanza precedente può restare attiva fino alla sostituzione verificata. Consulta la [guida di Agent Atelier](../../apps/agent-atelier/README.md) e, per quel passaggio, la [migrazione storica da 0.4.0 a 0.5.0](../../releases/migrations/repository-1.4.0-rc.5.md).

6. Per compilare il servizio locale dalle fonti, usa il lockfile fissato con Node.js 24.22.2 o una versione successiva supportata. Da `apps/agent-atelier/`, esegui i comandi seguenti. La prima installazione delle dipendenze richiede accesso di rete, senza implicare un nuovo servizio a pagamento.

```bash
npm ci --ignore-scripts
npm run build
node launcher/atelier.mjs start
node launcher/atelier.mjs status
node launcher/atelier.mjs doctor
node launcher/atelier.mjs stop
```

7. Su Mac, dopo la compilazione, `apps/agent-atelier/launcher/Agent Atelier.command` consente l’avvio con doppio clic. Il programma apre il loopback, riutilizza la propria istanza attiva e non abilita l’avvio automatico all’accesso. Seleziona una radice di progetto precisa, esaminala in anteprima e collegala. Il collegamento rileva il progetto in sola lettura: non ne adotta il nuovo metodo né autorizza tutte le attività future. La modalità dimostrativa contiene dati fittizi e non esegue comandi.

Nel pannello, trova il lavoro Codex disponibile e verifica la copertura della cronologia indicata. Progetti e attività sono raggruppati dalla cronologia nativa effettiva e dalle registrazioni nelle fonti, comprese le attività disponibili avviate direttamente in Codex; non è una scansione della cartella Home né un’autorizzazione a subentrare a un altro processo di scrittura. Collega la cartella esatta del progetto per contesto e prosecuzione. La mappa delle attività distingue risposte ricevute, risultati registrati nelle fonti e risultati accettati. Il risultato previsto e l’accettazione registrata mantengono la propria fonte; una proposta non è un’approvazione, la menzione di una competenza non è esecuzione e un agente pianificato non è installato. Descrivi il prossimo risultato tramite l’accesso unico, esamina il percorso proposto, quindi prepara e avvia l’attività delimitata. Le chat esistenti richiedono un passaggio supportato quando inattive; le modifiche protette allo stato nativo usano il controller verificato anziché scritture arbitrarie nei file.

Il portafoglio può mostrare progetti Codex locali registrati senza chat, se l’host rende disponibile il registro. Se manca un progetto, collega esplicitamente la sua cartella esatta. Per la competenza facoltativa nota di orchestrazione o manutenzione del repository, scegli **Esamina questo aggiornamento della competenza** nel catalogo, verifica le modifiche esatte della fonte, conservazione, conflitti e piano della copia precedente, quindi applica solo l’aggiornamento pronto ed esaminato. Verifica il registro effettivo e aggiorna separatamente la rilevazione dell’ambiente. Il ripristino recupera l’esatta copia precedente gestita e rifiuta modifiche successive sconosciute. Queste operazioni sulle fonti facoltative non aggiornano le 33 competenze di base né migrano prodotti.

Le chat native Codex esistenti possono essere esaminate nel portafoglio tramite un accesso dedicato alla cronologia in sola lettura. L’esecutore isolato non può riprendere una chat inattiva se non riesce a ripristinarne il contesto salvato nel proprio ambiente. In questo caso, preparate una nuova attività di progetto con limiti precisi a partire da fonti verificate, oppure proseguite la chat esistente in un ambiente nativo Codex capace di ripristinarne il contesto. L’accesso ai metadati o alla cronologia di una chat non garantisce un contesto utilizzabile per l’esecuzione. L’isolamento dell’esecuzione resta attivo; non viene effettuata alcuna migrazione dei database nativi.

8. Prepara un’attività con ambito, input, accettazione e limiti esatti, poi avviala tramite l’adattatore Codex supportato. Fonte, qualità del lavoro, integrazione, dispositivo, revisione indipendente e accettazione del proprietario sono stati distinti. L’annullamento è confermato solo dopo l’esito effettivo dell’ambiente. Le chat esistenti richiedono identità/cwd precisi e un passaggio in stato inattivo; il controllo del servizio non blocca un altro processo desktop che scrive. Riconcilia un effetto incerto prima di riprovare. Durante la preparazione dell’attività, il servizio registra le esatte fonti AGENTS che la governano, il loro ordine di priorità o la loro assenza verificata, e le impostazioni con cui Codex stesso carica le istruzioni. Verifica che questi dati corrispondano alle fonti delle istruzioni effettivamente caricate e li ricontrolla prima di una chiamata al modello. Se questi input cambiano o un’attività precedente non dispone di tali dati, occorre prepararla di nuovo; la sua cronologia e i file nativi del prodotto vengono conservati.
9. Le sessioni Foundry esistenti usano `suite-update-plan` e un record verificato `refresh --accept-suite-update` con impronte esatte dello stato sorgente e della destinazione. App state/1 non necessita di migrazione del formato per il toolkit. Le prove di integrazione Chat richiedono riferimenti correnti all’oggetto del contratto e una vera nuova osservazione; non si aggiungono riferimenti retroattivamente alle vecchie prove. Game usa l’aggiornamento del flusso 5→6 supportato mantenendo runtime2/model4/handoff1. Gli agenti generati richiedono confronto origine-destinazione e ripresa senza cronologia nascosta; nessun progetto viene azzerato.
10. Backup e ripristino del servizio riguardano solo il suo stato: esamina e valida il backup esatto, riconcilia i lavori e conserva le revoche dei permessi; non ripristinano database dei prodotti o effetti esterni. Il rollback delle competenze usa il registro effettivo dell’aggiornamento; quello del profilo ambiente usa il proprio registro e rifiuta variazioni successive. Installazione e controllo reali in WORK restano rinviati. Leggi la [migrazione dettagliata](../../releases/migrations/6.2.0.md) e la [guida del servizio](../../apps/agent-atelier/README.md) per recupero e limiti supportati.

## 0.1. Metodi di lavoro e verifiche precedenti

Il contesto proviene da requisiti, decisioni, identità e checkpoint nativi del progetto. Le competenze dirette possono compilare una proiezione esplicita con l’helper portabile; il pannello compila separatamente il pacchetto JavaScript della propria attività. Le dichiarazioni facoltative `atelier.context-bindings/1` verificano hash delle fonti, identità del progetto, ID attesi, requisiti obbligatori ed estratti letterali. Fonti necessarie mancanti o modificate bloccano la preparazione dipendente. I progetti senza dichiarazione mantengono il percorso precedente con copertura non verificata. Nessuno dei percorsi salva automaticamente ogni parola o fornisce un indice globale di embedding. RAG è ricerca condizionale per un’esigenza di conoscenza dimostrata, non l’autorità dello stato corrente dell’attività.

Attivare solo la responsabilità necessaria DATA, ANALYSIS, LLM, PREDICTION, ADAPTATION, MEDIA o EVALUATION sotto il responsabile esistente. Non ci sono sette nuove competenze installate, worker permanenti o framework obbligatori. Tredici tipi facoltativi di artefatto descrivono i record pertinenti di dati, modelli, esecuzione, valutazione e batch. L’helper in sola lettura verifica struttura dichiarata, riferimenti locali, limiti di leakage/retry e contabilità; non acquisisce dati, addestra modelli, certifica qualità o avvia job dei fornitori. Dalla radice del repository, leggere prima la guida degli helper effettivi:

```bash
python3 -B standards/context_capsule.py --help
python3 -B standards/ai_production.py --help
```

La versione 6.1 ha introdotto pacchetti agente generati con 15 risorse operative comuni e sette collegamenti locali alle istruzioni. I pacchetti 6.0 esistenti mantengono il contratto esatto di dodici risorse, quelli 5.x di otto; non sono certificati retroattivamente come 6.1. Aggiornare un agente tramite confronto fonte→destinazione, conservarne regole di dominio, identità, impostazioni e modifiche sconosciute, quindi verificare la ripresa senza cronologia e un’attività originale circoscritta. La sola installazione del toolkit non è adozione da parte del progetto.

Il pannello mostra requisiti leggibili, decisioni attuali, lavoro rinviato e verifiche delle fonti. «Stato nella fonte» conserva il testo del record e non sostituisce una decisione attuale successiva. Le conversazioni grandi usano pagine separate e limitate di turn/item con continuazione e copertura incompleta visibili. Caricamento e letture fallite hanno stati e ripristino espliciti. Installato, rilevato dall’host, collegato, eseguito e accettato dal proprietario sono fatti distinti. Il [manuale dei componenti](../evolution/2026-11-10/IMPLEMENTED-COMPONENTS.en.md) e il [caso reale dei feedback](../evolution/2026-11-10/REVIEW-STUDY.en.md) spiegano fonti, attivazione, destinatari e limiti.


Percorso della revisione grafica: un progetto normale apre la mappa delle attività documentate con lavori/risultati reali, prove e prossima azione. Selezionare un lavoro apre il relativo ispettore, inizialmente chiuso. Documenti fonte / Confronta le modifiche conserva l’intero spazio tecnico, fonti grezze, diff e azioni esistenti. La cronologia nativa viene letta su richiesta con copertura visibile. Solo un job runtime attivo e corrispondente prova l’esecuzione; il vecchio stato dispatched di un’attività non basta. Restano nomi di profilo comprensibili e tutte e sette le lingue; l’UI iniziale è ucraina e le preferenze salvate hanno precedenza. Il proprietario ha accettato la base visiva mostrata della revision6: «Так, цю основу приймаю». L’accettazione riguarda solo quella base; il caso A26 completo, tutti i 29 casi, la successiva logica di dati/assistenti e l’installazione restano separati. Render o CI precedenti non certificano byte modificati; la conservazione delle 11 viste, 41 azioni e 48 operazioni API va verificata sulla revisione esatta.

La vista facoltativa `current_checkpoint` deriva da una sola fonte esplicitamente collegata, obbligatoria e verificata nei byte, con ruolo `checkpoint`. Mostra `phase`, `completed`, `in_progress` e `next` della fonte, con hash e `status: declared`; non sovrascrive la fase nativa e non prova esecuzione o accettazione. Input assenti, ambigui, modificati o non supportati restituiscono `null` con una lacuna visibile, senza indovinare la fase corrente. La lacuna derivata non crea un nuovo blocco globale; gli errori esistenti delle fonti obbligatorie mantengono il loro effetto. Un risultato registrato si legge con le sue prove; il numero di file non è il numero di risultati consegnati.


Il reale errore di design modifica anche la regola comune di produzione UI. Creando o verificando un’interfaccia, dimostrare che l’utente previsto riconosce obiettivo, lavoro/risultato reale, attenzione richiesta e prossima azione utile; poi seleziona un record → legge prove/risultati comprensibili → esegue l’azione nell’ambito corretto. Tradurre il meccanismo operativo del riferimento nella propria attività: copiare il pannello di codice, la mappa o l’involucro non basta. Regola e profilo UI sono materializzati nei 33 pacchetti core esistenti e nell’orchestratore facoltativo. Le istruzioni caricate non sono un certificato né una garanzia automatica; verificare l’interfaccia reale e un percorso rappresentativo.


L’anteprima di un aggiornamento compatibile non è un’installazione. Se un predecessore noto e invariato risulta sconosciuto, confrontare byte esatti della release e modalità dei file con il registro canonico; non forzare la sovrascrittura né cambiare hash per nascondere differenze. Il percorso dell’orchestratore facoltativo verificato all’epoca, 1.1.0 → 1.2.0, usa il predecessore esatto di 40 file. Se la competenza di manutenzione è assente, mantenerla assente salvo richiesta d’installazione. Un aggiornamento prioritario limitato si ammette dopo la verifica degli invarianti interessati, separatamente dall’accettazione di ogni capacità o progetto.

## 1. Che cosa ti offre

Descrivi un risultato con parole comuni. Il sistema aiuta a trasformarlo in un compito concreto, coinvolge le specializzazioni pertinenti, mantiene insieme decisioni e requisiti e verifica il risultato rispetto all'obiettivo concordato.

Per esempio, «Aiutami a ridurre il carico sul database in questo backend» può diventare un'indagine mirata su query, confini delle transazioni, cache, misurazioni delle prestazioni e una modifica verificata. «Crea un'applicazione mobile per questo pubblico» richiede un percorso più ampio: ricerca, scelte di prodotto, design, architettura, implementazione, controlli di qualità, preparazione al rilascio e gestione operativa. Una piccola correzione deve rimanere una piccola correzione. Un prodotto completo deve conservare tutti i suoi requisiti, comprese le parti previste dopo la prima versione funzionante.

Una **competenza** è un insieme riutilizzabile di istruzioni operative, riferimenti e, a volte, script. Un **agente** applica un ruolo e queste istruzioni a un compito. Un **direttore** coordina una famiglia di prodotti. Un **costruttore** progetta un agente specializzato o un insieme riutilizzabile di competenze quando le famiglie esistenti non coprono il lavoro. Operano attraverso ChatGPT o Codex e gli strumenti realmente disponibili nell'ambiente. Installare istruzioni non crea un server in esecuzione, non acquista servizi, non concede permessi sui repository e non avvia un processo permanente in background.

Il valore sta nel flusso di lavoro organizzato: un brief condiviso, requisiti espliciti, specialisti pertinenti, decisioni conservate, passaggi di consegne verificabili e un modo per riprendere il lavoro. Il repository non dichiara una superiorità misurata, guadagni garantiti, accettazione garantita negli store o idoneità automatica alla produzione.

## 2. Scegli da dove iniziare

| La tua situazione | Inizia con | Una prima richiesta utile |
| --- | --- | --- |
| Vuoi un unico accesso per un’attività, un progetto o un miglioramento del sistema | `atelier-orchestrator` | «Ecco il risultato necessario. Ripristina il contesto del progetto, scegli le competenze disponibili adatte e completa il lavoro concordato». |
| Vuoi un agente specializzato su misura per un lavoro ricorrente | `agent-foundry` | «Crea un agente che indaghi i problemi di prestazioni nei nostri servizi Go. Chiarisci prima le sue responsabilità, le prove e gli accessi.» |
| Vuoi una competenza riutilizzabile o una famiglia coordinata di competenze | `design-specialist-skills` | «Progetta un flusso di revisione riutilizzabile per le nostre integrazioni basate su eventi, compreso il recupero dagli errori.» |
| Vuoi sviluppare un'applicazione o un prodotto esistente | `app-atelier-director` | «Continua questa applicazione dal suo checkpoint. Conserva i requisiti accettati e individua il prossimo risultato utile da consegnare.» |
| Vuoi un chatbot, un bot di assistenza o un compagno di conversazione | `chatbot-atelier-director` | «Progetta un bot per questo pubblico e questi canali, comprendendo lingua, memoria, azioni e costi operativi.» |
| Vuoi un gioco mobile o continuare un gioco esistente | `gamedev-director` | «Sviluppa concetti di gioco attorno a questa esperienza, con controlli significativi, progressione e un percorso di produzione fattibile.» |
| Conosci già la fase precisa | Lo specialista pertinente qui sotto | «Esamina questa schermata di pagamento rispetto al design approvato e ai criteri di accettazione.» |

Non devi memorizzare tutti i 33 nomi. Usa un direttore per un prodotto oppure un costruttore per un nuovo flusso specialistico. Puoi anche richiedere esplicitamente una competenza dal selettore dell'ambiente. In Work la forma consueta è `@skill-name`; in Codex è `$skill-name`. I selettori disponibili e i nomi visualizzati possono differire tra le versioni dell'ambiente. Quando serve certezza, chiedi di mostrare la fonte esatta caricata.

### Il catalogo completo

#### Due costruttori

| Competenza | Che cosa ti aiuta a produrre |
| --- | --- |
| `agent-foundry` | Un agente specializzato o una famiglia coordinata di agenti, modellata su un dominio reale, responsabilità, strumenti, conoscenze, controlli e un percorso operativo praticabile. Il suo primo compito è progettare l'agente, anziché svolgere senza dichiararlo il futuro progetto dell'agente. |
| `design-specialist-skills` | Competenze riutilizzabili e famiglie di competenze per un compito definito: specializzazioni giuste, criteri di qualità, riferimenti, strumenti e sequenza di lavoro. |

#### Team applicazioni — 11 competenze

| Competenza | Che cosa fa in parole semplici |
| --- | --- |
| `app-atelier-director` | Mantiene coerente il progetto dell'applicazione dalla prima idea allo sviluppo e alla gestione operativa. |
| `app-atelier-research` | Studia utenti, bisogni, alternative e riscontri di mercato prima che il team investa in una direzione di prodotto. |
| `app-atelier-concepts` | Confronta opzioni di prodotto complete: utilità, esperienza, modello di business, costi e perimetro realistico. |
| `app-atelier-specification` | Trasforma il prodotto scelto in requisiti precisi e contratti per comportamento, dati, API, autenticazione e pagamenti. |
| `app-atelier-experience` | Crea e verifica brand, schermate, stati, onboarding, accessibilità, localizzazione e materiali di design per la produzione. |
| `app-atelier-build` | Implementa i client Android, iOS e web concordati, il backend e le integrazioni necessarie, con build riproducibili. |
| `app-atelier-support` | Progetta e implementa il bot di assistenza del prodotto e il flusso delle conoscenze, comprese escalation e azioni controllate. |
| `app-atelier-qa` | Verifica in modo indipendente requisiti, design, implementazione, pagamenti, privacy, recupero e preparazione al rilascio quando è disponibile un soggetto indipendente. |
| `app-atelier-release` | Verifica presto la fattibilità del rilascio, poi prepara firma, schede negli store, distribuzioni, ricevute e rollback entro il perimetro autorizzato. |
| `app-atelier-growth` | Valuta e prepara canali di acquisizione pertinenti, contenuti e misurazioni, quindi attiva un percorso autorizzato quando il prodotto è pronto. |
| `app-atelier-operations` | Gestisce incidenti, metriche di prodotto, richieste di assistenza, costi, backup, modifiche e continuità operativa. |

#### Team chatbot — 11 competenze

| Competenza | Che cosa fa in parole semplici |
| --- | --- |
| `chatbot-atelier-director` | Coordina l'intero ciclo di vita di un bot e ne conserva le capacità esistenti quando il lavoro riprende. |
| `chatbot-atelier-research` | Studia pubblico, dominio tematico, vincoli delle piattaforme, integrazioni e fattibilità pratica. |
| `chatbot-atelier-specification` | Definisce regole, stato, dati, strumenti, eventi, errori, privacy e criteri di accettazione del bot. |
| `chatbot-atelier-conversation` | Sviluppa lingua, carattere, domande utili, iniziativa, pulsanti e comportamento nelle conversazioni personali o di gruppo. |
| `chatbot-atelier-knowledge` | Progetta fonti di conoscenza e memoria con ambiti definiti, recupero delle informazioni quando utile, correzioni, scadenza, eliminazione e privacy. |
| `chatbot-atelier-integrations` | Costruisce adattatori per piattaforme, callback, strumenti, attività pianificate e azioni esterne affidabili con recupero e prove di consegna. |
| `chatbot-atelier-media` | Crea e integra identità visiva, immagini, animazioni, audio e voce del bot tramite gli strumenti disponibili. |
| `chatbot-atelier-build` | Implementa il bot completo concordato, compresi il runtime necessario e l'integrazione in produzione. |
| `chatbot-atelier-qa` | Verifica conversazione, conoscenze, privacy, azioni, media, runtime e scenari negativi sulla base di prove reali. |
| `chatbot-atelier-release` | Prepara ed esegue un rilascio autorizzato con identificazione esatta di fonte/build, controlli di consegna, compatibilità dei dati e rollback. |
| `chatbot-atelier-operations` | Mantiene affidabilità, qualità della conversazione, assistenza, costi, migrazioni e sviluppo continuo. |

#### Team giochi — nove competenze

| Competenza | Che cosa fa in parole semplici |
| --- | --- |
| `gamedev-director` | Coordina il progetto di gioco conservandone direzione creativa accettata, decisioni e checkpoint. |
| `gamedev-studio` | Definisce o ripristina identità dello studio, originali approvati del brand, identità dello sviluppatore e preparazione degli account. |
| `gamedev-concepts` | Produce concetti di gioco distinti con controlli, sistemi interagenti, progressione, direzione artistica e un percorso di produzione fattibile. |
| `gamedev-preproduction` | Espande il concetto scelto in un design di gioco e tecnico dettagliato, regole numeriche, cataloghi, stati e piano di produzione. |
| `gamedev-assets` | Crea e integra grafica, animazioni, UI, suoni e feedback aptico, conservando le fonti accettate e il loro rapporto con gli asset a runtime. |
| `gamedev-build` | Implementa il gioco mobile nativo: controlli, camera, gameplay, nemici, mondo, progressione, economia, salvataggi e build per piattaforma. |
| `gamedev-qa` | Verifica gameplay reale, comportamento sui dispositivi, controlli, salvataggi, prestazioni e requisiti, distinguendo le prove a runtime dai controlli documentali. |
| `gamedev-release` | Prepara firma, binari esatti, materiali per gli store, acquisti, privacy, distribuzione graduale e recupero per un rilascio autorizzato. |
| `gamedev-liveops` | Sviluppa e mantiene il gioco rilasciato usando telemetria osservata, incidenti, progressione, contenuti, economia e modifiche compatibili. |

Queste sono responsabilità, non la promessa che 33 agenti lavorino contemporaneamente. Il sistema deve scegliere il team e il livello di impegno necessari al compito. Una revisione è indipendente soltanto quando viene svolta realmente da un altro soggetto; l'autoverifica dell'autore deve essere indicata come tale.

## 3. Scegli la lingua prima dell'installazione

Apri la guida tradotta dai collegamenti sopra. L'inglese è la lingua predefinita quando non viene indicata una preferenza. Le guide tradotte coprono gli stessi passaggi; codice, nomi stabili delle competenze, nomi dei file e identificatori dei protocolli rimangono invariati affinché i comandi funzionino in modo coerente.

All'inizio dell'installazione o del progetto, incolla questo testo e sostituisci la lingua:

```text
La mia lingua di lavoro è l'italiano (it). Usala per spiegazioni, domande,
aggiornamenti di stato, istruzioni per i passaggi di consegne e rapporti destinati
all'utente. Mantieni invariati i nomi stabili delle competenze, la sintassi dei
comandi e gli identificatori tecnici. Registra questa preferenza nel contesto
salvato del progetto e nei passaggi di consegne. Chiedi separatamente quale
lingua deve usare il prodotto che stiamo costruendo.
```

La lingua della documentazione, quella della conversazione e quella del prodotto sono scelte distinte. Per esempio, puoi leggere la guida ucraina, lavorare con l'agente in ucraino e pubblicare un'applicazione in inglese e tedesco. Specifica tutte e tre quando pertinente. Registra la preferenza nel modello del contesto di progetto o in un file equivalente esistente e includila in ogni passaggio di consegne. Cambiare soltanto la lingua della pagina nel browser non imposta la lingua di un'altra chat.

## 4. Prepara account e fonti

1. Accedi all'account ChatGPT o Codex nel quale intendi usare la suite. Verifica che la modalità richiesta e gli strumenti di gestione delle competenze siano realmente disponibili in quell'account o spazio di lavoro.
2. Apri `https://github.com/alex-hohaizel/codex-agents`. La visibilità del repository è attualmente sotto il controllo del proprietario. Un repository privato richiede un account GitHub autorizzato e una connessione che abbia accesso proprio a quel repository.
3. In Work, collega o seleziona GitHub tramite l'interfaccia Plugins/connessioni disponibile. Se l'accesso è limitato a repository selezionati, includi `alex-hohaizel/codex-agents`. Chiedi a Work di leggere `README.md` e indicare branch e revisione ai quali può realmente accedere.
4. In Codex locale, autorizza l'accesso Git locale se intendi clonare un repository privato. Una connessione GitHub in Work non dimostra che Terminale sul tuo computer possa autenticarsi.
5. Usa una release identificata o un commit esatto per l'installazione. Salva tale identificatore. Leggere un branch `main` non fissato mentre cambia può mescolare versioni.
6. Per le competenze gestite in Codex, scarica l’archivio Codex della versione stabile scelta e segui la [migrazione con verifica della firma](../../releases/migrations/6.2.0.md). **Code → Download ZIP** su GitHub e i cloni Git forniscono le fonti da esaminare, da usare in Work o da provare in un ambiente isolato. Le fonti contengono `kit/manifest.json`, `kit/portable/` e `kit/skills/`.
7. Non collocare download, piani o backup in una directory di rilevamento delle competenze. Va bene una cartella normale come Download o uno spazio dedicato alla gestione delle competenze.

Per Git locale, usa un branch confermato e una nuova destinazione che non contenga altro lavoro:

```bash
git clone --branch main https://github.com/alex-hohaizel/codex-agents.git "codex-agents"
cd "codex-agents"
git rev-parse HEAD
git status --short
```

Un clone su `main` è una comoda copia di lavoro delle fonti. Prima di applicare un aggiornamento, conferma che il suo SHA corrisponda alla release scelta. Non incollare token di accesso in chat, file di progetto, comandi shell o documenti di passaggio di consegne. Usa la connessione dell'account o il flusso di gestione delle credenziali della piattaforma.

## 5. Installa in Work da un account nuovo

### Che cosa fa questo percorso

Salva le 33 competenze riutilizzabili come competenze personali tramite il processo di gestione supportato dall'ambiente. Collegare semplicemente GitHub, caricare uno ZIP, leggere questa guida o aggiungere file del repository come fonti di progetto non dimostra che una competenza sia stata installata o caricata.

### Passo dopo passo

1. Apri Work e crea o apri un progetto di gestione delle competenze. Qui gestisci il toolkit, anziché il prodotto che costruirai in seguito.
2. Scegli la lingua con il blocco della sezione 3.
3. Fornisci accesso alla revisione selezionata del repository. Se Work non può leggere file GitHub privati, collega quel repository oppure allega il pacchetto selezionato tramite l'interfaccia file disponibile.
4. Richiama la funzionalità disponibile Skill Creator/gestione delle competenze. Chiedile di esaminare il pacchetto prima di cambiare le voci installate.
5. Incolla il blocco di installazione qui sotto. Autorizza l'installazione nel perimetro indicato e le verifiche necessarie.
6. Lascia che Work esamini l'inventario esistente delle competenze per nome stabile. Per un account nuovo deve creare le voci mancanti; per uno esistente deve aggiornare le corrispondenti voci personali e conservare le competenze non pertinenti.
7. Conserva il rapporto di installazione. Deve identificare ognuna delle 33 competenze, versione, revisione della fonte, risultato ed errori non risolti.
8. Aggiorna o riapri la pagina Skills se la visualizzazione non è aggiornata. Apri una nuova chat nel progetto del prodotto previsto ed esegui il controllo di caricamento e quello pratico descritti sotto.

```text
Installa le 33 competenze personali riutilizzabili dalla revisione selezionata
e verificata di alex-hohaizel/codex-agents, usando kit/manifest.json e kit/skills/.
La mia lingua di lavoro è l'italiano (it).

Usa il processo di gestione delle competenze personali supportato dall'ambiente.
Esamina le voci esistenti per nome stabile, verifica il pacchetto, conserva le
competenze non pertinenti e l'identità visiva esistente, quindi installa o aggiorna
le voci corrispondenti. Conserva backup e provenienza esatta delle fonti. Non
installare globalmente agenti specifici di progetto. Non modificare dati di
prodotto, servizi di produzione o impostazioni dell'account.

Riporta ogni nome stabile, versione, revisione della fonte e stato
create/update/noop/failure. Distingui una competenza salvata dal rilevamento
dell'ambiente e dall'uso reale in un compito. Se la gestione delle competenze non
è disponibile, spiega esattamente quale capacità manca; non descrivere una copia
caricata o di sola lettura come installata.
```

La procedura di gestione supportata da Work può salvare una competenza alla volta. Un risultato parziale deve nominare le voci completate e quelle rimanenti, consentendo di proseguire in sicurezza anziché ricominciare. Eseguire l'updater portatile di Codex in un filesystem cloud non dimostra che la tua directory personale di competenze Work sia stata aggiornata.

## 6. Installa o aggiorna in Codex

### Il percorso più semplice: chiedi a Codex di eseguire l'installazione controllata

1. Scegli la versione stabile e procurati la revisione e gli hash approvati secondo la [migrazione con verifica della firma](../../releases/migrations/6.2.0.md).
2. Apri Codex nello spazio di gestione delle competenze esistente. Se è la prima installazione, apri il checkout o un'altra cartella normale di gestione; non occorre un nuovo repository di prodotto.
3. Fornisci a Codex il percorso della copia fidata, l’archivio Codex scaricato e gli identificativi e gli hash approvati separatamente. Su Mac, seleziona la cartella nel Finder e premi **Option + Command + C** per copiarne il percorso.
4. Incolla il blocco sotto dopo aver impostato la lingua preferita.
5. Esamina il rapporto finale di installazione e conserva il journal e la posizione del backup.
6. Apri una nuova chat nel progetto reale del prodotto per i controlli di caricamento e quelli pratici.

```text
Installa le 33 competenze personali di base della versione stabile scelta
di alex-hohaizel/codex-agents. Segui la migrazione Codex con verifica della firma nella sezione 0.
Usa il kit indicato nella ricevuta di verifica. Prima di applicare il piano, verifica che
l’hash del manifesto nel piano corrisponda a quello approvato.
La mia lingua di lavoro è l’italiano (it).

Questo autorizza audit → apply → verify locali, piani esatti e backup per questa
suite. Leggi kit/manifest.json e --help dell'updater. Verifica l'integrità del
pacchetto. Esamina le directory personali e le copie di progetto note. Salva piani
e backup fuori dalle radici di rilevamento delle competenze. Applica soltanto il
piano esatto pronto. Conserva modifiche locali sconosciute e riporta i file in
conflitto; non aggirare i controlli delle divergenze.

Conserva icon_small, icon_large, brand_color, percorsi e byte delle icone esistenti,
compresi i riferimenti storici ./assets/. Verifica usando il journal esatto
restituito da apply. Riporta canonical_core_verified, visual_preservation_verified,
conteggi updated/noop, blockers, failures e duplicates.

Non modificare prodotti, produzione, plugin o configurazione dell'ambiente.
Verifica poi separatamente il rilevamento da parte dell'ambiente dei due
costruttori e dei direttori App, ChatBot e Game. Non trattare i file installati
come prova dell'uso reale in un compito.
```

### Percorso da Terminale per chi vuole i comandi esatti

Per un’installazione attiva di Codex, segui la [migrazione con verifica della firma](../../releases/migrations/6.2.0.md) e usa il kit esatto indicato nella ricevuta. I comandi qui sotto, eseguiti dalla radice del repository, provano il programma di aggiornamento portatile in un ambiente isolato. Richiede Python 3.9 o successivo e usa la libreria standard. Audit legge il kit e i percorsi di prova e registra il piano. Apply modifica solo l’ambiente di test selezionato e crea un registro.

```bash
python3 kit/portable/update_skill_suite.py --help
fixture_root=/absolute/path/to/isolated-test
mkdir -p "$fixture_root"
python3 kit/portable/update_skill_suite.py audit --kit kit --destination "$fixture_root/.agents/skills" --legacy-root "$fixture_root/.codex/skills" --backup-root "$fixture_root/backups" --plan "$fixture_root/core-plan.json"
python3 kit/portable/update_skill_suite.py apply --plan "$fixture_root/core-plan.json"
```

Leggi il risultato di `apply`. Copia il suo percorso `journal` esatto nel comando di verifica:

```bash
python3 kit/portable/update_skill_suite.py verify --kit kit --destination "$fixture_root/.agents/skills" --legacy-root "$fixture_root/.codex/skills" --journal /absolute/path/from-apply/journal.json
```

Il percorso finale sopra è un segnaposto. Sostituiscilo; non eseguirlo letteralmente. Per impostazione predefinita l'updater usa `~/.agents/skills` come destinazione e controlla la radice storica `~/.codex/skills`. Se il tuo ambiente usa un'altra radice personale supportata, usa esplicitamente e in modo coerente gli argomenti `--destination` e `--legacy-root`. Consulta prima `audit --help`. Aggiungi `--project-root /absolute/path/to/product` per controllare le copie locali al prodotto pertinenti. L'updater non rimuove automaticamente una copia di progetto che nasconde una competenza personale.

Un'installazione dei file riuscita significa 33 fonti verificate alla versione prevista, nessun blocker/failure/duplicate irrisolto, `canonical_core_verified=true` e `visual_preservation_verified=true` dalla verifica che usa il journal apply effettivo. Un controllo degli hash senza quel journal non può dimostrare la conservazione delle tue icone esistenti. Fermati in presenza di un conflitto e conserva il lavoro locale; non usare una sostituzione forzata per far sembrare pulito il rapporto.

### Verifica il caricamento separatamente dall'installazione

Chiedi a Codex o Work in una nuova chat di prodotto:

```text
Prima di modificare qualsiasi cosa, identifica la fonte caricata esatta e la
versione di agent-foundry, design-specialist-skills e dei tre direttori di prodotto.
Conferma quali istruzioni adattive, di ricerca, identità visiva e Work↔Codex hai
realmente letto. Riporta separatamente le fonti non disponibili.
```

Assegna poi un piccolo compito reale con un input noto e un criterio di accettazione. Per esempio, chiedi al direttore applicazioni di esaminare gli stati di errore di una schermata rispetto a un requisito esistente oppure a un costruttore di delineare le responsabilità di un agente specializzato. Questo verifica il comportamento. Non certifica ogni capacità di prodotto. Mantieni installazione dei file, caricamento dell'ambiente, uso pratico e accettazione del prodotto come risultati separati.

## 7. Usa il sistema per un compito reale

### Un compito ingegneristico circoscritto

```text
Indaga le query ripetute al database in questo endpoint. Conservane API e
comportamento di business. Leggi prima il codice e le misurazioni esistenti.
Identifica le prove mancanti, proponi la più piccola indagine utile e implementa
una correzione motivata in questo branch. Verifica la correttezza e mostra
misurazioni prima/dopo dove l'ambiente le rende possibili.
```

Questo non richiede una nuova azienda, un prodotto, un brand o uno studio di mercato completo. Un costruttore può progettare un investigatore riutilizzabile se desideri questo flusso come agente duraturo; per un compito singolo, usa gli strumenti e le istruzioni pertinenti già esistenti. Il sistema non deve creare un nuovo agente solo perché un compito è tecnico.

### Un'applicazione completa

```text
BRIEF: Voglio un'applicazione per [pubblico] che risolva [problema]. Le piattaforme
previste sono [piattaforme], il budget è [budget] e il mio ruolo è [ruolo]. Chiarisci
le incognite, studia alternative reali e prepara opzioni complete. Mantieni
visibili nel piano tutti i miei requisiti, compresi design, lingua, assistenza
e monetizzazione. Non scegliere un concetto al posto mio senza dichiararlo.
```

Il team deve studiare ciò che conta, confrontare le opzioni e identificare ostacoli al rilascio o legati agli account prima di una grande implementazione. Dopo aver scelto un concetto, conserva i riferimenti di design selezionati e tutti i requisiti concordati. Una prima versione funzionante è un checkpoint in quel piano, non il permesso di scartare il resto.

### Un gioco mobile

```text
BRIEF: Sviluppa concetti di gioco mobile distinti per [pubblico/esperienza]. Copri
controlli e feedback, sistemi interagenti, nemici, progressione significativa,
direzione artistica, monetizzazione e un percorso di produzione Android/iOS
fattibile. Mostra concetti visivi confrontabili. Conserva l'identità selezionata
negli asset e nell'implementazione giocabile. Definisci controlli reali sui dispositivi.
```

Un'immagine concettuale non può dimostrare animazione, controlli touch, prestazioni o recupero dei salvataggi. Il flusso per i giochi deve collegare la promessa visiva selezionata ad asset sorgente modificabili e a una sezione rappresentativa giocabile prima di produrre l'intero insieme di asset.

## 8. Work e Codex sullo stesso progetto

Work è utile dove sono disponibili le fonti necessarie, gli strumenti di ricerca e design e i servizi collegati. Codex è utile dove sono disponibili checkout delle fonti, runtime, strumenti di build e integrazioni locali o con dispositivi. Entrambe le modalità possono fare di più quando hanno le capacità giuste. Scegli in base ad accessi e prove reali, anziché assegnare ogni attività di ragionamento a una modalità e ogni attività di codice all'altra.

Crea una sola identità per il prodotto. Nomi come `My Product [WORK]` e `My Product [CODEX]` aiutano la navigazione, ma non dimostrano che i due progetti contengano lo stesso prodotto. Registra repository, branch, sottodirectory, identificatori di progetto e fonti dei checkpoint. Una nuova chat deve rimanere all'interno di quel progetto esistente.

### Mantieni un piccolo contesto condiviso

Usa il modello di contesto di progetto del repository o un equivalente già presente nel prodotto. Registra almeno: identificatore di progetto; repository e branch; SHA completo del commit attuale; identificatore del compito; fase attuale; lingue di lavoro e del prodotto; versione del toolkit e ricevuta di installazione; decisioni accettate; fonte completa dei requisiti; fonte dei riferimenti di design; perimetro autorizzato; checkpoint attuale; effetti o decisioni irrisolti; prossima azione. Tieni le credenziali fuori da questo registro.

### Work → Codex locale, passo dopo passo

1. Chiedi a Work: «Continua questa fase in Codex. Prepara il passaggio di consegne per questo progetto esistente.»
2. Work deve identificare l'esatto prossimo risultato da consegnare e le prove richieste per accettarlo. Deve salvare o fornire requisiti, decisioni, fonti e checkpoint pertinenti.
3. Se è disponibile un canale condiviso autorizzato, Work può salvare il passaggio di consegne e verificare la revisione salvata. Salvare un file non dimostra che sia iniziata un'altra sessione Codex.
4. Apri il checkout locale esistente. Se non c'è una copia locale, clona repository e branch confermati nella cartella scelta. Autenticati localmente per i repository privati.
5. Prima di aggiornare il checkout, esaminalo:

```bash
git remote get-url origin
git branch --show-current
git rev-parse HEAD
git status --short
```

6. Se l'albero di lavoro è pulito e serve un aggiornamento su quel branch, usa `git pull --ff-only origin <confirmed-branch>` con il vero nome del branch. Conferma lo SHA completo risultante. Se esistono modifiche locali o una cronologia divergente, conservale e risolvi la discrepanza prima del lavoro dipendente.
7. Apri la cartella esatta nell'interfaccia progetti di Codex. Per un prodotto esistente, usa il progetto esistente; se necessario aggiungi la cartella tramite l'interfaccia disponibile per modificare il progetto.
8. Incolla il blocco compilato qui sotto. Codex prima conferma identità del repository, revisione, modifiche locali, permessi e checkpoint, poi lavora sull'azione circoscritta.
9. Conserva il rapporto del risultato, i riferimenti a commit/build e le prove dei test per il passaggio di consegne di ritorno.

### Codex → Work, passo dopo passo

1. Chiedi a Codex di preparare un passaggio di consegne del risultato o di un nuovo compito per lo stesso progetto esistente.
2. Includi file realmente modificati, SHA completo o revisione dell'artefatto, controlli eseguiti, limiti, decisioni aperte e prossima azione. Specifica se le modifiche sono locali, registrate in un commit o pubblicate.
3. Se è autorizzata la pubblicazione delle modifiche concordate su un branch nominato, pubblica soltanto quel perimetro e verifica la revisione remota. Altrimenti fornisci un artefatto controllato tramite il canale disponibile. Un percorso locale sul Mac non è automaticamente leggibile da Work.
4. Apri il progetto Work esistente, collega il repository pertinente o allega l'artefatto esatto e incolla il passaggio di consegne.
5. Work legge le fonti reali e verifica la revisione in ingresso prima di esaminare o continuare. Deve segnalare esplicitamente i file inaccessibili.
6. Registra l'accettazione separatamente dalla consegna e dall'esecuzione. Un rapporto che indica l'esistenza di una build non equivale all'accettazione del prodotto.

### Passaggio di consegne da copiare

Sostituisci ogni campo tra parentesi quadre prima di usare questo blocco:

```text
Continua il progetto esistente [ID/nome progetto] in [Work/Codex].
Lingua di lavoro: [lingua/codice]. Lingue del prodotto: [lingue].
Repository: [URL]. Branch/sottodirectory: [branch/percorso].
Revisione in ingresso: [SHA completo o revisione esatta dell'artefatto].
ID del compito e fase: [ID/fase].
Checkpoint: [fonte esatta accessibile].
Requisiti e decisioni accettate: [fonti esatte].
Riferimenti di design e identità: [fonti esatte, se pertinenti].
Risultato atteso e accettazione: [risultato/controlli concreti].
Perimetro autorizzato: [che cosa può essere modificato o pubblicato].
Lavoro completato e prove: [fatti e riferimenti].
Decisioni aperte, blocchi o effetti esterni incerti: [dettagli/nessuno].
Prossima azione: [un'azione concreta].

Verifica prima identità del progetto, revisione, strumenti disponibili e permessi.
Conserva ogni requisito e decisione accettati. Non reinizializzare il prodotto.
Distingui passaggio preparato, consegna verificata, ricezione, esecuzione,
risultato e accettazione. Continua il lavoro autorizzato realmente possibile.
```

## 9. Riprendi dopo una chat interrotta

Apri una nuova chat nello stesso progetto e chiedi di ripristinare l'ultimo checkpoint verificato. Fornisci la fonte del checkpoint se non è già accessibile. Prima di continuare deve riconciliare compito, requisiti, revisione delle fonti, file attuali e risultati esterni reali.

```text
Ripristina questo compito esistente dall'ultimo checkpoint verificato e dalle
fonti reali. Conserva requisiti, decisioni, permessi, risultati completati ed
effetti esterni incerti. Verifica la revisione attuale e chi è responsabile della
prossima azione. Prima di ripetere una distribuzione, un pagamento, un messaggio
o un'altra azione esterna, controlla se il tentativo precedente si è realmente
concluso. Continua il lavoro autorizzato disponibile e registra un nuovo checkpoint.
```

Una conversazione bloccata non dimostra che l'ultima operazione sia fallita. Il recupero deve controllare il risultato reale prima di riprovare un'azione che potrebbe essere duplicata.

## 10. Aggiorna le versioni senza perdere un progetto esistente

### Leggi prima il registro della release

Ogni release deve spiegare che cosa è cambiato, quali utenti sono interessati, prerequisiti, passaggi di installazione, passaggi di adozione nel progetto, verifica, limiti noti e rollback. Anche la guida generale deve cambiare quando cambia il flusso ordinario. Non affidarti soltanto a un numero di versione.

La release 6.0.0 conserva i 33 nomi stabili e l’identità delle icone, rafforzando prove, dipendenze delle fonti, lettura JSON e scritture dello stato. Aggiunge profili di produzione/contesto autosufficienti e una fedeltà esplicita ai riferimenti. I numeri storici dei protocolli e degli schemi runtime del progetto restano distinti; rinominare un vecchio schema con il numero della suite senza migrazione interrompe la compatibilità.

### Progetti esistenti Agent Systems 2.3 / Game 4.3

1. Salva il checkpoint attuale del progetto, requisiti accettati, decisioni, originali di design, revisione delle fonti, versione del toolkit ed effetti esterni noti.
2. Registra da dove ogni competenza o agente di progetto viene realmente caricato. Fai l'inventario delle copie personali e locali al progetto; non presumere che cambiare una directory globale cambi ogni progetto.
3. Installa la suite di destinazione tramite il percorso Work o Codex pertinente descritto sopra. Conserva la versione della fonte e la ricevuta di installazione.
4. Riapri il progetto esistente ed esegui una revisione di compatibilità in sola lettura prima della prossima azione dipendente.
5. Chiedi al direttore o al costruttore di confrontare lo stato attuale del progetto con il nuovo flusso. Identifica un aggiornamento esplicito dello stato nativo o del flusso soltanto dove necessario. Conserva comportamento del prodotto, scelte accettate ed effetti sconosciuti.
6. Visualizza in anteprima le modifiche esatte. Se serve una migrazione dello stato, usa il relativo strumento supportato e il suo vero `--help`; lega l'anteprima all'hash dello stato sorgente, all'hash della suite di destinazione e alla fonte di autorizzazione. Applica il piano esaminato e autorizzato anziché inventare un'approvazione storica.
7. Ricontrolla ogni requisito interessato e i criteri di accettazione della fase attuale. Esegui un piccolo compito reale di continuazione e salvane le prove.
8. Registra nel checkpoint del prodotto la versione adottata del toolkit. Conserva il registro della migrazione affinché la prossima chat possa spiegare il passaggio.

Game6.0.0 contiene un percorso di aggiornamento del flusso soggetto a revisione per progetti 4.2.0/4.3.0/5.0.0 mantenendo lo schema runtime 2.0.0. Il suo uso dipende dallo stato reale del progetto e dagli input supportati dallo strumento. Anche i progetti App e ChatBot richiedono la propria revisione di stato e compatibilità; non devono passare per una migrazione Game soltanto perché la suite condivide una versione.

### Agenti costruiti in precedenza con un costruttore

Aggiornare il costruttore non riscrive gli agenti che ha creato in precedenza. Questi agenti possono contenere regole, strumenti, conoscenze e identità visiva specifici di progetto. Fanne l'inventario nei rispettivi progetti. Confronta vecchia fonte, modifiche locali e nuova fonte proposta. Conserva le prove originali di proprietà/installazione. Se mancano, prepara un confronto e un piano espliciti di adozione; non fabbricare una vecchia ricevuta. Esegui casi di regressione per le responsabilità reali dell'agente e registra separatamente la versione adottata.

Il repository riutilizzabile esclude i pacchetti sorgente privati degli agenti di prodotto. L'aggiornamento di un singolo progetto appartiene alle fonti controllate e al registro di migrazione di quel progetto, non all'installazione globale delle competenze di tutti.

### Conserva l'identità visiva

Icone Codex esistenti, percorsi delle icone, colore e byte delle icone devono sopravvivere agli aggiornamenti ordinari. Una nuova versione non è un'istruzione per ridisegnare una competenza o un prodotto esistente. Le nuove competenze prive di identità possono ricevere lo stile di sistema o di progetto appropriato. Work può gestire autonomamente un avatar di servizio; mantieni distinto il comportamento di visualizzazione dell'ambiente dall'identità Codex portatile. Conserva gli originali selezionati del design del prodotto e del gioco, non soltanto una loro descrizione verbale.

### Esegui il rollback con attenzione

Per un'installazione della suite Codex, usa il journal esatto di installazione:

```bash
python3 kit/portable/update_skill_suite.py rollback --journal /absolute/path/from-apply/journal.json
```

Il rollback verifica i backup e protegge le modifiche successive sconosciute. Annulla l'installazione delle competenze rappresentata da quel journal. Non annulla una migrazione dei dati di prodotto, una distribuzione, un messaggio, un acquisto o un'altra azione esterna. Il ripristino in Work deve usare il percorso di gestione delle competenze supportato e la fonte precedente salvata. Un rollback dello stato del prodotto richiede la propria procedura di recupero esaminata.

## 11. Mantieni completi gli aggiornamenti futuri

Per ogni futura modifica del toolkit, aggiorna questo repository con fonti canoniche, requisiti interessati, contenuto dei pacchetti, registro della versione, passaggi di migrazione, prove di verifica e modifiche necessarie alla guida o alle traduzioni. Conserva i registri delle release precedenti. Ricostruisci pacchetti e metadati di integrità dalle fonti controllate; evita di pubblicare un archivio assemblato da una cache dell'ambiente non aggiornata.

Pubblica insieme le fonti approvate, i requisiti interessati, le versioni, le istruzioni e i pacchetti pertinenti nel branch attivo di GitHub. Usa `main` se il proprietario non ha indicato un altro branch attivo. Segui il processo di revisione e CI del repository e verifica la revisione integrata nel branch di destinazione. [Regole di aggiornamento del repository](../../governance/UPDATE_CONTRACT.md)

Esegui i comandi di controllo e creazione dei pacchetti del repository secondo il loro `--help` attuale e la documentazione per i manutentori. Conferma il commit remoto dopo la pubblicazione. «Salvato localmente», «registrato in un commit», «pubblicato», «installato», «caricato» e «adottato da un progetto» sono stati distinti. Se l'accesso impedisce la pubblicazione, conserva il lavoro completato e riporta la revisione esatta non sincronizzata.

Una regola del repository è efficace quando un agente futuro la legge in un ambiente con gli accessi necessari. Non è un ascoltatore globale di tutte le altre chat e di tutti i computer. Inizia un futuro compito di gestione delle competenze collegando questo repository e leggendo `AGENTS.md`, requisiti e ultimo registro della release. Un servizio separato di sincronizzazione pianificata richiederebbe un proprio runtime reale e un'autorizzazione; la suite non ne crea uno di nascosto.

## 12. Risoluzione dei problemi

| Sintomo | Che cosa controllare dopo |
| --- | --- |
| Work non può leggere il repository | Verifica account GitHub, concessione per lo specifico repository privato e connessione selezionata; chiedi di leggere un file noto. |
| Il clone locale chiede l'autenticazione | Configura l'autorizzazione Git locale usando il flusso delle credenziali della piattaforma. La connessione Work è separata. |
| Le competenze non appaiono dopo il salvataggio | Aggiorna o riapri la pagina Skills, poi usa una nuova chat di progetto e verifica il rilevamento reale delle fonti. |
| Appaiono due copie della stessa competenza | Esamina i nomi stabili nelle radici personali e di progetto. Conserva le modifiche locali e risolvi la fonte duplicata esatta; non eliminare competenze non pertinenti. |
| L'updater segnala divergenze o un conflitto | Salva il diff locale e confronta i file nominati con la fonte selezionata. Usa un piano di riconciliazione esaminato. |
| Un controllo dei file è riuscito, ma l'agente si comporta come prima | Verifica la fonte realmente caricata dall'ambiente, poi esegui un piccolo compito; la sola integrità dei file non basta. |
| Work non vede codice modificato su un Mac | Pubblica il perimetro autorizzato o allega un artefatto esatto; un percorso locale da solo non concede accesso. |
| Una nuova chat ha perso le decisioni | Ripristina checkpoint e fonti complete dei requisiti prima di continuare. Aggiorna il contesto salvato. |
| La prima versione funzionante omette design o lingua concordati | Riconcilia il registro dei requisiti; mantienili nel piano e nomina i loro passaggi di implementazione e accettazione. |
| Distribuzione, invio agli store o controlli sui dispositivi non sono disponibili | Indica esattamente account, strumento, dispositivo o accesso mancanti e continua la preparazione indipendente. Non dichiarare riuscito il controllo indisponibile. |
| Un agente afferma di aver avviato un'altra sessione | Chiedi un riferimento verificato di avvio/ricezione. Un file di passaggio di consegne dimostra soltanto lo stato realmente osservato. |
| Vuoi attività continue | Conferma scheduler, executor, credenziali, controlli di attività e percorso di recupero reali. L'installazione delle competenze da sola non li fornisce. |

## 13. Documentazione ufficiale e ambito delle prove

Le interfacce dell'ambiente e la disponibilità degli account possono cambiare. Consulta l'interfaccia reale e la documentazione ufficiale aggiornata quando installi o colleghi servizi. Riferimenti sul comportamento del prodotto verificati per questa guida il 7 novembre 2026:

- [Build skills — ChatGPT Learn](https://learn.chatgpt.com/docs/build-skills): struttura delle competenze riutilizzabili, rilevamento locale e concetti di installazione.
- [Plugins — ChatGPT Learn](https://learn.chatgpt.com/docs/plugins): directory dei plugin, connessioni e concetti di distribuzione.

Questo repository distribuisce una suite riutilizzabile e il suo flusso di installazione controllato. Un plugin per un marketplace pubblico, una licenza commerciale, un runtime ospitato permanente, strumenti a pagamento di terze parti e credenziali sono risultati separati, a meno che una release specifica non li fornisca e verifichi esplicitamente. I concetti di marketing illustrano flussi di lavoro e usi previsti; le affermazioni promozionali finali devono corrispondere a capacità e prove verificate.
