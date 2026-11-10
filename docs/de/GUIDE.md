# Agent System — der vollständige Leitfaden für Work + Codex

[English](../en/GUIDE.md) · [Українська](../uk/GUIDE.md) · [Deutsch](../de/GUIDE.md) · [Italiano](../it/GUIDE.md) · [Español](../es/GUIDE.md) · [Français](../fr/GUIDE.md) · [中文](../zh-CN/GUIDE.md)

**Grundlage dieses Leitfadens:** Agent System 6.0.0, 9. November 2026. **Wiederverwendbares Paket:** 33 Skills. Dieser Leitfaden behandelt eine neue Installation, die tägliche Arbeit, die gemeinsame Arbeit an einem Projekt in Work und Codex sowie die Aktualisierung eines bestehenden Projekts. Die Repository-Dokumentation und Paketrevisionen können sich ändern, ohne dass sich die zugrunde liegende Skill-Version ändert; lies vor einer Aktualisierung den Release-Eintrag.


**Aktuelles Release:** Suite 6.0.0, Repository 1.3.2, optional Atelier Orchestrator 1.1.0 und lokaler Agent Atelier 0.2.0. Lies vor der Aktualisierung [die genaue 6.0-Migration](../../releases/migrations/6.0.0.md). Die frühere 1.1.0-Kampagne bleibt unverändert: [englische Werbung](../../marketing/campaign/README.md) und [ukrainische Werbung](../../marketing/campaign/README.uk.md), zehn Materialien je Sprache. Werbung ist EN/UK; Leitfäden und Dienstoberfläche decken alle sieben angegebenen Sprachen ab. Live-Audit, Aktualisierung, Installation und Steuerung in Work bleiben eine separate Aufgabe im jeweiligen Host; ein Quellarchiv oder eine Repository-Verbindung ist kein Installationsbeleg.

**Überarbeiteter AI/data-Pass0.2, 10. November 2026:** repository1.3.2 bewahrt alle17 Fähigkeiten mit den bestehenden35 Quellen/12 Rollen und sieben bedingt aktivierten internen Profilen. Kontext, professionelles Design und eine funktionierende Oberfläche haben Vorrang. Jede bestätigte Regression verhindert die Übernahme; Vergleiche an realen Aufgaben sind geplant. Lesen Sie [das Handbuch](../evolution/2026-11-10/README.md). Nur Dokumentation: Ziel-Laufzeitänderungen und Vergleiche wurden nicht ausgeführt. Das ausführliche Handbuch ist EN/UK; Live-WORK bleibt zurückgestellt.

## 0. Auf 6.0 aktualisieren und den lokalen Arbeitsbereich öffnen

1. Wähle einen exakten verifizierten Release-Commit. Bewahre die aktuellen Quellen der 33 Skills, Icon-Dateien/-Bindungen/-Farben/-Klassen, lokale Änderungen und Besitznachweise. Sichere native Projektanforderungen, angenommene Identität/Persona, Entscheidungen, Berechtigungen, offene Aufgaben und ungeklärte Effekte. Eine Installation migriert kein Produkt.
2. Lies in `kit/` die Hilfe des portablen Updaters und prüfe dann den exakten Kandidaten. Kontrolliere vor apply alle 33 Einträge, Konflikte und die visuelle Erhaltung. Pläne und Backups gehören außerhalb der Skill-Erkennungsverzeichnisse.

```bash
python3 portable/update_skill_suite.py --help
python3 portable/update_skill_suite.py audit --kit . --plan /absolute/agent-system-plan.json
python3 portable/update_skill_suite.py apply --plan /absolute/agent-system-plan.json
python3 portable/update_skill_suite.py verify --kit . --journal /actual/apply/journal.json
```

3. Ersetze den Journal-Platzhalter ausschließlich durch den tatsächlich von apply zurückgegebenen Pfad. Unbekannte Abweichungen müssen geklärt werden; erzwinge kein Überschreiben. Prüfe tatsächliche Erkennung/Quellenladung und eine begrenzte Aufgabe getrennt. Bestehende Icons und andere Skills bleiben erhalten.
4. Prüfe das Codex-Hostprofil getrennt vom Repository-Stamm aus: `python3 scripts/install_host_profile.py audit --plan /absolute/host-plan.json`. Wende es mit `apply --plan /absolute/host-plan.json --journal /absolute/host-journal.json` an, danach mit `verify --journal /absolute/host-journal.json` prüfen. Der verwaltete Block erhält bestehende globale Anweisungen; die zwölf begrenzten Rollen behalten ihre Modelle und Beschränkungen externer Effekte. Das tatsächliche Laden im Host ist eine eigene Prüfung.
5. Installiere optional `atelier-orchestrator` mit dem unterstützten Skill-Manager aus `optional-skills/atelier-orchestrator` des gewählten Commits. Er gehört nicht zum33-Core-Updater; vorhandene Quellen belegen weder Installation noch erfolgreiche Ausführung. Der bestehende Wartungs-Skill bleibt ebenfalls separat optional.

Atelier Orchestrator 1.1.0 ist der optionale zentrale Einstieg: Beschreiben Sie das Ergebnis einmal, und er wählt direkte Ausführung, einen vorhandenen Spezialisten, einen Projektagenten, einen Direktor, Komponentenkoordination oder Foundry. Einfache Anfragen bleiben einfach. Ein gemeinsames Briefing und die bestehenden Berechtigungen begleiten die Arbeit. Sobald ein Projektagent erstellt, geprüft und vom Host erkannt wurde, empfiehlt der Orchestrator die Fortsetzung über diesen Agenten und behält diese Zuordnung bei späteren Anfragen bei. Agentenerstellung und ursprüngliche Produktaufgabe haben getrennte Abnahmekriterien; ein Agentenpaket schließt kein bestelltes Produkt ab.

Anfragen zur Verbesserung oder Überarbeitung des Orchestrators selbst, eines Skills, Konstruktors, einer Familie oder eines bestehenden Agenten nutzen den Wartungsweg: tatsächliche Quellen und Einstellungen lesen, Auswirkungen und Änderungen prüfen, Identität und lokale Anpassungen bewahren, eine vorherige Kopie sichern und das gespeicherte Ergebnis prüfen. Eine Wegvorschau und der optionale Routing-Prüfer zertifizieren weder fachliche Eignung noch menschliche Zustimmung, Ausführung oder Qualität. Bestehende direkte Skill-Aufrufe bleiben verfügbar.

Agent Atelier 0.2.0 ist die separate lokale Anwendung bzw. der Server und wird über den eigenen Starter geöffnet. Der Skill ist kein Hintergrunddienst, und die Anwendung ist kein Eintrag in der Skill-Liste. Ihre Versionen sind unabhängig. Original-SVG, PNG-Icon-Verknüpfungen und Markenfarbe bleiben erhalten. Lesen Sie [das Update auf 1.3 und den Rollback](../../releases/migrations/repository-1.3.0.md). Die Basissuite bleibt 6.0.0; weder Produktrücksetzung noch automatische Übernahme neuer Regeln sind impliziert. Live-Audit, Update und Steuerung von WORK bleiben bis zur Wiederherstellung des Zugriffs zurückgestellt.

6. Baue den lokalen Dienst aus den Quellen mit der festgeschriebenen Lockdatei und Node.js 24.22.2 oder einer unterstützten neueren Laufzeit. Führe in `apps/agent-atelier/` Folgendes aus. Für die erste Abhängigkeitsinstallation ist Netzwerkzugriff erforderlich; ein neuer kostenpflichtiger Dienst ist damit nicht verbunden.

```bash
npm ci --ignore-scripts
npm run build
node launcher/atelier.mjs start
node launcher/atelier.mjs status
node launcher/atelier.mjs doctor
node launcher/atelier.mjs stop
```

