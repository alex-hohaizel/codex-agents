# Agent System — le guide complet Work + Codex

[English](../en/GUIDE.md) · [Українська](../uk/GUIDE.md) · [Deutsch](../de/GUIDE.md) · [Italiano](../it/GUIDE.md) · [Español](../es/GUIDE.md) · [Français](../fr/GUIDE.md) · [中文](../zh-CN/GUIDE.md)

**Référence du guide :** Agent System 5.0.0, 7 novembre 2026. **Suite réutilisable :** 33 compétences. Ce guide couvre une nouvelle installation, le travail quotidien, le partage d'un projet entre Work et Codex et la mise à jour d'un projet existant. Les révisions de la documentation et des paquets du dépôt peuvent changer sans modifier la version des compétences sous-jacentes ; consultez la fiche de version avant toute mise à jour.


**Campagne et édition du dépôt 1.1.0 :** [Publicité en anglais](../../marketing/campaign/README.md) · [Українська реклама](../../marketing/campaign/README.uk.md). La campagne comprend dix supports correspondants par langue sur les applications, jeux, chatbots, plateformes, l’automatisation et les spécialistes personnalisés. La publicité est disponible uniquement en anglais et en ukrainien ; chaque guide reste complet dans sa langue annoncée. Cette édition modifie la présentation, la documentation et des outils compatibles du dépôt ; la suite réutilisable reste en version 5.0.0. Les installations existantes vérifiées n’exigent ni réinstallation ni réinitialisation du produit. Poursuivez le même projet avec ses exigences, son identité visuelle, ses décisions et son checkpoint et lisez les instructions actuelles du dépôt avant la prochaine tâche dépendante.

## 1. Ce que cela vous apporte

Décrivez un résultat avec des mots courants. Le système vous aide à en faire une tâche concrète, mobilise les spécialités pertinentes, conserve ensemble les décisions et les exigences, et vérifie que le résultat correspond à l'objectif convenu.

Par exemple, « Aide-moi à réduire la charge de la base de données de ce backend » peut devenir une investigation ciblée des requêtes, des limites transactionnelles, du cache, des mesures de performance et d'une modification testée. « Crée une application mobile pour ce public » demande un parcours plus large : recherche, choix de produit, conception, architecture, réalisation, contrôles qualité, préparation de la sortie et exploitation. Une petite réparation doit rester une petite réparation. Un produit complet doit conserver l'ensemble de ses exigences, y compris les parties prévues après la première version fonctionnelle.

Une **compétence** est un ensemble réutilisable d'instructions de travail, de références et parfois de scripts. Un **agent** applique un rôle et ces instructions à une tâche. Un **directeur** coordonne une famille de produits. Un **constructeur** conçoit un agent spécialisé ou un ensemble réutilisable de compétences lorsque les familles existantes ne couvrent pas le travail. Ils fonctionnent au moyen de ChatGPT ou Codex et des outils réellement disponibles dans cet environnement. Installer des instructions ne crée pas de serveur en fonctionnement, n'achète pas de services, n'accorde pas d'autorisations sur un dépôt et ne lance pas de processus permanent en arrière-plan.

La valeur réside dans l'organisation du travail : un brief commun, des exigences explicites, les spécialistes pertinents, des décisions préservées, des transmissions vérifiables et une manière de reprendre le travail. Le dépôt ne revendique ni supériorité mesurée, ni revenus garantis, ni acceptation garantie par les boutiques, ni préparation automatique à la production.

## 2. Choisir par où commencer

| Votre situation | Commencer avec | Une première demande utile |
| --- | --- | --- |
| Vous voulez un agent spécialisé adapté à un travail récurrent | `agent-foundry` | « Crée un agent qui étudie les problèmes de performance de nos services Go. Précise d'abord ses responsabilités, ses preuves et ses accès. » |
| Vous voulez une compétence réutilisable ou une famille coordonnée de compétences | `design-specialist-skills` | « Conçois une procédure de revue réutilisable pour nos intégrations événementielles, avec reprise après échec. » |
| Vous voulez développer une application ou un produit existant | `app-atelier-director` | « Reprends cette application à partir de son point de contrôle. Préserve ses exigences acceptées et identifie le prochain livrable utile. » |
| Vous voulez un chatbot, un bot d'assistance ou un compagnon conversationnel | `chatbot-atelier-director` | « Conçois un bot pour ce public et ces canaux, avec sa langue, sa mémoire, ses actions et ses coûts d'exploitation. » |
| Vous voulez un jeu mobile ou poursuivre un jeu existant | `gamedev-director` | « Développe des concepts de jeu autour de cette expérience, avec des commandes pertinentes, une progression et un parcours de production réalisable. » |
| Vous connaissez déjà l'étape exacte | Le spécialiste pertinent ci-dessous | « Examine cet écran de paiement selon la conception approuvée et les critères d'acceptation. » |

Vous n'avez pas besoin de mémoriser les 33 noms. Utilisez un directeur pour un produit ou un constructeur pour une nouvelle procédure spécialisée. Vous pouvez aussi demander explicitement une compétence dans le sélecteur de l'environnement hôte. Dans Work, la forme habituelle est `@skill-name` ; dans Codex, `$skill-name`. Les sélecteurs et noms affichés disponibles peuvent varier selon la version de l'hôte. Demandez-lui d'indiquer la source exacte chargée lorsque vous avez besoin de certitude.

