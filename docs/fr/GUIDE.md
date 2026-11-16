# Guide de Codex Agent System

Traitez une tâche précise dans Codex, développez un produit avec les spécialistes ou créez un agent réutilisable. Le système rattache le travail à sa source, à un responsable et à un résultat vérifiable.

[English](../en/GUIDE.md) · [Українська](../uk/GUIDE.md) · [Deutsch](../de/GUIDE.md) · [Italiano](../it/GUIDE.md) · [Español](../es/GUIDE.md) · [Français](../fr/GUIDE.md) · [简体中文](../zh-CN/GUIDE.md) · [Exemples visuels](../../marketing/fr/README.md)

[Installation](#install) · [Première tâche](#first-task) · [Flux de travail](#workflow) · [RAG](#retrieval) · [Évaluations](#evals) · [Atelier Mac](#workbench) · [Exploitation](#operations) · [Catalogue](#catalog)

<a name="install"></a>
## Installer et vérifier la détection

1. Ouvrez la version stable de `alex-hohaizel/codex-agents`. La procédure en terminal sur macOS ou Linux utilise Bash, Python 3.9+, Git, GitHub CLI (`gh`) avec une session authentifiée et Codex. Pour une installation guidée, demandez à Codex d’expliquer chaque étape en français en conservant les options et chemins exacts.
2. Suivez la procédure avec attestation. Le vérificateur compare l’empreinte du paquet et l’attestation GitHub au commit source, au workflow et au manifeste. Choisissez une première installation si la suite gérée est absente, ou indiquez la version installée que vous avez vérifiée. [Version stable](https://github.com/alex-hohaizel/codex-agents/releases/latest) · [Commandes exactes](../INSTALL.md#steps)
3. Vérifiez dans l’audit les 33 compétences, la destination, la conservation des icônes et de leurs références et les conflits ouverts. Appliquez le plan relu et vérifiez les fichiers avec le journal renvoyé. Le profil géré et les douze rôles disposent de leur propre audit et journal. [Profil et rôles](../INSTALL.md#profile-and-roles)
4. Installez Orchestrator et Maintenance séparément selon vos besoins. Dans Agent Atelier, examinez l’aperçu de la source exacte, la cible et les modifications avant de les appliquer et de les vérifier. Dans Codex, utilisez le gestionnaire de compétences personnelles avec le dossier optionnel complet. [Composants optionnels](../INSTALL.md#optional-components)
5. Ouvrez un nouveau chat Codex dans le dossier du projet. Appelez `$agent-foundry` ou la compétence souhaitée. Lorsque l’hôte expose son chemin résolu, comparez-le à celui de la source installée. Vérifiez ensuite l’utilisation sur une tâche dont le résultat est observable. [Détection dans Codex](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)

ChatGPT Work utilise une interface distincte pour ses compétences personnelles. Utilisez le paquet Work et vérifiez les enregistrements réellement sauvegardés et chargés sur cet hôte. L’installation locale de Codex suit son propre parcours. [Paquets](../../governance/PACKAGES.md)

<a name="first-task"></a>
## Faire une première modification

Créez un dossier de test et ouvrez-y un nouveau chat Codex. Placez `# Cheklist` dans `README.md` et une ligne à conserver dans `notes.txt`. Demandez en français :

```text
Corrige l’orthographe du titre dans README.md. Conserve notes.txt intact.
Montre le titre corrigé et comment tu as vérifié les deux fichiers.
```

Relevez le titre `# Checklist` et le contenu original de `notes.txt`. Un traitement direct suffit ici. Pour un projet plus large, indiquez à Orchestrator le résultat, le dossier du projet, les modifications permises et un critère d’acceptation observable. Par exemple, demandez une revue du paiement qui préserve le contrat approuvé et rapporte les problèmes reproductibles. [Première tâche reproductible](../../START_HERE.md#install-and-verify)

<a name="workflow"></a>
## Choisir le parcours et conserver le contexte

- **Harness .** Codex fournit le moteur d’exécution, les outils et le contrôle des permissions. Le dépôt fournit `AGENTS.md`, les descriptions et ressources des compétences, les contrats métier, les rôles et les vérifications. Confirmez les instructions chargées et appliquez les autorisations au niveau de l’outil réel.
- **Parcours .** Traitez la tâche directement, appelez une compétence ou demandez à `$atelier-orchestrator` de choisir. Prenez un directeur pour le cycle complet d’une application, d’un chatbot ou d’un jeu. `$agent-foundry` sert à concevoir un agent ou une équipe pour un travail récurrent. Relisez le passeport avant construction, puis testez le paquet préparé sur une tâche originale. `$design-specialist-skills` sert à définir un flux réutilisable, ses déclencheurs et son acceptation.
- **Rôles et sous-agents .** Déléguez des résultats séparés ou une revue indépendante. Précisez l’acteur, la révision, les chemins en entrée, l’autorisation d’écriture, le livrable, les limites, la condition d’arrêt et où rendre le résultat. Attribuez l’écriture de l’état partagé à un seul acteur. Récupérez le résultat réel avant l’intégration.
- **Capsule de contexte .** Partez des exigences qui font foi, de l’identité, des décisions et du point de reprise du projet. Fixez les empreintes des sources et transportez les obligations, effets permis, travaux différés, résultat, effets non résolus et prochaine action qui concernent la tâche. Une source modifiée ou indisponible entraîne une nouvelle vérification de l’obligation associée. Le transfert passe cette sélection au prochain acteur ou hôte et les sources originales continuent de faire foi.

Enregistrez `preferred_language` dans le contexte du projet et transmettez-le lors des relais. Conservez les commandes, sélecteurs, identifiants, références et citations originales. [Modèle de travail](../OPERATING_MODEL.md#project-context-and-handoffs) · [Contexte de projet](../../templates/project-context.json) · [Passage de relais](../../templates/HANDOFF.md)

<a name="retrieval"></a>
## Ajouter de la recherche et du RAG

Commencez par les chemins vérifiés, identifiants exacts, requêtes structurées et recherche lexicale. Ajoutez la génération augmentée par la recherche quand les éléments utiles restent difficiles à trouver. Comparez les approches lexicale, sémantique et hybride avec le même corpus autorisé avant de choisir un index ou un stockage vectoriel. Vérifiez les résultats trouvés, la fidélité des citations, les cas sans réponse, plusieurs langues, les sources révoquées ou périmées, les projets privés voisins, la latence et le coût. Associez les droits et la révision à chaque fragment, contrôlez l’accès avant recherche et citation, et prévoyez suppression ou reconstruction. Le texte récupéré sert de donnée; les droits de la tâche viennent du projet et des outils réels.

Utilisez `$chatbot-atelier-knowledge` pour le corpus, les réponses fondées sur des sources et le cycle de vie. DATA, ANALYSIS, LLM, PREDICTION, ADAPTATION, MEDIA et EVALUATION sont des profils pour les tâches concernées. Retenez le profil le plus ciblé et vérifiez le résultat chez son véritable consommateur. [Guide technique de la recherche](../OPERATING_MODEL.md#retrieval-and-rag) · [Profils IA et données](../../standards/ai-production.md)

<a name="evals"></a>
## Évaluer les comportements et les preuves

Figez les entrées représentatives, la révision des sources, le modèle, l’hôte, le résultat attendu, les cas d’échec et les limites de durée ou de coût. Testez l’appel explicite et la sélection naturelle, les requêtes proches, les refus d’accès, les références périmées et la reprise. Éprouvez l’artefact dans le système qui l’utilise. Notez séparément contrôles structurels, comportement natif, reçus d’opération et acceptation indépendante. Gardez les requêtes brutes et chemins privés dans le matériel de test isolé.

Depuis la racine du dépôt, lancez un petit contrôle d’exécution avec Codex CLI et une session prise en charge :

```bash
receipt_dir="$(mktemp -d)"
python3 -B evaluations/native_canary.py --case p01-direct --output "$receipt_dir/direct.jsonl"
```

Le contrôle corrige une faute attendue dans un projet jetable et vérifie l’autre fichier. La suite couvre aussi un relais ciblé, un passeport de constructeur approuvé et le premier usage d’une compétence générée. Une affirmation sur un produit externe requiert des preuves dans son environnement réel. [Suite, données et reçus](../../evaluations/README.md) · [Validation](../../governance/VALIDATION.md)

<a name="workbench"></a>
## Utiliser Agent Atelier sur Mac

1. Ouvrez les sources actuelles et compilez avec le fichier de verrouillage Node.js. Dans `apps/agent-atelier/`, exécutez :

```bash
npm ci --ignore-scripts
npm run build
node launcher/atelier.mjs start
node launcher/atelier.mjs status
node launcher/atelier.mjs doctor
```

2. Dans l’interface locale, trouvez le projet et vérifiez la couverture indiquée. Les projets inscrits dans Codex peuvent apparaître sans chats. L’historique et les artefacts se chargent à l’ouverture. Examinez le dossier exact, puis liez-le explicitement. Le mode de démonstration utilise des données fictives.
3. Ouvrez l’élément de travail et sa prochaine action documentée. Transférez-la dans le formulaire et vérifiez objectif, acceptation, entrées, permissions, compétences et parcours Orchestrator. Préparez la tâche. Démarrez le travail autorisé et vérifiez résultat et reçu. Reprenez un chat existant si le contexte et l’identité sont pris en charge et que l’écrivain est disponible. Pour un contexte indisponible, préparez une nouvelle tâche délimitée.
4. Dans Connexions, inspectez apps, extensions et connecteurs. Lorsque le système le permet, l’interface recherche la documentation officielle OpenAI, montre et télécharge un PNG produit par Codex, trouve des images et sons Openverse avec origine et licence, et lit les métadonnées d’un dépôt via une session GitHub CLI existante. Choisissez une opération prise en charge par l’hôte et le compte réels. [Guide Agent Atelier](../../apps/agent-atelier/README.md) · [API et connexions](../../apps/agent-atelier/shared/API.md)

<a name="operations"></a>
## Exploiter, restaurer et mettre à jour

Avant une action d’écriture, vérifiez opération, cible, autorisation, coût, limites et reçu attendu. Suite à un délai dépassé ou à un reçu absent, relisez l’état faisant foi pour la requête exacte. Renouvelez l’action avec l’autorisation courante et une protection testée contre les doublons. Tenez visibles les effets incertains et les preuves. Évaluez le résultat dans le produit réel en distinguant préparation, exécution et création de fichiers.

Utilisez le paquet stable et son plan exact pour les mises à jour. Conservez journaux et état. Après une interruption, examinez la cible réelle avant de continuer. Restaurez le noyau, le profil ou un composant optionnel avec son propre journal. Sauvegardez la base et les fichiers de l’interface selon la procédure, redémarrez avec le bon répertoire de données puis vérifiez les projets et une tâche bornée. Données produit, chats natifs et comptes ont chacun leurs responsables et procédures de restauration. [Installation et restauration](../INSTALL.md#rollback) · [Reprise du travail](../../governance/RESUMABLE_WORK.md)

<a name="catalog"></a>
## Choisir une compétence ou une famille

| Sélecteur | Utilisation |
| --- | --- |
| `$atelier-orchestrator` | Choisir le parcours, poursuivre et coordonner |
| `$agent-foundry` | Créer un agent ou une équipe pour une tâche récurrente réelle |
| `$design-specialist-skills` | Définir une compétence réutilisable ou une famille ciblée |
| `$app-atelier-director` | Recherche, concepts, spécification, UX, développement, support, croissance, QA, publication et exploitation d’une application |
| `$chatbot-atelier-director` | Publics et canaux, produit, conversation, connaissances, intégrations, médias, développement, QA, publication et exploitation |
| `$gamedev-director` | Studio, concepts, préproduction, ressources, développement, QA, publication et suivi en production |
| `$codex-agents-maintenance` | Changements autorisés des compétences et guides, validation et publication des paquets |

### Liste complète des spécialités et des rôles

**Équipe application**

- [`$app-atelier-director`](../../kit/skills/app-atelier-director/SKILL.md) · Pilotage du cycle de vie
- [`$app-atelier-research`](../../kit/skills/app-atelier-research/SKILL.md) · Recherche utilisateurs et marché
- [`$app-atelier-concepts`](../../kit/skills/app-atelier-concepts/SKILL.md) · Concepts produit
- [`$app-atelier-specification`](../../kit/skills/app-atelier-specification/SKILL.md) · Exigences et contrats
- [`$app-atelier-experience`](../../kit/skills/app-atelier-experience/SKILL.md) · Expérience et accessibilité
- [`$app-atelier-build`](../../kit/skills/app-atelier-build/SKILL.md) · Implémentation
- [`$app-atelier-growth`](../../kit/skills/app-atelier-growth/SKILL.md) · Acquisition
- [`$app-atelier-support`](../../kit/skills/app-atelier-support/SKILL.md) · Parcours de support
- [`$app-atelier-qa`](../../kit/skills/app-atelier-qa/SKILL.md) · Revue qualité indépendante
- [`$app-atelier-release`](../../kit/skills/app-atelier-release/SKILL.md) · Publication
- [`$app-atelier-operations`](../../kit/skills/app-atelier-operations/SKILL.md) · Exploitation

**Équipe chatbot**

- [`$chatbot-atelier-director`](../../kit/skills/chatbot-atelier-director/SKILL.md) · Pilotage du cycle de vie
- [`$chatbot-atelier-research`](../../kit/skills/chatbot-atelier-research/SKILL.md) · Recherche des publics et canaux
- [`$chatbot-atelier-specification`](../../kit/skills/chatbot-atelier-specification/SKILL.md) · Contrats de comportement et d’état
- [`$chatbot-atelier-conversation`](../../kit/skills/chatbot-atelier-conversation/SKILL.md) · Conception des dialogues
- [`$chatbot-atelier-knowledge`](../../kit/skills/chatbot-atelier-knowledge/SKILL.md) · Connaissances et recherche
- [`$chatbot-atelier-integrations`](../../kit/skills/chatbot-atelier-integrations/SKILL.md) · Intégrations et reçus
- [`$chatbot-atelier-media`](../../kit/skills/chatbot-atelier-media/SKILL.md) · Médias
- [`$chatbot-atelier-build`](../../kit/skills/chatbot-atelier-build/SKILL.md) · Implémentation
- [`$chatbot-atelier-qa`](../../kit/skills/chatbot-atelier-qa/SKILL.md) · Revue qualité
- [`$chatbot-atelier-release`](../../kit/skills/chatbot-atelier-release/SKILL.md) · Publication
- [`$chatbot-atelier-operations`](../../kit/skills/chatbot-atelier-operations/SKILL.md) · Exploitation et reprise

**Équipe jeu**

- [`$gamedev-director`](../../kit/skills/gamedev-director/SKILL.md) · Pilotage du cycle de vie
- [`$gamedev-studio`](../../kit/skills/gamedev-studio/SKILL.md) · Pratiques du studio
- [`$gamedev-concepts`](../../kit/skills/gamedev-concepts/SKILL.md) · Concepts jouables
- [`$gamedev-preproduction`](../../kit/skills/gamedev-preproduction/SKILL.md) · Systèmes et planification
- [`$gamedev-assets`](../../kit/skills/gamedev-assets/SKILL.md) · Production des ressources
- [`$gamedev-build`](../../kit/skills/gamedev-build/SKILL.md) · Implémentation du jeu
- [`$gamedev-qa`](../../kit/skills/gamedev-qa/SKILL.md) · Revue qualité
- [`$gamedev-release`](../../kit/skills/gamedev-release/SKILL.md) · Publication
- [`$gamedev-liveops`](../../kit/skills/gamedev-liveops/SKILL.md) · Suivi en production

**Rôles spécialistes Codex**

- [`foundry-architecture`](../../agent-profiles/foundry-architecture.toml) · Architecture
- [`foundry-backend`](../../agent-profiles/foundry-backend.toml) · Backend
- [`foundry-conversation`](../../agent-profiles/foundry-conversation.toml) · Dialogues
- [`foundry-cost`](../../agent-profiles/foundry-cost.toml) · Coûts
- [`foundry-integrations`](../../agent-profiles/foundry-integrations.toml) · Intégrations
- [`foundry-judge`](../../agent-profiles/foundry-judge.toml) · Jugement indépendant
- [`foundry-platform`](../../agent-profiles/foundry-platform.toml) · Plateformes cibles
- [`foundry-privacy`](../../agent-profiles/foundry-privacy.toml) · Confidentialité
- [`foundry-product`](../../agent-profiles/foundry-product.toml) · Produit
- [`foundry-qa`](../../agent-profiles/foundry-qa.toml) · Qualité
- [`foundry-reliability`](../../agent-profiles/foundry-reliability.toml) · Fiabilité
- [`foundry-skeptic`](../../agent-profiles/foundry-skeptic.toml) · Revue critique

Le catalogue couvre chaque compétence par son nom stable et les douze rôles. [Catalogue complet](../CAPABILITIES.md#all-skills-and-roles) · [Exemples visuels](../../marketing/fr/README.md) · [Autres langues](../../START_HERE.md#use-another-language)