7. Auf dem Mac startet nach dem Build ein Doppelklick auf `apps/agent-atelier/launcher/Agent Atelier.command` den Dienst. Der Launcher öffnet Loopback, verwendet seine eigene laufende Instanz erneut und aktiviert keinen Anmeldungs-Autostart. Wähle einen konkreten Projektstamm, prüfe dessen Vorschau und verbinde ihn dann. Die Zuordnung ist schreibgeschützte Projekterkennung, keine Produktübernahme und keine Erlaubnis für alle künftigen Aufgaben. Der Demomodus enthält erfundene Daten und führt keine Befehle aus.

Suchen Sie im Arbeitsbereich nach verfügbaren Codex-Arbeiten und prüfen Sie die angezeigte Verlaufsabdeckung. Projekte und Arbeiten werden aus tatsächlichem nativem Verlauf und Quelleneinträgen gruppiert, einschließlich verfügbarer direkt in Codex begonnener Arbeiten. Das ist weder ein Scan des Home-Ordners noch eine Erlaubnis, einen anderen Schreiber zu übernehmen. Verbinden Sie den genauen Projektordner für Kontext und Fortsetzung. Die Arbeitskarte trennt erhaltene Antworten, in Quellen dokumentierte Ergebnisse und abgenommene Ergebnisse. Ziel und dokumentierte Abnahme behalten ihre Quelle; ein Vorschlag ist keine Zustimmung, eine Skill-Erwähnung keine Ausführung und ein geplanter Agent nicht installiert. Beschreiben Sie das nächste Ergebnis über den zentralen Einstieg, prüfen Sie den vorgeschlagenen Weg und bereiten Sie danach die begrenzte Aufgabe vor und starten Sie sie. Bestehende Chats erfordern eine unterstützte Übergabe im inaktiven Zustand; geschützte Änderungen des nativen Zustands erfolgen über den geprüften Controller statt durch beliebige Dateischreibzugriffe.

Die native Historie ist kein Desktop-Register leerer Projekte; verbinden Sie ein Projekt ohne verfügbaren Verlauf ausdrücklich. Wählen Sie für den bekannten optionalen Orchestrator- oder Repository-Wartungs-Skill im Katalog **Dieses Skill-Update prüfen**. Prüfen Sie genaue Quelländerungen, Erhaltung, Konflikte und den Plan für die vorherige Kopie; wenden Sie nur das bereite geprüfte Update an. Prüfen Sie das tatsächliche Journal und aktualisieren Sie die Host-Erkennung separat. Der Rollback stellt die genaue verwaltete vorherige Kopie wieder her und lehnt spätere unbekannte Änderungen ab. Diese optionalen Quelloperationen aktualisieren nicht die 33 Core-Skills und migrieren keine Produkte.

Vorhandene native Codex-Chats lassen sich im Portfolio über einen eigenen schreibgeschützten Zugriff auf den Verlauf einsehen. Der isolierte Ausführungsdienst kann einen inaktiven Chat nicht fortsetzen, wenn sich dessen gespeicherter Kontext dort nicht wiederherstellen lässt. Bereiten Sie dann aus geprüften Quellen eine neue, klar begrenzte Projektaufgabe vor oder setzen Sie den bestehenden Chat in einer nativen Codex-Umgebung fort, die seinen Kontext wiederherstellen kann. Zugriff auf Metadaten oder Verlauf eines Chats bedeutet noch nicht, dass ein nutzbarer Ausführungskontext vorliegt. Die Ausführungsisolation bleibt bestehen; native Datenbanken werden nicht migriert.

8. Bereite eine Aufgabe mit exaktem Umfang, Eingaben, Abnahme und Grenzen vor und starte sie über den unterstützten Codex-Adapter. Quelle, handwerkliche Qualität, Integration, Gerät, unabhängige Prüfung und Eigentümerabnahme haben unterschiedliche Zustände. Ein Abbruch ist erst nach dem tatsächlichen Host-Ergebnis bestätigt. Bestehende Chats benötigen genaue Identität/cwd und eine Übergabe im Ruhezustand; ein Dienst-Lease sperrt keinen anderen Desktop-Schreibprozess. Gleiche einen ungeklärten Effekt vor einem erneuten Versuch ab. Bei der Aufgabenvorbereitung erfasst der Dienst die exakten maßgeblichen AGENTS-Quellen, ihre Rangfolge oder ihr bestätigtes Fehlen sowie die Einstellungen, mit denen Codex selbst Anweisungen lädt. Er prüft, ob diese Aufzeichnungen mit den tatsächlich geladenen Anweisungsquellen übereinstimmen, und kontrolliert sie vor einem Modellaufruf erneut. Ändern sich diese Eingaben oder fehlen einem älteren Auftrag solche Aufzeichnungen, muss die Aufgabe erneut vorbereitet werden; ihr Verlauf und die nativen Produktdateien bleiben erhalten.
9. Bestehende Foundry-Sitzungen verwenden `suite-update-plan` und einen geprüften `refresh --accept-suite-update`-Datensatz mit exakten Quellzustands-/Ziel-Hashes. App state/1 benötigt keine toolkitbedingte Formatmigration. Integrierte Chat-Nachweise benötigen aktuelle Bindungen des Vertragsgegenstands und eine echte neue Beobachtung; alte Beweise werden nicht rückwirkend ergänzt. Game verwendet das unterstützte Workflow-Upgrade 5→6 und behält runtime2/model4/handoff1 bei. Erzeugte Agenten benötigen einen Quell-Ziel-Vergleich und eine Wiederaufnahme ohne verborgenen Chatkontext; kein Projekt wird zurückgesetzt.
10. Dienstsicherung und -wiederherstellung betreffen nur den Dienstzustand: Prüfe die exakte Sicherung vorab, gleiche Aufträge ab und erhalte widerrufene Berechtigungen; Produktdatenbanken oder externe Effekte werden nicht wiederhergestellt. Skill-Rollback verwendet das tatsächliche Updater-Journal; Hostprofil-Rollback verwendet sein eigenes Journal und weist spätere Abweichungen zurück. Live-Installation/-Steuerung in WORK bleibt zurückgestellt. Lies die [ausführliche Migration](../../releases/migrations/6.0.0.md) und die [Dienstanleitung](../../apps/agent-atelier/README.md) zu Wiederherstellung und unterstützten Grenzen.

## 1. Was du damit erhältst

Beschreibe ein Ergebnis in gewöhnlicher Sprache. Das System hilft, daraus eine konkrete Aufgabe zu machen, zieht die passenden Fachgebiete hinzu, hält Entscheidungen und Anforderungen zusammen und prüft das Ergebnis am vereinbarten Ziel.

Zum Beispiel kann „Hilf mir, die Datenbanklast in diesem Backend zu reduzieren“ zu einer gezielten Untersuchung von Abfragen, Transaktionsgrenzen, Caching, Leistungsmessungen und einer getesteten Änderung werden. „Erstelle eine mobile Anwendung für diese Zielgruppe“ braucht einen umfassenderen Ablauf: Recherche, Produktentscheidungen, Design, Architektur, Implementierung, Qualitätsprüfungen, Release-Vorbereitung und Betrieb. Eine kleine Reparatur soll eine kleine Reparatur bleiben. Bei einem vollständigen Produkt müssen sämtliche Anforderungen erhalten bleiben, auch die Teile, die erst nach der ersten funktionsfähigen Version geplant sind.

Ein **Skill** ist ein wiederverwendbarer Satz aus Arbeitsanweisungen, Referenzen und manchmal Skripten. Ein **Agent** wendet eine Rolle und diese Anweisungen auf eine Aufgabe an. Ein **Direktor** koordiniert eine Produktfamilie. Ein **Konstruktor** entwirft einen spezialisierten Agenten oder einen wiederverwendbaren Satz von Skills, wenn die vorhandenen Familien die Aufgabe nicht abdecken. Sie arbeiten über ChatGPT oder Codex und die Werkzeuge, die in dieser Umgebung tatsächlich verfügbar sind. Das Installieren von Anweisungen erstellt keinen laufenden Server, kauft keine Dienste, erteilt keine Repository-Berechtigungen und startet keinen dauerhaften Hintergrundprozess.