### Le catalogue complet

#### Deux constructeurs

| Compétence | Ce qu'elle vous aide à produire |
| --- | --- |
| `agent-foundry` | Un agent spécialisé ou une famille coordonnée d'agents, définis autour d'un domaine réel, de responsabilités, d'outils, de connaissances, de contrôles et d'un mode de fonctionnement réalisable. Sa première mission est de concevoir l'agent, plutôt que d'exécuter silencieusement le futur projet de cet agent. |
| `design-specialist-skills` | Des compétences et familles de compétences réutilisables pour une tâche définie : les bonnes spécialités, les critères qualité, les références, les outils et l'ordre de travail. |

#### Équipe application — 11 compétences

| Compétence | Son rôle en termes simples |
| --- | --- |
| `app-atelier-director` | Assure la cohérence du projet d'application depuis la première idée jusqu'au développement et à l'exploitation. |
| `app-atelier-research` | Étudie les utilisateurs, leurs besoins, les alternatives et les éléments de marché avant que l'équipe investisse dans une orientation produit. |
| `app-atelier-concepts` | Compare des options produit complètes : utilité, expérience, modèle économique, coûts et périmètre réaliste. |
| `app-atelier-specification` | Transforme le produit choisi en exigences précises et en contrats de comportement, données, API, authentification et paiement. |
| `app-atelier-experience` | Crée et vérifie la marque, les écrans, les états, l'accueil initial, l'accessibilité, la localisation et les éléments de conception destinés à la production. |
| `app-atelier-build` | Réalise les clients Android, iOS et web convenus, le backend et les intégrations nécessaires, avec des builds reproductibles. |
| `app-atelier-support` | Conçoit et réalise le bot d'assistance et le parcours de connaissances du produit, avec escalade et actions contrôlées. |
| `app-atelier-qa` | Vérifie indépendamment les exigences, la conception, la réalisation, les paiements, la confidentialité, la reprise et l'aptitude à la sortie lorsqu'un acteur indépendant est disponible. |
| `app-atelier-release` | Vérifie tôt la faisabilité de la sortie, puis prépare la signature, les fiches des boutiques, les déploiements, les justificatifs et le retour arrière dans le périmètre autorisé. |
| `app-atelier-growth` | Évalue et prépare les canaux d'acquisition pertinents, les contenus et les mesures, puis active une voie autorisée lorsque le produit est prêt. |
| `app-atelier-operations` | Gère les incidents, les indicateurs produit, les demandes d'assistance, les coûts, les sauvegardes, les changements et l'exploitation continue. |

#### Équipe chatbot — 11 compétences

| Compétence | Son rôle en termes simples |
| --- | --- |
| `chatbot-atelier-director` | Coordonne tout le cycle de vie d'un bot et préserve ses capacités existantes lors de la reprise du travail. |
| `chatbot-atelier-research` | Étudie le public, le domaine, les contraintes des plateformes, les intégrations et la faisabilité pratique. |
| `chatbot-atelier-specification` | Définit les règles, l'état, les données, les outils, les événements, les erreurs, la confidentialité et les critères d'acceptation du bot. |
| `chatbot-atelier-conversation` | Développe sa langue, son caractère, ses questions utiles, son initiative, ses boutons et son comportement en conversation individuelle ou de groupe. |
| `chatbot-atelier-knowledge` | Conçoit les sources de connaissances et une mémoire au périmètre défini, la recherche lorsque pertinente, les corrections, l'expiration, la suppression et la confidentialité. |
| `chatbot-atelier-integrations` | Construit les adaptateurs de plateforme, callbacks, outils, tâches planifiées et actions externes fiables, avec reprise et preuves de livraison. |
| `chatbot-atelier-media` | Crée et intègre l'identité visuelle, les images, l'animation, le son et la voix du bot au moyen des outils disponibles. |
| `chatbot-atelier-build` | Réalise le bot complet convenu, avec l'environnement d'exécution et l'intégration en production nécessaires. |
| `chatbot-atelier-qa` | Vérifie la conversation, les connaissances, la confidentialité, les actions, les médias, l'exécution et les scénarios négatifs selon des preuves réelles. |
| `chatbot-atelier-release` | Prépare et effectue une sortie autorisée avec identification exacte des sources et du build, contrôles de livraison, compatibilité des données et retour arrière. |
| `chatbot-atelier-operations` | Maintient la fiabilité, la qualité des conversations, l'assistance, les coûts, les migrations et le développement continu. |

#### Équipe jeu — neuf compétences

