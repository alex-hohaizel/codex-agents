# Handbuch für Codex Agent System

Erledigen Sie eine einzelne Aufgabe mit Codex, entwickeln Sie ein Produkt mit Fachrollen oder entwerfen Sie einen wiederverwendbaren Agenten. Das System verknüpft die Arbeit mit ihrer tatsächlichen Quelle, einer verantwortlichen Person und einem überprüfbaren Ergebnis.

[English](../en/GUIDE.md) · [Українська](../uk/GUIDE.md) · [Deutsch](../de/GUIDE.md) · [Italiano](../it/GUIDE.md) · [Español](../es/GUIDE.md) · [Français](../fr/GUIDE.md) · [简体中文](../zh-CN/GUIDE.md)

## Einstieg wählen

- **Codex ausprobieren.** [Installieren und prüfen](#install) · [Erste Aufgabe erledigen](#first-task) · [Abläufe mit Bildbeispielen](../../marketing/de/README.md)
- **Ein Projekt entwickeln oder betreiben.** [Ablauf wählen](#workflow) · [Skills und Rollen finden](#catalog) · [Mac-Oberfläche](#workbench) · [Betrieb und Wiederherstellung](#operations)
- **Das System verstehen.** [Harness](#harness) · [Subagenten](#subagents) · [Kontextkapseln](#context) · [Modelle und Kosten](#models)
- **Belege finden und prüfen.** [Wissenssuche (RAG)](#retrieval) · [Evals](#evals) · [Werkzeuge und Berechtigungen](#permissions)

[Technische Themen (Englisch)](../OPERATING_MODEL.md#engineering-topics) · [RAG-Beispiel (Englisch)](../technical/RETRIEVAL.md) · [Produktanforderungen](../../governance/requirements.csv)

<a name="install"></a>
## Installieren und Erkennung prüfen

1. Öffnen Sie die stabile Veröffentlichung von `alex-hohaizel/codex-agents`. Das Terminalverfahren unter macOS oder Linux verwendet Bash, Python 3.9+, Git, eine angemeldete GitHub CLI (`gh`) und Codex. Für eine begleitete Installation kann Codex jeden Schritt auf Deutsch erklären und exakte Optionen und Pfade beibehalten.
2. Folgen Sie der attestierten Installation. Das Prüfwerkzeug gleicht Archivprüfsumme und GitHub-Attestierung mit Quell-Commit, Workflow und Manifest ab. Wählen Sie die Neuinstallation für ein leeres Profil oder geben Sie die verifizierte Version einer vorhandenen Suite an. [Stabile Veröffentlichung](https://github.com/alex-hohaizel/codex-agents/releases/latest) · [Genaue Befehle](../INSTALL.md#steps)
3. Kontrollieren Sie im Prüfplan die 33 Skills, das Ziel, den Erhalt der Symbole und ihrer Verweise sowie offene Konflikte. Wenden Sie den geprüften Plan an und verifizieren Sie die Dateien mit dem zurückgegebenen Journal. Das verwaltete Profil und die zwölf Rollen haben eine eigene Prüfung und ein eigenes Journal. [Profil und Rollen](../INSTALL.md#profile-and-roles)
4. Installieren Sie Orchestrator und Maintenance nach Bedarf einzeln. Prüfen Sie in Agent Atelier die Vorschau mit exakter Quelle, Ziel und Änderungen. Wenden Sie diese an und kontrollieren Sie das Ergebnis. In Codex stehen die jeweilige persönliche Skill-Verwaltung und die vollständige optionale Quelle zur Verfügung. [Optionale Bestandteile](../INSTALL.md#optional-components)
5. Öffnen Sie einen neuen Codex-Chat im Produktordner. Rufen Sie `$agent-foundry` oder den gewählten Skill auf. Wenn der Host den aufgelösten Pfad anzeigt, vergleichen Sie ihn mit der installierten Quelle. Danach prüfen Sie die Nutzung mit einer Aufgabe, die ein sichtbares Ergebnis hat. [Erkennung in Codex](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)

ChatGPT Work hat eine eigene Oberfläche für persönliche Skills. Verwenden Sie das Work-Archiv und prüfen Sie dort gespeicherte und geladene Einträge. Eine lokale Codex-Installation ist ein eigener Vorgang. [Pakete](../../governance/PACKAGES.md)

<a name="first-task"></a>
## Eine erste Änderung durchführen

Erstellen Sie einen Testordner und öffnen Sie darin einen neuen Codex-Chat. Schreiben Sie `# Cheklist` in `README.md` und eine Zeile zum Beibehalten in `notes.txt`. Fragen Sie auf Deutsch:

```text
Korrigiere die Rechtschreibung der Überschrift in README.md. Lass notes.txt unverändert.
Zeige die korrigierte Überschrift und deine Prüfung beider Dateien.
```

Prüfen Sie die Überschrift `# Checklist` und den ursprünglichen Inhalt von `notes.txt`. Für diesen Auftrag genügt die direkte Bearbeitung. Geben Sie Orchestrator bei einem größeren Projekt das Ziel, den Projektordner, erlaubte Änderungen und ein beobachtbares Abnahmekriterium. Bitten Sie beispielsweise um eine Prüfung des Bestellablaufs mit reproduzierbaren Befunden und Erhalt des freigegebenen Zahlungsvertrags. [Erste Aufgabe zum Nachmachen](../../START_HERE.md#install-and-verify)

<a name="workflow"></a>
## Arbeitsweg und Kontext festlegen

Erledigen Sie die Aufgabe direkt, wählen Sie einen Skill oder lassen Sie `$atelier-orchestrator` entscheiden. Ein Director koordiniert den gesamten Lebenszyklus einer App, eines Chatbots oder Spiels. `$agent-foundry` entwirft einen Agenten oder ein Team für wiederkehrende Arbeit. Prüfen Sie den Agentenpass vor der Erstellung und testen Sie das vorbereitete Paket mit einer Originalaufgabe. Für einen wiederverwendbaren Ablauf mit Auslösern und Abnahmefällen dient `$design-specialist-skills`.

<a name="harness"></a>
### Harness und Berechtigungen

Codex stellt Laufzeit, Werkzeuge und Berechtigungen bereit. Das Repository liefert `AGENTS.md`, Skill-Beschreibungen und Ressourcen, Fachverträge, Rollen und Prüfungen. Verifizieren Sie die geladenen Anweisungen und die Berechtigung am tatsächlichen Werkzeug. [Harness und Berechtigungen](../OPERATING_MODEL.md#harness-and-authority)

<a name="subagents"></a>
### Rollen und Subagenten

Delegieren Sie eigenständige Ergebnisse oder unabhängige Prüfungen. Nennen Sie Rolle, Quellrevision, Eingabepfade, Schreibbereich, Ausgabe, Grenzen, Abbruchbedingung und Rückgabeort. Legen Sie für gemeinsam veränderlichen Zustand einen Schreibverantwortlichen fest. Fordern Sie vor der Integration das tatsächliche Ergebnis an. [Arbeitswege und Subagenten](../OPERATING_MODEL.md#routes-and-subagents)

<a name="context"></a>
### Kontextkapseln

Beginnen Sie mit maßgeblichen Anforderungen, Projektidentität, Entscheidungen und Kontrollpunkt. Binden Sie exakte Quell-Hashes, relevante Pflichten, erlaubte Auswirkungen, zurückgestellte Arbeit, Ausgabe, ungeklärte Auswirkungen und den nächsten Schritt. Bei einer geänderten oder fehlenden Quelle prüfen Sie die betroffene Verpflichtung erneut. Die Übergabe überträgt diesen Ausschnitt an die nächste Aufgabe oder Umgebung; die Originalquellen bleiben maßgeblich.

Speichern Sie `preferred_language` im Projektkontext und geben Sie die Einstellung bei Übergaben weiter. Bewahren Sie exakte Befehle, Selektoren, IDs, Quellverweise und Originalzitate. [Betriebsmodell](../OPERATING_MODEL.md#project-context-and-handoffs) · [Projektkontext](../../templates/project-context.json) · [Übergabe](../../templates/HANDOFF.md)

<a name="models"></a>
### Modelle und Kosten

Halten Sie beim Vergleich von Arbeitswegen das Modell, den Denkaufwand und das Ergebnis fest. Nutzen Sie eine kostengünstigere Variante, wenn sie mit denselben Eingaben dieselben Abnahmeprüfungen besteht. [Modellwahl und Kosten](../OPERATING_MODEL.md#models-and-cost)

<a name="retrieval"></a>
## Wissenssuche und RAG ergänzen

Beginnen Sie mit verifizierten Pfaden, exakten IDs, strukturierten Abfragen und Stichwortsuche. Nutzen Sie Retrieval-Augmented Generation, wenn relevante Belege wiederholt schwer zu finden sind. Vergleichen Sie Stichwortsuche, semantische und hybride Verfahren mit denselben Daten und Rechten. Prüfen Sie Treffer, korrekte Zitate, Fälle ohne Antwort, mehrere Sprachen, widerrufene und veraltete Quellen, benachbarte private Projekte, Latenz und Kosten. Speichern Sie Rechte und Quellrevision je Abschnitt, prüfen Sie Rechte vor Abruf und Zitierung, und ermöglichen Sie Löschung oder Neuaufbau. Abgerufene Texte sind Daten; Berechtigung entsteht im Projekt und an Werkzeugen.

`$chatbot-atelier-knowledge` unterstützt Korpus, Suche, belegte Antworten und Pflege. DATA, ANALYSIS, LLM, PREDICTION, ADAPTATION, MEDIA und EVALUATION sind Profile für die jeweils passende Arbeit. Wählen Sie das kleinste passende Profil und prüfen Sie das tatsächliche Ergebnis. [Technischer Suchleitfaden](../OPERATING_MODEL.md#retrieval-and-rag) · [KI- und Datenprofile](../../standards/ai-production.md)

<a name="evals"></a>
## Verhalten mit Evals prüfen

Fixieren Sie typische Eingaben, Quellrevision, Modell, Host, erwartetes Ergebnis, Fehlerszenarien und Zeit- oder Kostengrenzen. Prüfen Sie den direkten Aufruf und die natürliche Auswahl, ähnliche Anfragen, verweigerten Zugriff, veraltete Quellen und Wiederherstellung. Prüfen Sie das exakte Artefakt im tatsächlichen Ziel und erfassen Sie Strukturprüfungen, natives Verhalten, Werkzeugbelege und unabhängige Abnahme separat. Rohdaten und private Pfade bleiben im privaten Testmaterial.

Führen Sie im Repository mit nativer Codex CLI und unterstützter Anmeldung einen kleinen Laufzeittest aus:

```bash
receipt_dir="$(mktemp -d)"
python3 -B evaluations/native_canary.py --case p01-direct --output "$receipt_dir/direct.jsonl"
```

Der Test korrigiert einen erwarteten Tippfehler im Testprojekt und kontrolliert die zweite Datei. Die Suite prüft auch eine begrenzte Übergabe, einen genehmigten Agentenpass und die erste Nutzung eines erzeugten Skills. Aussagen über externe Produkte benötigen Belege aus deren Umgebung. [Suite, Testdaten und Belege](../../evaluations/README.md) · [Validierung](../../governance/VALIDATION.md)

<a name="workbench"></a>
## Agent Atelier auf dem Mac verwenden

1. Bauen Sie die aktuelle Quelle mit der fixierten Node.js-Lockdatei. In `apps/agent-atelier/` ausführen:

```bash
npm ci --ignore-scripts
npm run build
node launcher/atelier.mjs start
node launcher/atelier.mjs status
node launcher/atelier.mjs doctor
```

2. Suchen Sie in der lokalen Browseroberfläche das Projekt und prüfen Sie die angegebene Abdeckung. Registrierte Codex-Projekte können ohne Chats erscheinen. Verlauf und Artefakte werden beim Öffnen geladen. Prüfen Sie den genauen Ordner in der Vorschau und binden Sie ihn ausdrücklich. Der Demomodus zeigt fiktive Einträge.
3. Öffnen Sie das Arbeitselement und den belegten nächsten Schritt. Übernehmen Sie ihn in das Formular, prüfen Sie Ziel, Abnahme, Eingaben, Rechte und Skills sowie die Route des Orchestrators. Bereiten Sie die Aufgabe vor, starten Sie den autorisierten Lauf und prüfen Sie Ergebnis und Beleg. Einen vorhandenen Chat setzen Sie bei unterstütztem Kontext, bestätigter Identität und freiem Schreibzugriff fort. Für nicht verfügbaren gespeicherten Kontext bereiten Sie eine begrenzte neue Aufgabe vor.
4. Prüfen Sie unter Verbindungen Apps, Plugins und Konnektoren. Bei entsprechender Unterstützung können Sie offizielle OpenAI-Dokumente suchen, ein von Codex erzeugtes PNG ansehen und herunterladen, Openverse-Bilder und -Audio samt Herkunft und Lizenz suchen sowie Repository-Metadaten mit einer vorhandenen GitHub-CLI-Anmeldung lesen. Wählen Sie die im tatsächlichen Host und Konto verfügbaren Operationen. [Handbuch der Oberfläche](../../apps/agent-atelier/README.md) · [API und Verbindungen](../../apps/agent-atelier/shared/API.md)

<a name="operations"></a>
## Betrieb, Wiederherstellung und Aktualisierung

<a name="permissions"></a>
### Werkzeuge und Berechtigungen

Prüfen Sie vor einem schreibenden Werkzeugaufruf Operation, Ziel, Berechtigung, Kosten, Grenzen und erwarteten Beleg. Nach einem Timeout oder ohne Beleg lesen Sie den maßgeblichen Zustand der exakten Anfrage. Wiederholen Sie einen Vorgang nur mit gültiger Berechtigung und geprüftem Schutz vor Duplikaten. Halten Sie ungeklärte Auswirkungen und Belege sichtbar. Bewerten Sie Ergebnisse im tatsächlichen Produkt und erfassen Sie Vorbereitung, Ausführung und Dateierstellung als eigene Zustände. [Werkzeugwirkungen und Belege](../OPERATING_MODEL.md#tools-evidence-and-recovery)

### Wiederherstellung und Aktualisierung

Verwenden Sie für Updates das stabile Archiv und den exakten Plan. Bewahren Sie Journale und vorhandene Daten auf. Nach einer Unterbrechung prüfen Sie zuerst das tatsächliche Ziel. Setzen Sie Kern, Profil oder optionalen Skill mit deren jeweiligem Journal zurück. Sichern Sie Datenbank und Dateien der Oberfläche nach der beschriebenen Prozedur. Starten Sie sie im eigenen Datenordner und prüfen Sie Projektbestand und eine begrenzte Aufgabe. Produktdaten, native Chats und Konten haben eigene Verantwortliche und Wiederherstellungsschritte. [Installation und Wiederherstellung](../INSTALL.md#rollback) · [Arbeit fortsetzen](../../governance/RESUMABLE_WORK.md)

<a name="catalog"></a>
## Skill oder Produktfamilie auswählen

| Selektor | Einstieg für |
| --- | --- |
| `$atelier-orchestrator` | Route wählen, Arbeit fortsetzen und koordinieren |
| `$agent-foundry` | Agent oder Team für eine praktische wiederkehrende Aufgabe |
| `$design-specialist-skills` | Fokussierten wiederverwendbaren Skill oder Skill-Familie entwerfen |
| `$app-atelier-director` | App-Recherche, Konzepte, Spezifikation, UX, Entwicklung, Support, Wachstum, QA, Veröffentlichung und Betrieb |
| `$chatbot-atelier-director` | Nutzer und Kanäle, Produkt, Gespräch, Wissen, Integration, Medien, Entwicklung, QA, Veröffentlichung und Betrieb |
| `$gamedev-director` | Studio, Spielideen, Vorproduktion, Assets, Entwicklung, QA, Veröffentlichung und Live-Betrieb |
| `$codex-agents-maintenance` | Autorisierte Änderungen an Skills und Dokumentation, Releaseprüfung und Pakete |

### Alle Fachskills und Rollen

**App-Team**

- [`$app-atelier-director`](../../kit/skills/app-atelier-director/SKILL.md) · Leitung des Lebenszyklus
- [`$app-atelier-research`](../../kit/skills/app-atelier-research/SKILL.md) · Nutzer- und Marktforschung
- [`$app-atelier-concepts`](../../kit/skills/app-atelier-concepts/SKILL.md) · Produktkonzepte
- [`$app-atelier-specification`](../../kit/skills/app-atelier-specification/SKILL.md) · Anforderungen und Verträge
- [`$app-atelier-experience`](../../kit/skills/app-atelier-experience/SKILL.md) · Nutzungserlebnis und Barrierefreiheit
- [`$app-atelier-build`](../../kit/skills/app-atelier-build/SKILL.md) · Implementierung
- [`$app-atelier-growth`](../../kit/skills/app-atelier-growth/SKILL.md) · Nutzergewinnung
- [`$app-atelier-support`](../../kit/skills/app-atelier-support/SKILL.md) · Supportablauf
- [`$app-atelier-qa`](../../kit/skills/app-atelier-qa/SKILL.md) · Unabhängige Qualitätsprüfung
- [`$app-atelier-release`](../../kit/skills/app-atelier-release/SKILL.md) · Veröffentlichung
- [`$app-atelier-operations`](../../kit/skills/app-atelier-operations/SKILL.md) · Betrieb

**Chatbot-Team**

- [`$chatbot-atelier-director`](../../kit/skills/chatbot-atelier-director/SKILL.md) · Leitung des Lebenszyklus
- [`$chatbot-atelier-research`](../../kit/skills/chatbot-atelier-research/SKILL.md) · Publikums- und Kanalforschung
- [`$chatbot-atelier-specification`](../../kit/skills/chatbot-atelier-specification/SKILL.md) · Verhalten und Zustandsverträge
- [`$chatbot-atelier-conversation`](../../kit/skills/chatbot-atelier-conversation/SKILL.md) · Dialoggestaltung
- [`$chatbot-atelier-knowledge`](../../kit/skills/chatbot-atelier-knowledge/SKILL.md) · Wissen und Abruf
- [`$chatbot-atelier-integrations`](../../kit/skills/chatbot-atelier-integrations/SKILL.md) · Integrationen und Belege
- [`$chatbot-atelier-media`](../../kit/skills/chatbot-atelier-media/SKILL.md) · Medien
- [`$chatbot-atelier-build`](../../kit/skills/chatbot-atelier-build/SKILL.md) · Implementierung
- [`$chatbot-atelier-qa`](../../kit/skills/chatbot-atelier-qa/SKILL.md) · Qualitätsprüfung
- [`$chatbot-atelier-release`](../../kit/skills/chatbot-atelier-release/SKILL.md) · Veröffentlichung
- [`$chatbot-atelier-operations`](../../kit/skills/chatbot-atelier-operations/SKILL.md) · Betrieb und Wiederherstellung

**Spieleteam**

- [`$gamedev-director`](../../kit/skills/gamedev-director/SKILL.md) · Leitung des Lebenszyklus
- [`$gamedev-studio`](../../kit/skills/gamedev-studio/SKILL.md) · Studiopraxis
- [`$gamedev-concepts`](../../kit/skills/gamedev-concepts/SKILL.md) · Spielbare Konzepte
- [`$gamedev-preproduction`](../../kit/skills/gamedev-preproduction/SKILL.md) · Systeme und Produktionsplanung
- [`$gamedev-assets`](../../kit/skills/gamedev-assets/SKILL.md) · Asset-Produktion
- [`$gamedev-build`](../../kit/skills/gamedev-build/SKILL.md) · Gameplay-Implementierung
- [`$gamedev-qa`](../../kit/skills/gamedev-qa/SKILL.md) · Qualitätsprüfung
- [`$gamedev-release`](../../kit/skills/gamedev-release/SKILL.md) · Veröffentlichung
- [`$gamedev-liveops`](../../kit/skills/gamedev-liveops/SKILL.md) · Live-Betrieb

**Codex-Fachrollen**

- [`foundry-architecture`](../../agent-profiles/foundry-architecture.toml) · Architektur
- [`foundry-backend`](../../agent-profiles/foundry-backend.toml) · Backend
- [`foundry-conversation`](../../agent-profiles/foundry-conversation.toml) · Dialoge
- [`foundry-cost`](../../agent-profiles/foundry-cost.toml) · Kosten
- [`foundry-integrations`](../../agent-profiles/foundry-integrations.toml) · Integrationen
- [`foundry-judge`](../../agent-profiles/foundry-judge.toml) · Unabhängige Beurteilung
- [`foundry-platform`](../../agent-profiles/foundry-platform.toml) · Zielplattformen
- [`foundry-privacy`](../../agent-profiles/foundry-privacy.toml) · Datenschutz
- [`foundry-product`](../../agent-profiles/foundry-product.toml) · Produkt
- [`foundry-qa`](../../agent-profiles/foundry-qa.toml) · Qualität
- [`foundry-reliability`](../../agent-profiles/foundry-reliability.toml) · Zuverlässigkeit
- [`foundry-skeptic`](../../agent-profiles/foundry-skeptic.toml) · Kritische Prüfung

Der Katalog enthält alle Skills mit ihren stabilen Namen und alle zwölf Rollen. [Vollständiger Katalog](../CAPABILITIES.md#all-skills-and-roles) · [Bildbeispiele](../../marketing/de/README.md) · [Weitere Sprachen](../../START_HERE.md#use-another-language)