Der Nutzen liegt im geordneten Arbeitsablauf: ein gemeinsames Briefing, ausdrückliche Anforderungen, passende Fachleute, erhaltene Entscheidungen, überprüfbare Übergaben und eine Möglichkeit, die Arbeit fortzusetzen. Das Repository behauptet weder eine gemessene Überlegenheit noch garantierte Einnahmen, eine garantierte Store-Zulassung oder automatische Produktionsreife.

## 2. Wähle deinen Einstieg

| Deine Situation | Beginne mit | Eine hilfreiche erste Anfrage |
| --- | --- | --- |
| Sie möchten einen Einstieg für eine Aufgabe, ein Projekt oder eine Systemverbesserung | `atelier-orchestrator` | „Hier ist das benötigte Ergebnis. Stelle den Projektkontext wieder her, wähle passende verfügbare Kompetenzen und erledige die vereinbarte Arbeit.“ |
| Du möchtest einen spezialisierten Agenten für eine wiederkehrende Aufgabe | `agent-foundry` | „Erstelle einen Agenten, der Leistungsprobleme in unseren Go-Diensten untersucht. Kläre zuerst seine Zuständigkeiten, Nachweise und Zugriffe.“ |
| Du möchtest einen wiederverwendbaren Skill oder eine koordinierte Skill-Familie | `design-specialist-skills` | „Entwirf einen wiederverwendbaren Prüfablauf für unsere ereignisgesteuerten Integrationen, einschließlich der Wiederherstellung nach Fehlern.“ |
| Du möchtest eine Anwendung oder ein bestehendes Produkt weiterentwickeln | `app-atelier-director` | „Setze diese Anwendung von ihrem Checkpoint aus fort. Erhalte die akzeptierten Anforderungen und bestimme das nächste nützliche Arbeitsergebnis.“ |
| Du möchtest einen Chatbot, Support-Bot oder Gesprächsbegleiter | `chatbot-atelier-director` | „Entwirf einen Bot für diese Zielgruppe und diese Kanäle, einschließlich Sprache, Gedächtnis, Aktionen und Betriebskosten.“ |
| Du möchtest ein mobiles Spiel oder ein bestehendes Spiel fortsetzen | `gamedev-director` | „Entwickle Spielkonzepte für dieses Erlebnis mit sinnvoller Steuerung, Fortschritt und einem umsetzbaren Produktionsweg.“ |
| Du kennst die genaue Phase bereits | Dem passenden Spezialisten unten | „Prüfe diesen Zahlungsbildschirm anhand des freigegebenen Designs und der Abnahmekriterien.“ |

Du musst dir nicht alle 33 Namen merken. Verwende für ein Produkt einen Direktor oder für einen neuen spezialisierten Arbeitsablauf einen Konstruktor. Du kannst einen Skill auch ausdrücklich über die Skill-Auswahl des Hosts anfordern. In Work ist die übliche Form `@skill-name`, in Codex `$skill-name`. Verfügbare Auswahlelemente und Anzeigenamen können sich je nach Host-Version unterscheiden. Bitte den Host, die tatsächlich geladene Quelle anzuzeigen, wenn du Gewissheit brauchst.

### Der vollständige Katalog

#### Zwei Konstruktoren

| Skill | Wobei er dich unterstützt |
| --- | --- |
| `agent-foundry` | Ein spezialisierter Agent oder eine koordinierte Agentenfamilie, zugeschnitten auf ein reales Fachgebiet, Zuständigkeiten, Werkzeuge, Wissen, Prüfungen und einen praktikablen Betriebsweg. Seine erste Aufgabe ist der Entwurf des Agenten, statt unbemerkt dessen späteres Projekt auszuführen. |
| `design-specialist-skills` | Wiederverwendbare Skills und Skill-Familien für eine festgelegte Aufgabe: passende Fachgebiete, Qualitätskriterien, Referenzen, Werkzeuge und Arbeitsreihenfolge. |

#### Anwendungsteam — 11 Skills

| Skill | Seine Aufgabe in verständlichen Worten |
| --- | --- |
| `app-atelier-director` | Hält das Anwendungsprojekt von der ersten Idee über die Entwicklung bis zum Betrieb zusammen. |
| `app-atelier-research` | Untersucht Nutzer, Bedürfnisse, Alternativen und Marktbelege, bevor das Team in eine Produktrichtung investiert. |
| `app-atelier-concepts` | Vergleicht vollständige Produktoptionen: Nutzen, Erlebnis, Geschäftsmodell, Kosten und realistischen Umfang. |
| `app-atelier-specification` | Übersetzt das gewählte Produkt in präzise Anforderungen sowie Verträge für Verhalten, Daten, API, Authentifizierung und Zahlungen. |
| `app-atelier-experience` | Erstellt und prüft Marke, Bildschirme, Zustände, Einführung, Barrierefreiheit, Lokalisierung und Designunterlagen für die Produktion. |
| `app-atelier-build` | Implementiert die vereinbarten Android-, iOS- und Web-Clients sowie bei Bedarf Backend und Integrationen mit reproduzierbaren Builds. |
| `app-atelier-support` | Entwirft und implementiert den Support-Bot und den Wissensablauf des Produkts, einschließlich Eskalation und kontrollierter Aktionen. |
| `app-atelier-qa` | Prüft unabhängig Anforderungen, Design, Implementierung, Zahlungen, Datenschutz, Wiederherstellung und Release-Reife, sofern ein unabhängiger Akteur verfügbar ist. |
| `app-atelier-release` | Prüft frühzeitig die Umsetzbarkeit der Veröffentlichung und bereitet anschließend Signierung, Store-Einträge, Deployments, Belege und Rückabwicklung innerhalb des erlaubten Umfangs vor. |
| `app-atelier-growth` | Bewertet passende Kanäle zur Nutzergewinnung, Inhalte und Messungen, bereitet sie vor und aktiviert einen autorisierten Weg, sobald das Produkt bereit ist. |
| `app-atelier-operations` | Bearbeitet Vorfälle, Produktkennzahlen, Supportfälle, Kosten, Sicherungen, Änderungen und den fortlaufenden Betrieb. |

#### Chatbot-Team — 11 Skills

| Skill | Seine Aufgabe in verständlichen Worten |
| --- | --- |
| `chatbot-atelier-director` | Koordiniert den gesamten Lebenszyklus eines Bots und erhält dessen vorhandene Fähigkeiten, wenn die Arbeit fortgesetzt wird. |
| `chatbot-atelier-research` | Untersucht Zielgruppe, Fachgebiet, Plattformgrenzen, Integrationen und praktische Umsetzbarkeit. |
| `chatbot-atelier-specification` | Definiert Regeln, Zustand, Daten, Werkzeuge, Ereignisse, Fehler, Datenschutz und Abnahmekriterien des Bots. |
| `chatbot-atelier-conversation` | Entwickelt Sprache, Charakter, hilfreiche Fragen, Eigeninitiative, Schaltflächen und Verhalten in Einzel- oder Gruppengesprächen. |
| `chatbot-atelier-knowledge` | Entwirft Wissensquellen und ein klar abgegrenztes Gedächtnis, bei Bedarf Informationsabruf, Korrekturen, Ablauf, Löschung und Datenschutz. |
| `chatbot-atelier-integrations` | Baut Plattformadapter, Callbacks, Werkzeuge, geplante Aufgaben und zuverlässige externe Aktionen mit Wiederherstellung und Zustellnachweisen. |
| `chatbot-atelier-media` | Erstellt und integriert die visuelle Identität, Bilder, Animationen, Audio und Stimme des Bots über verfügbare Werkzeuge. |
| `chatbot-atelier-build` | Implementiert den vollständigen vereinbarten Bot, einschließlich der notwendigen Laufzeitumgebung und Integration in den Produktivbetrieb. |
| `chatbot-atelier-qa` | Prüft Gesprächsverhalten, Wissen, Datenschutz, Aktionen, Medien, Laufzeit und Negativszenarien anhand tatsächlicher Nachweise. |
| `chatbot-atelier-release` | Bereitet eine autorisierte Veröffentlichung vor und führt sie aus, mit genauer Quellen-/Build-Identifikation, Zustellprüfungen, Datenkompatibilität und Rückabwicklung. |
| `chatbot-atelier-operations` | Pflegt Zuverlässigkeit, Gesprächsqualität, Support, Kosten, Migrationen und laufende Weiterentwicklung. |