| Compétence | Son rôle en termes simples |
| --- | --- |
| `gamedev-director` | Coordonne le projet de jeu en préservant son orientation créative acceptée, ses décisions et ses points de contrôle. |
| `gamedev-studio` | Établit ou restaure l'identité du studio, les originaux de marque acceptés, l'identité développeur et la préparation des comptes. |
| `gamedev-concepts` | Produit des concepts de jeu distincts avec commandes, systèmes interdépendants, progression, direction artistique et parcours de production réalisable. |
| `gamedev-preproduction` | Développe le concept choisi en conception détaillée du jeu et technique, règles chiffrées, catalogues, états et plan de production. |
| `gamedev-assets` | Crée et intègre les illustrations, animations, interfaces, sons et retours haptiques en préservant les sources acceptées et leur relation avec les ressources d'exécution. |
| `gamedev-build` | Réalise le jeu mobile natif : commandes, caméra, gameplay, ennemis, monde, progression, économie, sauvegardes et builds par plateforme. |
| `gamedev-qa` | Vérifie le gameplay réel, le comportement sur appareil, les commandes, les sauvegardes, les performances et les exigences, en distinguant les preuves d'exécution des contrôles documentaires. |
| `gamedev-release` | Prépare la signature, les binaires exacts, les éléments des boutiques, les achats, la confidentialité, le déploiement progressif et la reprise pour une sortie autorisée. |
| `gamedev-liveops` | Développe et maintient le jeu publié à partir de la télémétrie observée, des incidents, de la progression, des contenus, de l'économie et des changements compatibles. |

Ce sont des responsabilités, pas la promesse que 33 agents s'exécutent simultanément. Le système doit choisir l'équipe et le niveau d'effort nécessaires à la tâche. Une revue n'est indépendante que lorsqu'un autre acteur l'effectue réellement ; l'autocontrôle de l'auteur doit être présenté comme tel.

## 3. Choisir votre langue avant l'installation

Ouvrez le guide traduit à partir des liens ci-dessus. L'anglais est utilisé par défaut si aucune préférence n'est fournie. Les guides traduits couvrent les mêmes étapes ; le code, les noms stables des compétences, les noms de fichiers et les identifiants de protocole restent inchangés pour que les commandes fonctionnent de façon cohérente.

Au début de l'installation ou du projet, collez ceci et remplacez la langue :

```text
Ma langue de travail est le français (fr). Utilise-la pour les explications,
questions, points d'avancement, instructions de transmission et rapports qui
me sont destinés. Conserve les noms stables des compétences, la syntaxe des
commandes et les identifiants techniques. Enregistre cette préférence dans
le contexte sauvegardé du projet et les transmissions. Demande séparément
la langue du produit que nous construisons.
```

La langue de la documentation, la langue de conversation et la langue du produit sont des choix distincts. Par exemple, vous pouvez lire le guide ukrainien, travailler en ukrainien avec l'agent et publier une application en anglais et en allemand. Précisez les trois lorsqu'ils sont pertinents. Enregistrez la préférence dans le modèle de contexte du projet ou un fichier équivalent existant, et incluez-la dans chaque transmission. Changer uniquement la langue d'une page du navigateur ne définit pas la langue d'un autre chat.

## 4. Préparer vos comptes et vos sources

1. Connectez-vous au compte ChatGPT ou Codex avec lequel vous utiliserez la suite. Vérifiez que le mode requis et les outils de gestion des compétences sont réellement disponibles dans ce compte ou espace de travail.
2. Ouvrez `https://github.com/alex-hohaizel/codex-agents`. Le propriétaire contrôle actuellement la visibilité du dépôt. Un dépôt privé exige un compte GitHub autorisé et une connexion ayant accès à ce dépôt précis.
3. Dans Work, connectez ou sélectionnez GitHub dans l'interface Plugins/connexions disponible. Si l'accès est limité à certains dépôts, incluez `alex-hohaizel/codex-agents`. Demandez à Work de lire `README.md` et d'indiquer la branche et la révision auxquelles il accède réellement.
4. Dans Codex local, autorisez l'accès Git local si vous voulez cloner un dépôt privé. Une connexion GitHub dans Work ne prouve pas que Terminal peut s'authentifier sur votre ordinateur.
5. Utilisez une version nommée ou un commit exact pour l'installation. Conservez cet identifiant. Lire une branche `main` non figée pendant qu'elle évolue peut mélanger des versions.
6. Téléchargez la révision choisie du dépôt via **Code → Download ZIP** dans GitHub, ou clonez-la avec Git. Extrayez l'archive téléchargée avant l'installation. Vous devez voir `kit/manifest.json`, `kit/portable/` et `kit/skills/`.
7. Ne placez ni le téléchargement, ni les plans, ni les sauvegardes dans un répertoire de découverte des compétences. Un dossier ordinaire comme Téléchargements ou un espace consacré à la gestion des compétences convient.

Pour Git local, utilisez une branche confirmée et une nouvelle destination ne contenant aucun autre travail :

```bash
git clone --branch main https://github.com/alex-hohaizel/codex-agents.git "codex-agents"
cd "codex-agents"
git rev-parse HEAD
git status --short
```

Un clone de `main` est une copie de travail pratique des sources. Avant d'appliquer une mise à jour, confirmez que son SHA correspond à la version choisie. Ne collez pas de jetons d'accès dans un chat, un fichier projet, une commande shell ou un document de transmission. Utilisez la connexion de compte ou le parcours d'identification de la plateforme.

## 5. Installer dans Work depuis un nouveau compte

### Ce que fait ce parcours

Il enregistre les 33 compétences réutilisables comme compétences personnelles selon la procédure de gestion prise en charge par l'hôte. Connecter GitHub, téléverser un ZIP, lire ce guide ou ajouter des fichiers du dépôt comme sources d'un projet ne suffit pas à établir qu'une compétence a été installée ou chargée.

### Étape par étape