#### Spieleteam — neun Skills

| Skill | Seine Aufgabe in verständlichen Worten |
| --- | --- |
| `gamedev-director` | Koordiniert das Spielprojekt und erhält dabei die akzeptierte kreative Richtung, Entscheidungen und Checkpoints. |
| `gamedev-studio` | Erstellt oder stellt die Studioidentität, akzeptierte Markenoriginale, Entwickleridentität und Kontobereitschaft wieder her. |
| `gamedev-concepts` | Erstellt unterschiedliche Spielkonzepte mit Steuerung, zusammenwirkenden Systemen, Fortschritt, visueller Gestaltung und einem umsetzbaren Produktionsweg. |
| `gamedev-preproduction` | Erweitert das gewählte Konzept zu detailliertem Spiel- und Technikdesign, Zahlenregeln, Katalogen, Zuständen und einem Produktionsplan. |
| `gamedev-assets` | Erstellt und integriert Grafik, Animation, UI, Ton und Haptik und erhält dabei akzeptierte Quellen und die Beziehung zu Laufzeit-Assets. |
| `gamedev-build` | Implementiert das native mobile Spiel: Steuerung, Kamera, Spielmechanik, Gegner, Welt, Fortschritt, Wirtschaft, Spielstände und Plattform-Builds. |
| `gamedev-qa` | Prüft tatsächliches Gameplay, Geräteverhalten, Steuerung, Spielstände, Leistung und Anforderungen und unterscheidet reale Laufzeitnachweise von Dokumentenprüfungen. |
| `gamedev-release` | Bereitet Signierung, genaue Binärdateien, Store-Materialien, Käufe, Datenschutz, Einführung und Wiederherstellung für eine autorisierte Veröffentlichung vor. |
| `gamedev-liveops` | Entwickelt und pflegt das veröffentlichte Spiel anhand beobachteter Telemetrie, Vorfälle, Fortschritte, Inhalte, Wirtschaft und kompatibler Änderungen. |

Das sind Zuständigkeiten und kein Versprechen, dass 33 Agenten gleichzeitig laufen. Das System soll Team und Aufwand entsprechend der Aufgabe auswählen. Eine unabhängige Prüfung ist nur dann unabhängig, wenn ein anderer Akteur sie tatsächlich ausführt; die Eigenprüfung eines Autors muss entsprechend gekennzeichnet werden.

## 3. Wähle deine Sprache vor der Installation

Öffne den übersetzten Leitfaden über die Links oben. Ohne ausdrückliche Präferenz gilt Englisch als Standard. Die übersetzten Leitfäden behandeln dieselben Schritte; Code, stabile Skill-Namen, Dateinamen und Protokollkennungen bleiben unverändert, damit Befehle einheitlich funktionieren.

Füge zu Beginn der Installation oder des Projekts diesen Text ein und passe die Sprache an:

```text
Meine Arbeitssprache ist Deutsch (de). Verwende sie für Erklärungen, Fragen,
Statusmeldungen, Übergabeanweisungen und Berichte für mich. Lasse stabile
Skill-Namen, Befehlssyntax und technische Kennungen unverändert. Halte
diese Präferenz im gespeicherten Projektkontext und in Übergaben fest. Frage gesondert
nach der Sprache des Produkts, das wir entwickeln.
```

Dokumentationssprache, Gesprächssprache und Produktsprache sind getrennte Entscheidungen. Du kannst beispielsweise den ukrainischen Leitfaden lesen, auf Ukrainisch mit dem Agenten arbeiten und eine Anwendung auf Englisch und Deutsch veröffentlichen. Gib bei Bedarf alle drei an. Halte die Präferenz in der Vorlage für den Projektkontext oder einer bestehenden gleichwertigen Datei fest und übernimm sie in jede Übergabe. Das Ändern der Seitensprache im Browser allein legt die Sprache eines anderen Chats nicht fest.

## 4. Bereite Konten und Quellen vor

1. Melde dich bei dem ChatGPT- oder Codex-Konto an, in dem du das Paket verwenden möchtest. Prüfe, ob der erforderliche Modus und die Werkzeuge zur Skill-Verwaltung in diesem Konto oder Arbeitsbereich tatsächlich verfügbar sind.
2. Öffne `https://github.com/alex-hohaizel/codex-agents`. Der Eigentümer bestimmt derzeit die Sichtbarkeit des Repositorys. Ein privates Repository erfordert ein berechtigtes GitHub-Konto und eine Verbindung mit Zugriff auf genau dieses Repository.
3. Verbinde oder wähle GitHub in Work über die verfügbare Plugins-/Verbindungsoberfläche. Wenn der Zugriff auf ausgewählte Repositorys beschränkt ist, nimm `alex-hohaizel/codex-agents` auf. Bitte Work, `README.md` zu lesen und den tatsächlich zugänglichen Branch und die Revision anzugeben.
4. Autorisiere im lokalen Codex den lokalen Git-Zugriff, wenn du ein privates Repository klonen möchtest. Eine GitHub-Verbindung in Work belegt nicht, dass sich Terminal auf deinem Computer authentifizieren kann.
5. Verwende für die Installation ein benanntes Release oder einen genauen Commit. Speichere diese Kennung. Das Lesen eines nicht festgeschriebenen Branches `main`, während er sich ändert, kann Versionen vermischen.
6. Lade die gewählte Repository-Revision über **Code → Download ZIP** in GitHub herunter oder klone sie mit Git. Entpacke ein heruntergeladenes Archiv vor der Installation. Du solltest `kit/manifest.json`, `kit/portable/` und `kit/skills/` sehen.
7. Lege Download, Pläne und Sicherungen nicht in einem Verzeichnis ab, das für die Skill-Erkennung verwendet wird. Ein normaler Ordner wie Downloads oder ein eigener Arbeitsbereich zur Skill-Verwaltung ist geeignet.

Verwende für lokales Git einen bestätigten Branch und ein neues Ziel, das keine anderen Arbeiten enthält:

```bash
git clone --branch main https://github.com/alex-hohaizel/codex-agents.git "codex-agents"
cd "codex-agents"
git rev-parse HEAD
git status --short
```

Ein Klon von `main` ist ein praktischer Quellen-Checkout. Bestätige vor dem Anwenden einer Aktualisierung, dass dessen SHA zum gewählten Release passt. Füge Zugriffstoken weder in Chats, Projektdateien, Shell-Befehle noch in Übergabedokumente ein. Verwende die Kontoverbindung oder den Anmeldeablauf der Plattform.

## 5. Installation in Work mit einem neuen Konto

### Was dieser Weg bewirkt

Er speichert die 33 wiederverwendbaren Skills über den unterstützten Verwaltungsprozess des Hosts als persönliche Skills. Allein das Verbinden von GitHub, Hochladen einer ZIP-Datei, Lesen dieses Leitfadens oder Hinzufügen von Repository-Dateien als Projektquellen belegt nicht, dass ein Skill installiert oder geladen wurde.

### Schritt für Schritt

1. Öffne Work und erstelle oder öffne ein Projekt zur Skill-Verwaltung. Hier verwaltest du den Werkzeugsatz, nicht das Produkt, das du später entwickeln wirst.
2. Wähle deine Sprache mit dem Block aus Abschnitt 3.
3. Stelle Zugriff auf die gewählte Repository-Revision bereit. Falls Work private GitHub-Dateien nicht lesen kann, verbinde dieses Repository oder füge das zusammengestellte Paket über die verfügbare Dateischnittstelle hinzu.
4. Rufe die verfügbare Funktion Skill Creator/Skill-Verwaltung auf. Bitte sie, das Paket zu prüfen, bevor installierte Einträge verändert werden.
5. Füge den Installationsblock unten ein. Er autorisiert die begrenzte Installation und die erforderliche Überprüfung.
6. Lasse Work das vorhandene Skill-Inventar nach stabilen Namen prüfen. Bei einem neuen Konto soll es fehlende Einträge erstellen; bei einem vorhandenen Konto die passenden persönlichen Einträge aktualisieren und andere Skills erhalten.
7. Bewahre den Installationsbericht auf. Er muss jeden der 33 Skills, seine Version, Quellenrevision, das Ergebnis und ungelöste Fehler nennen.
8. Aktualisiere oder öffne die Skills-Seite erneut, wenn ihre Anzeige veraltet ist. Öffne einen neuen Chat im vorgesehenen Produktprojekt und führe die unten beschriebene Lade- und Praxisprüfung aus.

```text
Installiere die 33 wiederverwendbaren persönlichen Skills aus der gewählten, überprüften Revision
von alex-hohaizel/codex-agents anhand von kit/manifest.json und kit/skills/.
Meine Arbeitssprache ist Deutsch (de).

Verwende den vom Host unterstützten Verwaltungsprozess für persönliche Skills. Prüfe vorhandene
Einträge anhand stabiler Namen, überprüfe das Paket, erhalte andere Skills und die
vorhandene visuelle Identität und installiere oder aktualisiere die passenden Einträge. Bewahre
Sicherungen und die genaue Quellenherkunft auf. Installiere projektspezifische Agenten nicht
global. Verändere keine Produktdaten, Produktivdienste oder Kontoeinstellungen.

Melde jeden stabilen Namen, Version, Quellenrevision und den Status create/update/noop/failure.
Unterscheide einen gespeicherten Skill von der Erkennung durch den Host und der tatsächlichen Aufgabennutzung.
Falls die Skill-Verwaltung nicht verfügbar ist, erkläre die genau fehlende Fähigkeit;
bezeichne eine hochgeladene oder schreibgeschützte Kopie nicht als installiert.
```

Der unterstützte Verwaltungsprozess von Work kann Skills einzeln speichern. Bei einem Teilergebnis sollen abgeschlossene und verbleibende Einträge benannt werden, damit eine sichere Fortsetzung möglich ist, statt neu zu beginnen. Ein portabler Codex-Updater, der in einem Cloud-Dateisystem ausgeführt wurde, beweist keine Aktualisierung deines persönlichen Skill-Verzeichnisses in Work.

## 6. Installation oder Aktualisierung in Codex

### Der einfachste Weg: Bitte Codex um die kontrollierte Installation

1. Lade oder klone die gewählte Revision wie oben beschrieben.
2. Öffne Codex in deinem vorhandenen Arbeitsbereich zur Skill-Verwaltung. Bei der ersten Installation öffne den Checkout oder einen anderen normalen Verwaltungsordner; ein neues Produkt-Repository ist unnötig.
3. Gib Codex den genauen Checkout-Pfad. Wähle auf einem Mac den Ordner im Finder und drücke **Option + Command + C**, um den vollständigen Pfad zu kopieren.
4. Füge den folgenden Block ein, nachdem du deine bevorzugte Sprache festgelegt hast.
5. Prüfe den abschließenden Installationsbericht und bewahre sein Journal sowie den Sicherungsort auf.
6. Öffne für Lade- und Praxisprüfungen einen neuen Chat im tatsächlichen Produktprojekt.

```text
Installiere die 33 persönlichen Basis-Skills aus dem überprüften Verzeichnis kit/ in
diesem Checkout von alex-hohaizel/codex-agents. Verwende die gewählte Release-Revision.
Meine Arbeitssprache ist Deutsch (de).

Dies autorisiert lokales audit → apply → verify, genaue Pläne und Sicherungen für dieses
Paket. Lies kit/manifest.json und --help des Updaters. Prüfe die Paketintegrität.
Prüfe persönliche Verzeichnisse und alle bekannten Projektkopien. Speichere Pläne und
Sicherungen außerhalb der Verzeichnisse zur Skill-Erkennung. Wende nur den genauen fertigen Plan an. Erhalte
unbekannte lokale Änderungen und melde Konfliktdateien; umgehe keine Drift-Prüfungen.

Erhalte bestehende icon_small, icon_large, brand_color, Icon-Pfade und Icon-Bytes,
einschließlich historischer Verweise auf ./assets/. Prüfe mit dem genauen Journal,
das apply zurückgibt. Melde canonical_core_verified, visual_preservation_verified,
Anzahlen für updated/noop, Blockaden, Fehler und Duplikate.

Verändere keine Produkte, Produktivsysteme, Plugins oder Umgebungskonfiguration.
Prüfe anschließend gesondert die Erkennung beider Konstruktoren und der App-, ChatBot-
und Game-Direktoren durch den Host. Installierte Dateien sind kein Beleg für tatsächliche Aufgabennutzung.
```

### Terminal-Weg für alle, die die genauen Befehle möchten

Der portable Updater benötigt Python 3.9 oder neuer und verwendet die Standardbibliothek. Führe diese Befehle im Repository-Stamm aus. Das Audit liest Paket und Installationsorte und schreibt einen vorgeschlagenen Plan. Apply führt die geplanten Installationsänderungen aus und erstellt ein Journal.

```bash
python3 kit/portable/update_skill_suite.py --help
python3 kit/portable/update_skill_suite.py audit --kit kit --plan ../agent-system-plan.json
python3 kit/portable/update_skill_suite.py apply --plan ../agent-system-plan.json
```

Lies das Ergebnis von `apply`. Kopiere dessen genauen `journal`-Pfad in den Prüfbefehl:

```bash
python3 kit/portable/update_skill_suite.py verify --kit kit --journal /absolute/path/from-apply/journal.json
```

Der letzte Pfad oben ist ein Platzhalter. Ersetze ihn; führe ihn nicht wörtlich aus. Standardmäßig installiert der Updater nach `~/.agents/skills` und prüft das ältere Stammverzeichnis `~/.codex/skills`. Verwendet deine Umgebung ein anderes unterstütztes persönliches Stammverzeichnis, gib `--destination` und `--legacy-root` ausdrücklich und einheitlich an. Lies zuerst `audit --help`. Ergänze `--project-root /absolute/path/to/product`, um relevante lokale Produktkopien zu prüfen. Der Updater entfernt nicht automatisch eine Projektkopie, die einen persönlichen Skill überlagert.

Eine erfolgreiche Dateiinstallation bedeutet: 33 Quellen in der vorgesehenen Version überprüft, keine ungelösten Blockaden/Fehler/Duplikate sowie `canonical_core_verified=true` und `visual_preservation_verified=true` aus einer Prüfung mit dem tatsächlichen Apply-Journal. Eine Hash-Prüfung ohne dieses Journal kann den Erhalt deiner vorhandenen Icons nicht belegen. Halte bei einem Konflikt an und sichere die lokale Arbeit; verwende kein erzwungenes Ersetzen, nur damit der Bericht sauber aussieht.

### Prüfe das Laden getrennt von der Installation

Frage Codex oder Work in einem neuen Produktchat:

```text
Ermittle vor jeder Änderung die genau geladene Quelle und Version von
agent-foundry, design-specialist-skills und den drei Produktdirektoren.
Bestätige, welche Anweisungen zu adaptiver Arbeit, Recherche, visueller Identität und Work↔Codex
du tatsächlich gelesen hast. Melde nicht verfügbare Quellen gesondert.
```