1. Ouvrez Work et créez ou ouvrez un projet de gestion des compétences. Vous y gérez la boîte à outils, plutôt que le produit que vous construirez ensuite.
2. Choisissez votre langue avec le bloc de la section 3.
3. Fournissez l'accès à la révision choisie du dépôt. Si Work ne peut pas lire les fichiers GitHub privés, connectez ce dépôt ou joignez le paquet préparé via l'interface de fichiers disponible.
4. Invoquez la fonction Skill Creator/gestion des compétences disponible. Demandez-lui d'examiner le paquet avant de modifier les éléments installés.
5. Collez le bloc d'installation ci-dessous. Il autorise l'installation dans ce périmètre et les vérifications nécessaires.
6. Laissez Work examiner l'inventaire existant par nom stable. Pour un nouveau compte, il doit créer les entrées manquantes ; pour un compte existant, il doit mettre à jour les entrées personnelles correspondantes et préserver les compétences sans rapport.
7. Conservez le rapport d'installation. Il doit identifier chacune des 33 compétences, sa version, sa révision source, son résultat et les échecs non résolus.
8. Actualisez ou rouvrez la page Skills si son affichage est ancien. Ouvrez un nouveau chat dans le projet produit visé et effectuez les contrôles de chargement et de fonctionnement ci-dessous.

```text
Installe les 33 compétences personnelles réutilisables de la révision choisie
et vérifiée d'alex-hohaizel/codex-agents, à partir de kit/manifest.json et kit/skills/.
Ma langue de travail est le français (fr).

Utilise la procédure de gestion des compétences personnelles prise en charge
par l'hôte. Examine les entrées existantes par nom stable, vérifie le paquet,
préserve les compétences sans rapport et l'identité visuelle existante, puis
installe ou actualise les entrées correspondantes. Conserve des sauvegardes
et la provenance exacte des sources. N'installe pas globalement d'agents propres
à un projet. Ne modifie ni données produit, ni services de production, ni réglages du compte.

Indique chaque nom stable, version, révision source et statut create/update/noop/failure.
Distingue l'enregistrement d'une compétence, sa découverte par l'hôte et son
utilisation réelle. Si la gestion des compétences n'est pas disponible, explique
la capacité précise qui manque ; ne présente pas une copie téléversée ou en
lecture seule comme installée.
```

La procédure prise en charge par Work peut enregistrer les compétences une à une. Un résultat partiel doit nommer les entrées terminées et celles qui restent, afin de reprendre sans danger plutôt que de recommencer. Exécuter le programme de mise à jour portable Codex dans un système de fichiers cloud ne prouve pas que votre répertoire personnel de compétences Work a été mis à jour.

## 6. Installer ou mettre à jour dans Codex

### Le parcours le plus simple : demander à Codex une installation contrôlée

1. Téléchargez ou clonez la révision choisie comme décrit ci-dessus.
2. Ouvrez Codex dans votre espace existant de gestion des compétences. Pour une première installation, ouvrez la copie du dépôt ou un autre dossier ordinaire de gestion ; un nouveau dépôt produit est inutile.
3. Donnez à Codex le chemin exact de la copie de travail. Sur Mac, sélectionnez le dossier dans Finder et appuyez sur **Option + Command + C** pour copier son chemin complet.
4. Collez le bloc ci-dessous après avoir défini votre langue préférée.
5. Examinez le rapport final d'installation et conservez son journal et l'emplacement des sauvegardes.
6. Ouvrez un nouveau chat dans le véritable projet produit pour vérifier le chargement et le fonctionnement.

```text
Installe les 33 compétences personnelles de base depuis le répertoire kit/
vérifié de cette copie d'alex-hohaizel/codex-agents. Utilise la révision de version choisie.
Ma langue de travail est le français (fr).

Ceci autorise audit → apply → verify en local, les plans exacts et les sauvegardes
pour cette suite. Lis kit/manifest.json et le --help du programme de mise à jour.
Vérifie l'intégrité du paquet. Audite les répertoires personnels et toutes les
copies projet connues. Enregistre plans et sauvegardes hors des racines de
découverte des compétences. Applique uniquement le plan exact prêt. Préserve
les modifications locales inconnues et indique les fichiers en conflit ; ne
contourne pas les contrôles de divergence.

Préserve icon_small, icon_large, brand_color, chemins et octets d'icônes existants,
y compris les anciennes références ./assets/. Vérifie avec le journal exact
renvoyé par apply. Indique canonical_core_verified, visual_preservation_verified,
les nombres updated/noop, les blocages, les échecs et les doublons.

Ne modifie ni produits, ni production, ni plugins, ni configuration d'environnement.
Vérifie ensuite séparément la découverte par l'hôte des deux constructeurs et
des directeurs App, ChatBot et Game. Ne considère pas les fichiers installés
comme preuve d'une utilisation réelle sur une tâche.
```

### Parcours Terminal pour qui souhaite les commandes exactes

Le programme de mise à jour portable nécessite Python 3.9 ou une version ultérieure et utilise la bibliothèque standard. Exécutez ces commandes depuis la racine du dépôt. L'audit lit le paquet et les emplacements d'installation, puis écrit un plan proposé. Apply effectue les changements d'installation prévus et enregistre un journal.

```bash
python3 kit/portable/update_skill_suite.py --help
python3 kit/portable/update_skill_suite.py audit --kit kit --plan ../agent-system-plan.json
python3 kit/portable/update_skill_suite.py apply --plan ../agent-system-plan.json
```

Lisez le résultat de `apply`. Copiez son chemin exact `journal` dans la commande de vérification :

```bash
python3 kit/portable/update_skill_suite.py verify --kit kit --journal /absolute/path/from-apply/journal.json
```

Le dernier chemin ci-dessus est un exemple à remplacer ; ne l'exécutez pas littéralement. Par défaut, le programme cible `~/.agents/skills` et vérifie l'ancienne racine `~/.codex/skills`. Si votre environnement utilise une autre racine personnelle prise en charge, fournissez explicitement et systématiquement `--destination` et `--legacy-root`. Consultez d'abord `audit --help`. Ajoutez `--project-root /absolute/path/to/product` pour auditer les copies locales pertinentes du produit. Le programme ne supprime pas automatiquement une copie projet qui masque une compétence personnelle.

Une installation de fichiers réussie signifie que 33 sources ont été vérifiées à la version visée, qu'il n'y a aucun blocage/échec/doublon non résolu et que `canonical_core_verified=true` et `visual_preservation_verified=true` proviennent d'une vérification utilisant le vrai journal apply. Un contrôle de hachage sans ce journal ne peut pas prouver la préservation de vos icônes existantes. Arrêtez-vous en cas de conflit et préservez le travail local ; n'utilisez pas de remplacement forcé pour que le rapport paraisse propre.

### Vérifier le chargement séparément de l'installation

Demandez à Codex ou Work dans un nouveau chat produit :

```text
Avant toute modification, identifie la source exacte chargée et la version
d'agent-foundry, design-specialist-skills et des trois directeurs produit.
Confirme quelles instructions adaptatives, de recherche, d'identité visuelle
et Work↔Codex tu as réellement lues. Indique séparément les sources indisponibles.
```

Donnez ensuite une petite tâche réelle avec une entrée connue et un critère d'acceptation. Demandez par exemple au directeur d'application d'examiner les états d'erreur d'un écran selon une exigence existante, ou à un constructeur de décrire les responsabilités d'un agent spécialisé. Cela vérifie le comportement. Cela ne certifie pas toutes les capacités produit. Conservez l'installation des fichiers, le chargement par l'hôte, l'utilisation pratique et l'acceptation produit comme résultats distincts.

## 7. Utiliser le système sur une vraie tâche

### Une tâche d'ingénierie ciblée

```text
Étudie les requêtes répétées à la base de données dans cet endpoint. Préserve
son API et son comportement métier. Lis d'abord le code et les mesures existantes.
Identifie les preuves manquantes, propose la plus petite investigation utile
et réalise une réparation justifiée dans cette branche. Vérifie la correction
et montre des mesures avant/après lorsque l'environnement le permet.
```

Cela ne nécessite ni nouvelle entreprise, ni nouveau produit, ni marque, ni étude de marché complète. Un constructeur peut concevoir un investigateur réutilisable si vous voulez conserver ce parcours sous forme d'agent durable ; pour une tâche ponctuelle, utilisez les outils et instructions pertinents existants. Le système ne doit pas fabriquer un nouvel agent uniquement parce qu'une tâche est technique.

### Une application complète

```text
BRIEF : Je veux une application pour [public] qui résout [problème]. Les
plateformes cibles sont [plateformes], le budget est [budget] et mon rôle est [rôle].
Clarifie les inconnues, étudie les alternatives réelles et prépare des options
complètes. Garde toutes mes exigences visibles dans le plan, y compris la
conception, la langue, l'assistance et la monétisation. Ne choisis pas
silencieusement un concept à ma place.
```

L'équipe doit étudier les points importants, comparer les options et identifier les obstacles de sortie ou de comptes avant un développement important. Après le choix d'un concept, conservez les références de conception sélectionnées et toutes les exigences convenues. Une première version fonctionnelle est un point de contrôle de ce plan, pas l'autorisation d'abandonner le reste.

### Un jeu mobile

```text
BRIEF : Développe des concepts distincts de jeu mobile pour [public/expérience].
Couvre les commandes et retours, les systèmes interdépendants, les ennemis,
une progression pertinente, la direction artistique, la monétisation et un
parcours de production Android/iOS réalisable. Montre des concepts visuels
comparables. Préserve l'identité choisie dans les ressources et la réalisation
jouable. Définis de véritables contrôles sur appareils.
```

Une image conceptuelle ne prouve ni animation, ni commandes tactiles, ni performance, ni reprise des sauvegardes. Le parcours de jeu doit relier la promesse visuelle choisie à des ressources sources modifiables et à une tranche jouable représentative avant de produire tout le jeu de ressources.

## 8. Work et Codex sur le même projet

Work est utile lorsque les sources nécessaires, les outils de recherche, les outils de conception et les services connectés sont disponibles. Codex est utile lorsque la copie des sources, l'environnement d'exécution, les outils de build et les intégrations locales ou appareils sont disponibles. Chaque mode peut en faire davantage lorsqu'il dispose des capacités adéquates. Choisissez selon les accès et les preuves réels, plutôt que d'attribuer toutes les tâches de réflexion à un mode et tout le code à l'autre.