Gib danach eine kleine reale Aufgabe mit bekanntem Eingang und Abnahmekriterium. Bitte beispielsweise den Anwendungsdirektor, die Fehlerzustände eines einzelnen Bildschirms anhand einer bestehenden Anforderung zu prüfen, oder einen Konstruktor, die Zuständigkeiten eines spezialisierten Agenten zu umreißen. Dies prüft das Verhalten. Es zertifiziert nicht jede Produktfähigkeit. Halte Dateiinstallation, Laden durch den Host, praktische Nutzung und Produktabnahme als getrennte Ergebnisse fest.

## 7. Nutze das System für eine reale Aufgabe

### Eine eng begrenzte technische Aufgabe

```text
Untersuche wiederholte Datenbankabfragen in diesem Endpunkt. Erhalte seine API und
sein Geschäftsverhalten. Lies zuerst Code und bestehende Messungen. Ermittle,
welche Nachweise fehlen, schlage die kleinste nützliche Untersuchung vor und
implementiere eine begründete Reparatur in diesem Branch. Prüfe die Korrektheit und zeige
Vorher-/Nachher-Messungen, soweit die Umgebung sie ermöglicht.
```

Dafür braucht es kein neues Unternehmen, Produkt, keine Marke und keine vollständige Marktstudie. Ein Konstruktor kann einen wiederverwendbaren Untersuchungsagenten entwerfen, wenn du diesen Ablauf als dauerhaften Agenten möchtest; für eine einmalige Aufgabe verwende die vorhandenen passenden Werkzeuge und Anweisungen. Das System soll nicht allein deshalb einen neuen Agenten erzeugen, weil eine Aufgabe technisch ist.

### Eine vollständige Anwendung

```text
BRIEF: Ich möchte eine Anwendung für [Zielgruppe], die [Problem] löst. Die Ziel-
plattformen sind [Plattformen], das Budget ist [Budget] und meine Rolle ist [Rolle]. Kläre
Unbekanntes, untersuche reale Alternativen und bereite vollständige Optionen vor. Halte
alle meine Anforderungen, einschließlich Design, Sprache, Support und Monetarisierung,
im gesamten Plan sichtbar. Wähle kein Konzept stillschweigend für mich aus.
```

Das Team soll Relevantes untersuchen, Optionen vergleichen und Veröffentlichungs- oder Kontohindernisse vor einer großen Implementierung erkennen. Nach der Konzeptwahl müssen gewählte Designreferenzen und sämtliche vereinbarten Anforderungen erhalten bleiben. Eine frühe funktionsfähige Version ist ein Checkpoint in diesem Plan und keine Erlaubnis, den Rest zu verwerfen.

### Ein mobiles Spiel

```text
BRIEF: Entwickle unterschiedliche mobile Spielkonzepte für [Zielgruppe/Erlebnis]. Behandle
Steuerung und Rückmeldung, zusammenwirkende Systeme, Gegner, sinnvollen Fortschritt,
visuelle Gestaltung, Monetarisierung und einen umsetzbaren Produktionsweg für Android/iOS.
Zeige vergleichbare visuelle Konzepte. Erhalte die ausgewählte Identität in
Assets und der spielbaren Implementierung. Definiere tatsächliche Geräteprüfungen.
```

Ein Konzeptbild kann weder Animation, Touch-Steuerung, Leistung noch die Wiederherstellung von Spielständen belegen. Der Spielablauf soll das gewählte visuelle Versprechen mit bearbeitbaren Quell-Assets und einem repräsentativen spielbaren Ausschnitt verbinden, bevor der vollständige Asset-Satz entsteht.

## 8. Work und Codex im selben Projekt

Work ist dort hilfreich, wo die erforderlichen Quellen, Recherchewerkzeuge, Designwerkzeuge und verbundenen Dienste verfügbar sind. Codex ist dort hilfreich, wo Quellen-Checkout, Laufzeitumgebung, Build-Werkzeuge sowie Geräte- oder lokale Integrationen vorhanden sind. Jeder Modus kann mit den passenden Fähigkeiten mehr übernehmen. Wähle anhand tatsächlicher Zugriffe und Nachweise, statt jede Denkaufgabe einem Modus und jede Codeaufgabe dem anderen zuzuweisen.

Lege eine gemeinsame Produktidentität an. Namen wie `My Product [WORK]` und `My Product [CODEX]` erleichtern die Navigation, beweisen aber nicht, dass beide Projekte dasselbe Produkt enthalten. Halte Repository, Branch, Unterverzeichnis, Projektkennungen und Checkpoint-Quellen fest. Ein neuer Chat soll innerhalb dieses bestehenden Projekts bleiben.

### Halte einen kleinen gemeinsamen Kontext fest

Verwende die Projektkontext-Vorlage des Repositorys oder eine bestehende gleichwertige Datei in deinem Produkt. Erfasse mindestens: Projektkennung; Repository und Branch; aktuellen vollständigen Commit-SHA; Aufgabenkennung; aktuelle Phase; Arbeits- und Produktsprachen; Toolkit-Version und Installationsbeleg; akzeptierte Entscheidungen; vollständige Anforderungsquelle; Designreferenzquelle; gewährten Umfang; aktuellen Checkpoint; ungeklärte Wirkungen oder Entscheidungen und nächste Aktion. Zugangsdaten gehören nicht in diesen Datensatz.

### Work → lokales Codex, Schritt für Schritt

1. Bitte Work: „Setze diese Phase in Codex fort. Bereite die Übergabe für dieses bestehende Projekt vor.“
2. Work soll das genaue nächste Arbeitsergebnis und die für dessen Abnahme erforderlichen Nachweise bestimmen. Es soll die relevanten Anforderungen, Entscheidungen, Quellen und den Checkpoint speichern oder bereitstellen.
3. Ist ein autorisierter gemeinsamer Kanal verfügbar, kann Work die Übergabe speichern und die gespeicherte Revision überprüfen. Das Speichern einer Datei belegt nicht den Start einer anderen Codex-Sitzung.
4. Öffne den bestehenden lokalen Checkout. Gibt es keine lokale Kopie, klone das bestätigte Repository und den Branch in den gewählten Ordner. Authentifiziere dich für private Repositorys lokal.
5. Prüfe den Checkout vor seiner Aktualisierung:

```bash
git remote get-url origin
git branch --show-current
git rev-parse HEAD
git status --short
```

6. Ist der Arbeitsbaum sauber und eine Aktualisierung dieses Branches erforderlich, verwende `git pull --ff-only origin <confirmed-branch>` mit dem tatsächlichen Branchnamen. Bestätige den resultierenden vollständigen SHA. Gibt es lokale Änderungen oder auseinanderlaufende Historien, erhalte sie und kläre die Abweichung vor abhängigen Arbeiten.
7. Öffne den genauen Ordner in der Projektoberfläche von Codex. Verwende bei einem bestehenden Produkt dessen vorhandenes Projekt; füge den Ordner bei Bedarf über die verfügbare Projektbearbeitung hinzu.
8. Füge den ausgefüllten Übergabeblock unten ein. Codex bestätigt zuerst Repository-Identität, Revision, lokale Änderungen, Berechtigungen und Checkpoint und arbeitet dann an der begrenzten Aktion.
9. Bewahre Ergebnisbericht, Commit-/Build-Verweise und Testnachweise für die Rückübergabe auf.

### Codex → Work, Schritt für Schritt