Créez une identité unique pour le produit. Des noms tels que `My Product [WORK]` et `My Product [CODEX]` facilitent la navigation, mais ne prouvent pas que les deux projets contiennent le même produit. Enregistrez le dépôt, la branche, le sous-répertoire, les identifiants projet et les sources des points de contrôle. Un nouveau chat doit rester à l'intérieur de ce projet existant.

### Conserver un petit contexte partagé

Utilisez le modèle de contexte projet du dépôt ou un équivalent existant dans votre produit. Enregistrez au minimum : identifiant du projet ; dépôt et branche ; SHA complet du commit actuel ; identifiant de tâche ; étape actuelle ; langues de travail et du produit ; version de la boîte à outils et justificatif d'installation ; décisions acceptées ; source complète des exigences ; source des références de conception ; périmètre autorisé ; point de contrôle actuel ; effets ou décisions non résolus ; prochaine action. N'incluez pas d'identifiants d'accès dans ce document.

### Work → Codex local, étape par étape

1. Demandez à Work : « Poursuis cette étape dans Codex. Prépare la transmission pour ce projet existant. »
2. Work doit identifier le prochain livrable exact et les preuves nécessaires à son acceptation. Il doit enregistrer ou fournir les exigences, décisions, sources et point de contrôle pertinents.
3. Si un canal partagé autorisé est disponible, Work peut enregistrer la transmission et vérifier la révision enregistrée. Enregistrer un fichier ne prouve pas qu'une autre session Codex a démarré.
4. Ouvrez la copie de travail locale existante. S'il n'en existe pas, clonez le dépôt et la branche confirmés dans le dossier choisi. Authentifiez-vous localement pour les dépôts privés.
5. Avant d'actualiser la copie de travail, examinez-la :

```bash
git remote get-url origin
git branch --show-current
git rev-parse HEAD
git status --short
```

6. Si l'arbre de travail est propre et qu'une mise à jour de cette branche est nécessaire, utilisez `git pull --ff-only origin <confirmed-branch>` avec le vrai nom de branche. Confirmez le SHA complet obtenu. S'il existe des modifications locales ou un historique divergent, préservez-les et résolvez l'écart avant le travail qui en dépend.
7. Ouvrez le dossier exact dans l'interface de projets Codex. Pour un produit existant, utilisez son projet existant ; ajoutez le dossier via l'interface de modification du projet disponible si nécessaire.
8. Collez le bloc de transmission rempli ci-dessous. Codex confirme d'abord l'identité du dépôt, la révision, les changements locaux, les autorisations et le point de contrôle, puis réalise l'action dans le périmètre défini.
9. Conservez son rapport de résultat, ses références de commit/build et ses preuves de test pour la transmission de retour.

### Codex → Work, étape par étape

1. Demandez à Codex de préparer une transmission de résultat ou de nouvelle tâche pour le même projet existant.
2. Incluez les fichiers réellement modifiés, le SHA complet ou la révision de l'artefact, les contrôles effectués, les limites, les décisions ouvertes et la prochaine action. Précisez si les changements sont locaux, commités ou publiés.
3. Si la publication des changements convenus sur une branche nommée est autorisée, publiez uniquement ce périmètre et vérifiez la révision distante. Sinon, fournissez un artefact contrôlé via le canal disponible. Work ne peut pas automatiquement lire un chemin local Mac.
4. Ouvrez le projet Work existant, connectez le dépôt pertinent ou joignez l'artefact exact, puis collez la transmission.
5. Work lit les sources réelles et vérifie la révision d'entrée avant d'examiner ou de continuer. Il doit signaler explicitement les fichiers inaccessibles.
6. Enregistrez l'acceptation séparément de la livraison et de l'exécution. Un rapport indiquant qu'un build existe ne constitue pas l'acceptation du produit.

### Transmission à copier

Remplacez chaque champ entre crochets avant d'utiliser ce bloc :

```text
Poursuis le projet existant [identifiant/nom du projet] dans [Work/Codex].
Langue de travail : [langue/code]. Langues produit : [langues].
Dépôt : [URL]. Branche/sous-répertoire : [branche/chemin].
Révision d'entrée : [SHA complet ou révision exacte de l'artefact].
Identifiant de tâche et étape : [identifiant/étape].
Point de contrôle : [source exacte accessible].
Exigences et décisions acceptées : [sources exactes].
Références de conception et identité : [sources exactes, si pertinent].
Livrable et acceptation attendus : [résultat/contrôles concrets].
Périmètre autorisé : [ce qui peut être modifié ou publié].
Travail terminé et preuves : [faits et références].
Décisions ouvertes, blocages ou effets externes incertains : [détails/aucun].
Prochaine action : [une action concrète].

Vérifie d'abord l'identité du projet, sa révision, les outils disponibles et
les autorisations. Préserve chaque exigence et décision acceptée. Ne réinitialise
pas le produit. Distingue la transmission préparée, la livraison vérifiée,
la réception, l'exécution, le résultat et l'acceptation. Poursuis le travail
autorisé qui est réellement possible.
```

## 9. Reprendre après un chat interrompu

Ouvrez un nouveau chat dans le même projet et demandez-lui de restaurer le dernier point de contrôle vérifié. Fournissez sa source si elle n'est pas déjà accessible. Il doit rapprocher la tâche, les exigences, la révision source, les fichiers actuels et les résultats externes réels avant de continuer.