1. Bitte Codex um eine Ergebnisübergabe oder eine neue Aufgabenübergabe für dasselbe bestehende Projekt.
2. Nimm die tatsächlich geänderten Dateien, vollständigen SHA oder die Artefaktrevision, ausgeführte Prüfungen, Einschränkungen, offene Entscheidungen und nächste Aktion auf. Gib an, ob die Änderungen lokal, committed oder veröffentlicht sind.
3. Ist das Veröffentlichen der vereinbarten Änderungen auf einem benannten Branch autorisiert, veröffentliche nur diesen Umfang und überprüfe die entfernte Revision. Andernfalls stelle ein kontrolliertes Artefakt über den verfügbaren Kanal bereit. Ein lokaler Mac-Pfad ist nicht automatisch von Work aus lesbar.
4. Öffne das bestehende Work-Projekt, verbinde das relevante Repository oder füge das genaue Artefakt hinzu und füge die Übergabe ein.
5. Work liest die tatsächlichen Quellen und prüft die Eingangsrevision, bevor es überprüft oder fortsetzt. Nicht zugängliche Dateien soll es ausdrücklich nennen.
6. Halte die Abnahme getrennt von Lieferung und Ausführung fest. Der Bericht, dass ein Build existiert, ist nicht dasselbe wie die Produktabnahme.

### Kopierbare Übergabe

Ersetze vor Verwendung dieses Blocks jedes Feld in eckigen Klammern:

```text
Setze das bestehende Projekt [Projekt-ID/Name] in [Work/Codex] fort.
Arbeitssprache: [Sprache/Code]. Produktsprachen: [Sprachen].
Repository: [URL]. Branch/Unterverzeichnis: [Branch/Pfad].
Eingangsrevision: [vollständiger SHA oder genaue Artefaktrevision].
Aufgaben-ID und Phase: [ID/Phase].
Checkpoint: [genaue zugängliche Quelle].
Anforderungen und akzeptierte Entscheidungen: [genaue Quellen].
Designreferenzen und Identität: [genaue Quellen, falls relevant].
Erwartetes Arbeitsergebnis und Abnahme: [konkretes Ergebnis/Prüfungen].
Autorisierter Umfang: [was geändert oder veröffentlicht werden darf].
Abgeschlossene Arbeit und Nachweise: [Fakten und Verweise].
Offene Entscheidungen, Blockaden oder unklare externe Wirkungen: [Einzelheiten/keine].
Nächste Aktion: [eine konkrete Aktion].

Prüfe zuerst Projektidentität, Revision, verfügbare Werkzeuge und Berechtigungen.
Erhalte jede akzeptierte Anforderung und Entscheidung. Initialisiere das
Produkt nicht neu. Unterscheide vorbereitete Übergabe, überprüfte Zustellung, Empfang, Ausführung,
Ergebnis und Abnahme. Setze die autorisierte Arbeit fort, die tatsächlich möglich ist.
```

## 9. Fortsetzen nach einem unterbrochenen Chat

Öffne einen neuen Chat im selben Projekt und bitte ihn, den letzten überprüften Checkpoint wiederherzustellen. Stelle die Checkpoint-Quelle bereit, falls sie noch nicht zugänglich ist. Vor der Fortsetzung soll er Aufgabe, Anforderungen, Quellenrevision, aktuelle Dateien und tatsächliche externe Ergebnisse abgleichen.

```text
Stelle diese bestehende Aufgabe aus dem letzten überprüften Checkpoint und den tatsächlichen Quellen wieder her.
Erhalte Anforderungen, Entscheidungen, Berechtigungen, abgeschlossene Ergebnisse und unklare
externe Wirkungen. Prüfe die aktuelle Revision und die Zuständigkeit für die nächste Aktion.
Bevor du ein Deployment, eine Zahlung, Nachricht oder andere externe Aktion wiederholst,
prüfe, ob der vorherige Versuch tatsächlich abgeschlossen wurde. Setze die verfügbare
autorisierte Arbeit fort und halte einen neuen Checkpoint fest.
```

Ein festgefahrenes Gespräch ist kein Nachweis dafür, dass dessen letzter Vorgang fehlgeschlagen ist. Bei der Wiederherstellung muss das reale Ergebnis geprüft werden, bevor eine möglicherweise doppelte Aktion erneut versucht wird.

## 10. Versionen aktualisieren, ohne ein bestehendes Projekt zu verlieren

### Lies zuerst den Release-Eintrag

Jedes Release soll erklären, was sich geändert hat, welche Nutzer betroffen sind, Voraussetzungen, Installationsschritte, Übernahmeschritte für Projekte, Überprüfung, bekannte Einschränkungen und Rückabwicklung. Auch der allgemeine Leitfaden muss sich ändern, wenn sich der normale Ablauf ändert. Verlasse dich nicht allein auf eine Versionsnummer.

Release 6.0.0 erhält die 33 stabilen Namen und die Icon-Identität und stärkt zugleich Nachweise, Quellabhängigkeiten, JSON-Annahme und Zustandsschreibvorgänge. Es ergänzt eigenständig nutzbare Produktions-/Kontextprofile und explizite Referenztreue. Historische Protokoll- und native Laufzeitschema-Nummern bleiben getrennt; ein altes Schema ohne Migration in die Suite-Nummer umzubenennen, bricht die Kompatibilität.

### Bestehende Projekte aus Agent Systems 2.3 / Game 4.3

1. Sichere aktuellen Projektcheckpoint, akzeptierte Anforderungen, Entscheidungen, Designoriginale, Quellenrevision, Toolkit-Version und bekannte externe Wirkungen.
2. Halte fest, woher jeder Skill oder Projektagent tatsächlich geladen wird. Erfasse persönliche und projektlokale Kopien; gehe nicht davon aus, dass die Änderung eines globalen Verzeichnisses jedes Projekt ändert.
3. Installiere das Zielpaket über den passenden Work- oder Codex-Weg oben. Bewahre Quellenversion und Installationsbeleg auf.
4. Öffne das bestehende Projekt erneut und führe vor der nächsten abhängigen Aktion eine ausschließlich lesende Kompatibilitätsprüfung durch.
5. Bitte den Direktor oder Konstruktor, den aktuellen Projektzustand mit dem neuen Ablauf zu vergleichen. Bestimme eine ausdrückliche Aktualisierung des nativen Zustands oder des Arbeitsablaufs nur dort, wo sie erforderlich ist. Erhalte Produktverhalten, akzeptierte Entscheidungen und unbekannte Wirkungen.
6. Zeige die genauen Änderungen vorab an. Ist eine Zustandsmigration erforderlich, verwende das unterstützte Werkzeug und dessen tatsächliches `--help`; binde die Vorschau an den Hash des Quellzustands, den Hash des Zielpakets und die Autorisierungsquelle. Wende den autorisierten geprüften Plan an, statt eine frühere Freigabe zu erfinden.
7. Prüfe jede betroffene Anforderung und die Abnahmekriterien der aktuellen Phase erneut. Führe eine kleine reale Fortsetzungsaufgabe aus und sichere ihre Nachweise.
8. Halte die übernommene Toolkit-Version im Produktcheckpoint fest. Bewahre den Migrationseintrag auf, damit der nächste Chat den Übergang erklären kann.

Game6.0.0 enthält einen geprüften Weg zur Aktualisierung des Arbeitsablaufs für Projekte aus 4.2.0/4.3.0/5.0.0 und behält dabei Laufzeitschema 2.0.0 bei. Die Verwendung hängt vom tatsächlichen Projektzustand und den unterstützten Eingaben des Werkzeugs ab. Auch App- und ChatBot-Projekte brauchen ihre eigene Zustands- und Kompatibilitätsprüfung; sie dürfen nicht allein deshalb durch eine Spielmigration geleitet werden, weil das Paket eine gemeinsame Version hat.

### Zuvor mit einem Konstruktor erstellte Agenten

Die Aktualisierung des Konstruktors schreibt früher von ihm erstellte Agenten nicht um. Solche Agenten können projektspezifische Regeln, Werkzeuge, Wissen und visuelle Identität enthalten. Erfasse sie in ihren eigenen Projekten. Vergleiche die alte Quelle, lokale Änderungen und die vorgeschlagene neue Quelle. Erhalte die ursprünglichen Eigentums-/Installationsnachweise. Fehlen sie, bereite einen ausdrücklichen Übernahmevergleich und Plan vor; erfinde keinen alten Beleg. Führe Regressionstests für die tatsächlichen Zuständigkeiten des Agenten aus und halte die übernommene Version getrennt fest.