```text
Restaure cette tâche existante à partir de son dernier point de contrôle vérifié
et des sources réelles. Préserve les exigences, décisions, autorisations, résultats
terminés et effets externes incertains. Vérifie la révision actuelle et le
responsable de la prochaine action. Avant de répéter un déploiement, un paiement,
un message ou une autre action externe, vérifie si la tentative précédente
a réellement abouti. Poursuis le travail autorisé disponible et enregistre
un nouveau point de contrôle.
```

Une conversation bloquée ne prouve pas que sa dernière opération a échoué. La reprise doit vérifier le résultat réel avant de réessayer une action susceptible d'être dupliquée.

## 10. Mettre à jour les versions sans perdre un projet existant

### Lire d'abord la fiche de version

Chaque version doit expliquer ce qui a changé, les utilisateurs concernés, les prérequis, les étapes d'installation, les étapes d'adoption dans les projets, la vérification, les limites connues et le retour arrière. Le guide général doit aussi évoluer quand la procédure normale change. Ne vous fiez pas uniquement à un numéro de version.

La version commune 5.0.0 réunit les constructeurs et les trois familles sous une même version visible de suite. Elle ajoute une approche de travail adaptative commune, la recherche et la synthèse dans le domaine, la gestion de l'identité visuelle et un parcours Work↔Codex partagé. Les numéros historiques de protocoles et de schémas d'exécution restent distincts. Renommer un ancien schéma « 5.0.0 » sans véritable migration romprait la compatibilité au lieu de moderniser le projet.

### Projets existants Agent Systems 2.3 / Game 4.3

1. Enregistrez le point de contrôle actuel du projet, les exigences acceptées, les décisions, les originaux de conception, la révision source, la version de la boîte à outils et les effets externes connus.
2. Notez d'où chaque compétence ou agent projet est réellement chargé. Inventoriez les copies personnelles et locales au projet ; ne supposez pas que modifier un répertoire global change chaque projet.
3. Installez la suite cible via le parcours Work ou Codex pertinent ci-dessus. Conservez la version source et le justificatif d'installation.
4. Rouvrez le projet existant et effectuez une revue de compatibilité en lecture seule avant l'action suivante qui en dépend.
5. Demandez à son directeur ou constructeur de comparer l'état actuel du projet au nouveau parcours. Identifiez explicitement une actualisation d'état natif ou une mise à niveau de procédure uniquement si nécessaire. Préservez le comportement du produit, les choix acceptés et les effets inconnus.
6. Prévisualisez les changements exacts. Si une migration d'état est nécessaire, utilisez son outil pris en charge et son vrai `--help` ; liez la prévisualisation au hachage de l'état source, au hachage de la suite cible et à la source d'autorité. Appliquez le plan examiné et autorisé plutôt que d'inventer une approbation historique.
7. Revérifiez chaque exigence affectée et les critères d'acceptation de l'étape actuelle. Effectuez une petite tâche réelle de continuation et conservez ses preuves.
8. Enregistrez la version de la boîte à outils adoptée dans le point de contrôle produit. Conservez la fiche de migration afin que le chat suivant puisse expliquer la transition.

Game 5.0.0 contient un parcours de mise à niveau de procédure examiné pour les projets 4.2.0/4.3.0 tout en conservant le schéma d'exécution 2.0.0. Son utilisation dépend de l'état réel du projet et des entrées acceptées par l'outil. Les projets App et ChatBot nécessitent eux aussi leur propre revue d'état et de compatibilité ; ils ne doivent pas passer par une migration de jeu simplement parce que la suite partage une version commune.

### Agents déjà créés avec un constructeur

Mettre à jour le constructeur ne réécrit pas les agents qu'il a créés auparavant. Ces agents peuvent contenir des règles, outils, connaissances et une identité visuelle propres à leur projet. Inventoriez-les dans leurs projets respectifs. Comparez l'ancienne source, les modifications locales et la nouvelle source proposée. Préservez les preuves d'origine de propriété et d'installation. Si elles manquent, préparez une comparaison et un plan d'adoption explicites ; ne fabriquez pas d'ancien justificatif. Exécutez les cas de régression correspondant aux vraies responsabilités de l'agent et enregistrez séparément la version adoptée.

Le dépôt réutilisable exclut les paquets sources privés d'agents produit. La mise à jour d'un projet individuel relève des sources contrôlées et de la fiche de migration de ce projet, pas de l'installation globale de compétences de chacun.

### Préserver l'identité visuelle

Les icônes Codex existantes, leurs chemins, leur couleur et leurs octets doivent survivre aux mises à jour courantes. Une nouvelle version ne signifie pas qu'il faut redessiner une compétence ou un produit existant. Les nouvelles compétences sans identité peuvent recevoir le style système ou projet approprié. Work peut gérer lui-même un avatar de service ; distinguez son affichage hôte de l'identité Codex portable. Préservez les originaux des conceptions produit et jeu choisies, plutôt qu'une simple description verbale.

### Revenir en arrière avec précaution

Pour une installation de suite Codex, utilisez le journal exact de l'installation :

```bash
python3 kit/portable/update_skill_suite.py rollback --journal /absolute/path/from-apply/journal.json
```

Le retour arrière vérifie les sauvegardes et protège les modifications ultérieures inconnues. Il annule l'installation de compétences représentée par ce journal. Il n'annule pas une migration de données produit, un déploiement, un message, un achat ou une autre action externe. La restauration dans Work doit utiliser la procédure de gestion des compétences prise en charge et l'ancienne source enregistrée. Un retour arrière de l'état produit exige sa propre procédure de reprise examinée.

## 11. Garder les futures mises à jour complètes

À chaque future modification de la boîte à outils, mettez ce dépôt à jour avec les sources canoniques, les exigences touchées, le contenu des paquets, la fiche de version, les étapes de migration, les preuves de vérification et les changements nécessaires aux guides et traductions. Conservez les fiches des versions antérieures. Reconstruisez les paquets et métadonnées d'intégrité depuis les sources contrôlées ; évitez de publier une archive assemblée depuis un ancien cache hôte.

Exécutez les commandes de contrôle et de création des paquets selon leur `--help` actuel et la documentation de maintenance. Confirmez le commit distant après publication. « Enregistré localement », « commité », « publié », « installé », « chargé » et « adopté par un projet » sont des statuts distincts. Si un accès empêche la publication, préservez le travail terminé et indiquez la révision exacte non synchronisée.

Une règle du dépôt agit lorsqu'un futur agent la lit dans un environnement disposant des accès nécessaires. Ce n'est pas un écouteur global de tous les autres chats et ordinateurs. Commencez une future tâche de gestion des compétences en connectant ce dépôt et en lisant son `AGENTS.md`, ses exigences et sa dernière fiche de version. Un service distinct de synchronisation planifiée nécessiterait son propre environnement réel d'exécution et sa propre autorisation ; la suite n'en crée pas silencieusement.

## 12. Résolution des problèmes

| Symptôme | Prochaine vérification |
| --- | --- |
| Work ne peut pas lire le dépôt | Vérifiez le compte GitHub, l'autorisation de ce dépôt privé précis et la connexion sélectionnée ; demandez la lecture d'un fichier connu. |
| Le clone local demande une authentification | Configurez l'autorisation Git locale via le parcours d'identification de la plateforme. La connexion Work est distincte. |
| Les compétences n'apparaissent pas après enregistrement | Actualisez ou rouvrez la page Skills, puis utilisez un nouveau chat projet et vérifiez la découverte réelle des sources. |
| Deux copies de la même compétence apparaissent | Auditez les noms stables dans les racines personnelles et projet. Préservez les modifications locales et résolvez la source exacte du doublon ; ne supprimez pas les compétences sans rapport. |
| Le programme de mise à jour signale une divergence ou un conflit | Enregistrez le diff local et comparez les fichiers nommés à la source choisie. Utilisez un plan de rapprochement examiné. |
| Le contrôle des fichiers réussit mais l'agent se comporte comme avant | Vérifiez la source réellement chargée par l'hôte, puis effectuez une petite tâche ; l'intégrité des fichiers seule ne suffit pas. |
| Work ne voit pas le code modifié sur un Mac | Publiez le périmètre autorisé ou joignez un artefact exact ; un chemin local seul ne donne aucun accès. |
| Un nouveau chat a perdu des décisions | Restaurez le point de contrôle et les sources complètes des exigences avant de continuer. Actualisez le contexte enregistré. |
| La première version fonctionnelle omet une conception ou une langue convenue | Rapprochez le registre des exigences ; conservez ces exigences dans le plan et nommez leurs étapes de réalisation et d'acceptation. |
| Déploiement, soumission aux boutiques ou contrôles sur appareils sont indisponibles | Nommez le compte, l'outil, l'appareil ou l'accès précis manquant et poursuivez la préparation indépendante. N'affirmez pas que le contrôle indisponible a réussi. |
| Un agent affirme avoir lancé une autre session | Demandez une référence vérifiée de lancement/réception. Un fichier de transmission ne prouve que le statut réellement observé. |
| Vous voulez des tâches continues | Confirmez un vrai planificateur, un exécuteur, des identifiants d'accès, des contrôles de vie et une voie de reprise. L'installation des compétences ne les fournit pas. |

## 13. Documentation officielle et portée des preuves

Les interfaces de l'hôte et la disponibilité selon le compte peuvent changer. Consultez l'interface réelle et la documentation officielle actuelle lors de l'installation ou de la connexion de services. Références de comportement produit vérifiées pour ce guide le 7 novembre 2026 :

- [Build skills — ChatGPT Learn](https://learn.chatgpt.com/docs/build-skills) : structure réutilisable des compétences, découverte locale et concepts d'installation.
- [Plugins — ChatGPT Learn](https://learn.chatgpt.com/docs/plugins) : annuaire des plugins, concepts de connexion et de distribution.

Ce dépôt distribue une suite réutilisable et sa procédure d'installation contrôlée. Un plugin de place de marché publique, une licence commerciale, un environnement hébergé permanent, des outils tiers payants et des identifiants d'accès sont des livrables distincts, sauf si une version les fournit et les vérifie explicitement. Les concepts marketing illustrent les parcours et usages prévus ; les affirmations promotionnelles finales doivent correspondre aux capacités et preuves vérifiées.