Das wiederverwendbare Repository enthält keine privaten Quellpakete von Produktagenten. Die Aktualisierung eines einzelnen Projekts gehört in die kontrollierten Quellen und den Migrationseintrag dieses Projekts und nicht in die globale Skill-Installation aller Nutzer.

### Visuelle Identität erhalten

Bestehende Codex-Icons, Icon-Pfade, Farbe und Icon-Bytes müssen routinemäßige Aktualisierungen überstehen. Eine neue Version ist keine Anweisung, einen vorhandenen Skill oder ein Produkt neu zu gestalten. Neue Skills ohne Identität können den passenden System- oder Projektstil erhalten. Work kann einen Dienstavatar selbst verwalten; trenne dessen Host-Anzeigeverhalten von der portablen Codex-Identität. Erhalte ausgewählte Produkt- und Spieldesignoriginale, nicht nur ihre sprachliche Beschreibung.

### Sorgfältig zurücksetzen

Verwende für die Installation eines Codex-Pakets das genaue Installationsjournal:

```bash
python3 kit/portable/update_skill_suite.py rollback --journal /absolute/path/from-apply/journal.json
```

Die Rückabwicklung prüft Sicherungen und schützt spätere unbekannte Änderungen. Sie macht die durch dieses Journal erfasste Skill-Installation rückgängig. Sie macht keine Produktdatenmigration, kein Deployment, keine Nachricht, keinen Kauf und keine andere externe Aktion rückgängig. Die Wiederherstellung in Work soll den unterstützten Skill-Verwaltungsweg und die gespeicherte frühere Quelle verwenden. Das Zurücksetzen eines Produktzustands braucht ein eigenes geprüftes Wiederherstellungsverfahren.

## 11. Künftige Aktualisierungen vollständig halten

Aktualisiere dieses Repository bei jeder künftigen Toolkit-Änderung mit den kanonischen Quellen, betroffenen Anforderungen, Paketinhalten, Versionsaufzeichnung, Migrationsschritten, Prüfnachweisen und allen erforderlichen Leitfaden- oder Übersetzungsänderungen. Erhalte frühere Release-Einträge. Erzeuge Pakete und Integritätsmetadaten neu aus den geprüften Quellen; veröffentliche kein Archiv aus einem veralteten Host-Cache.

Führe die Prüf- und Paketbefehle des Repositorys entsprechend dem aktuellen `--help` und der Dokumentation für Verantwortliche aus. Bestätige nach der Veröffentlichung den entfernten Commit. „Lokal gespeichert“, „committed“, „veröffentlicht“, „installiert“, „geladen“ und „von einem Projekt übernommen“ sind getrennte Zustände. Verhindert fehlender Zugriff die Veröffentlichung, bewahre die abgeschlossene Arbeit auf und nenne die genaue nicht synchronisierte Revision.

Eine Repository-Regel wirkt, wenn ein künftiger Agent sie in einer Umgebung mit dem erforderlichen Zugriff liest. Sie ist kein globaler Beobachter für alle anderen Chats und Computer. Beginne eine künftige Skill-Verwaltungsaufgabe damit, dieses Repository zu verbinden und dessen `AGENTS.md`, Anforderungen und neuesten Release-Eintrag zu lesen. Ein separater geplanter Synchronisationsdienst bräuchte eine eigene tatsächliche Laufzeitumgebung und Autorisierung; das Paket erstellt ihn nicht unbemerkt.

## 12. Fehlerbehebung

| Symptom | Nächste Prüfung |
| --- | --- |
| Work kann das Repository nicht lesen | Prüfe GitHub-Konto, genaue Freigabe des privaten Repositorys und gewählte Verbindung; bitte Work, eine bekannte Datei zu lesen. |
| Der lokale Klon verlangt Authentifizierung | Richte die lokale Git-Autorisierung über den Anmeldeablauf der Plattform ein. Die Work-Verbindung ist davon getrennt. |
| Skills erscheinen nach dem Speichern nicht | Aktualisiere oder öffne die Skills-Seite erneut, verwende dann einen neuen Projektchat und prüfe die tatsächliche Quellenerkennung. |
| Zwei Kopien desselben Skills erscheinen | Prüfe stabile Namen in persönlichen und Projektstammverzeichnissen. Erhalte lokale Änderungen und kläre die genaue doppelte Quelle; lösche keine anderen Skills. |
| Der Updater meldet Drift oder einen Konflikt | Sichere den lokalen Diff und vergleiche die benannten Dateien mit der gewählten Quelle. Verwende einen geprüften Abgleichplan. |
| Die Dateiprüfung war erfolgreich, doch der Agent verhält sich wie zuvor | Prüfe die vom Host tatsächlich geladene Quelle und führe dann eine kleine Aufgabe aus; Dateiintegrität allein genügt nicht. |
| Work sieht auf einem Mac geänderten Code nicht | Veröffentliche den autorisierten Umfang oder füge ein genaues Artefakt hinzu; ein lokaler Pfad allein gewährt keinen Zugriff. |
| In einem neuen Chat fehlen Entscheidungen | Stelle vor der Fortsetzung den Checkpoint und die vollständigen Anforderungsquellen wieder her. Aktualisiere den gespeicherten Kontext. |
| Der ersten funktionsfähigen Version fehlen vereinbartes Design oder Sprache | Gleiche das Anforderungsverzeichnis ab; erhalte diese Anforderungen im Plan und benenne ihre Implementierungs- und Abnahmeschritte. |
| Deployment, Store-Einreichung oder Geräteprüfungen sind nicht verfügbar | Benenne das genau fehlende Konto, Werkzeug, Gerät oder den Zugriff und setze unabhängige Vorbereitungen fort. Behaupte nicht, die nicht verfügbare Prüfung sei bestanden. |
| Ein Agent behauptet, eine andere Sitzung gestartet zu haben | Frage nach einem überprüften Start-/Empfangsnachweis. Eine Übergabedatei belegt nur den tatsächlich beobachteten Status. |
| Du möchtest kontinuierliche Aufgaben | Bestätige einen tatsächlichen Scheduler, Executor, Zugangsdaten, Verfügbarkeitsprüfungen und Wiederherstellungsweg. Eine Skill-Installation allein stellt sie nicht bereit. |

## 13. Offizielle Dokumentation und Reichweite der Nachweise

Die Oberflächen des Hosts und die Kontoverfügbarkeit können sich ändern. Prüfe beim Installieren oder Verbinden von Diensten die tatsächliche Oberfläche und aktuelle offizielle Dokumentation. Für diesen Leitfaden am 7. November 2026 geprüfte Referenzen zum Produktverhalten:

- [Build skills — ChatGPT Learn](https://learn.chatgpt.com/docs/build-skills): Struktur wiederverwendbarer Skills, lokale Erkennung und Installationskonzepte.
- [Plugins — ChatGPT Learn](https://learn.chatgpt.com/docs/plugins): Plugin-Verzeichnis, Verbindungs- und Vertriebskonzepte.

Dieses Repository verteilt ein wiederverwendbares Paket und dessen kontrollierten Installationsablauf. Ein öffentliches Marketplace-Plugin, eine kommerzielle Lizenz, eine dauerhafte gehostete Laufzeitumgebung, kostenpflichtige Drittanbieterwerkzeuge und Zugangsdaten sind getrennte Liefergegenstände, sofern ein bestimmtes Release sie nicht ausdrücklich liefert und überprüft. Die Marketingkonzepte veranschaulichen Abläufe und vorgesehene Nutzungen; endgültige Werbeaussagen müssen zu überprüften Fähigkeiten und Nachweisen passen.
