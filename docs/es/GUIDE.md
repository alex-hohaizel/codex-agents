# Guía de Codex Agent System

Resuelve una tarea concreta con Codex, desarrolla un producto con especialistas o diseña un agente reutilizable. El sistema vincula el trabajo con su fuente, una persona responsable y un resultado verificable.

[English](../en/GUIDE.md) · [Українська](../uk/GUIDE.md) · [Deutsch](../de/GUIDE.md) · [Italiano](../it/GUIDE.md) · [Español](../es/GUIDE.md) · [Français](../fr/GUIDE.md) · [简体中文](../zh-CN/GUIDE.md)

Para la primera sesión, abre el [inicio guiado](../../START_HERE.md#install-and-verify). Luego [sigue una petición durante todo el proyecto](../technical/END_TO_END.md), desde la elección del equipo hasta la revisión de la publicación. [Abre el mapa del flujo](../../assets/marketing/release-1.7/workflow-en.svg)

## Elige por dónde empezar

- **Prueba Codex.** [Instala y verifica](#install) · [Haz una primera tarea](#first-task) · [Flujos ilustrados](../../marketing/es/README.md)
- **Desarrolla u opera un proyecto.** [Elige un flujo de trabajo](#workflow) · [Encuentra una habilidad o un rol](#catalog) · [Panel para Mac](#workbench) · [Operación y recuperación](#operations)
- **Entiende el sistema.** [Harness](#harness) · [Subagentes](#subagents) · [Cápsulas de contexto](#context) · [Modelos y costes](#models)
- **Encuentra y verifica evidencias.** [Búsqueda de conocimiento (RAG)](#retrieval) · [Evaluaciones (evals)](#evals) · [Herramientas y permisos](#permissions)

[Temas técnicos (en inglés)](../OPERATING_MODEL.md#engineering-topics) · [Ejemplo práctico de RAG (en inglés)](../technical/RETRIEVAL.md) · [Requisitos del producto](../../governance/requirements.csv)

<a name="install"></a>
## Instala y verifica la detección

1. Abre la versión estable de `alex-hohaizel/codex-agents`. La instalación por terminal en macOS o Linux usa Bash, Python 3.9+, Git, una sesión autenticada de GitHub CLI (`gh`) y Codex. Puedes pedir a Codex que explique cada paso en español y mantenga exactas las opciones y rutas.
2. Sigue la instalación con atestación. El verificador comprueba la huella del paquete y la atestación de GitHub con el commit, el flujo y el manifiesto. Elige instalación nueva si no tienes la suite gestionada, o indica la versión instalada que ya verificaste. [Versión estable](https://github.com/alex-hohaizel/codex-agents/releases/latest) · [Comandos exactos](../INSTALL.md#steps)
3. Comprueba en la auditoría las 33 habilidades, el destino, la conservación de iconos y referencias y los conflictos abiertos. Aplica el plan revisado y verifica los archivos con el registro devuelto. El perfil gestionado y los doce roles tienen su propia auditoría y su registro. [Perfil y roles](../INSTALL.md#profile-and-roles)
4. Instala Orchestrator y Maintenance por separado si los necesitas. En Agent Atelier examina la vista previa de la fuente exacta, el destino y las diferencias, aplica y verifica. En Codex puedes usar el gestor de habilidades personales con la carpeta opcional completa. [Componentes opcionales](../INSTALL.md#optional-components)
5. Abre un chat nuevo de Codex en la carpeta del producto. Invoca `$agent-foundry` o la habilidad elegida. Si el entorno muestra la ruta resuelta, compárala con la fuente instalada. Comprueba el uso con una tarea de resultado visible. [Detección en Codex](https://learn.chatgpt.com/docs/build-skills#where-codex-loads-local-skills)

ChatGPT Work tiene su propia interfaz de habilidades personales. Usa el paquete de Work y verifica los registros guardados y cargados en ese entorno. La instalación local de Codex es una operación distinta. [Paquetes](../../governance/PACKAGES.md)

<a name="first-task"></a>
## Haz un primer cambio

Crea una carpeta de prueba y abre un chat nuevo de Codex allí. Guarda `# Cheklist` en `README.md` y una línea que quieras conservar en `notes.txt`. Pide en español:

```text
Corrige la ortografía del encabezado en README.md. Mantén notes.txt intacto.
Muestra el encabezado corregido y cómo verificaste ambos archivos.
```

Comprueba `# Checklist` y el contenido original de `notes.txt`. Para esta tarea basta una vía directa. Para proyectos más amplios, indica a Orchestrator el resultado, la carpeta, los cambios permitidos y un criterio observable de aceptación. Por ejemplo, pide revisar el flujo de compra, conservar el contrato de pago aprobado y devolver solo problemas reproducibles. [Primera tarea reproducible](../../START_HERE.md#install-and-verify)

<a name="workflow"></a>
## Elige el flujo y conserva el contexto

Trabaja directamente, llama a una habilidad o pide a `$atelier-orchestrator` que seleccione el camino. Un director coordina el ciclo de vida de una aplicación, chatbot o juego. `$agent-foundry` diseña un agente o equipo para trabajo recurrente. Revisa su pasaporte antes de construir y prueba el paquete preparado en una tarea original. `$design-specialist-skills` define un flujo reutilizable con activadores y casos de aceptación.

<a name="harness"></a>
### Harness y permisos

Codex proporciona el entorno de ejecución, las herramientas y los permisos. El repositorio aporta `AGENTS.md`, descripciones y recursos de habilidades, contratos de dominio, roles y comprobaciones. Confirma qué instrucciones se cargaron y aplica la autorización en la herramienta real. [Harness y permisos](../OPERATING_MODEL.md#harness-and-authority)

<a name="subagents"></a>
### Roles y subagentes

Delega resultados separados o una revisión independiente. Indica actor, revisión de la fuente, rutas de entrada, autorización de escritura, resultado, límites, condición de cierre y destino de la entrega. Asigna un único escritor al estado compartido. Recoge el resultado real antes de integrarlo. [Flujos y subagentes](../OPERATING_MODEL.md#routes-and-subagents)

Si el proyecto mantiene su registro de tareas en una proyección local de tickets, prepara y revisa el cambio de plan y aplícalo tras su aprobación. Lee el recibo registrado antes de asignar una tarea lista. Comprueba de nuevo la entrega en la sesión de Codex que recibe la tarea y guarda el resultado para una revisión independiente. [Cambio de plan aprobado y entrega de trabajo](../technical/TICKET_REPLAN.md)

Para el trabajo en paralelo, asigna worktrees de Git separados a partir del mismo commit. Guarda un punto de control cuando se interrumpa una tarea, compruébalo en la nueva sesión e integra los commits revisados en un worktree dedicado. [Coordinar los worktrees y reanudar](../technical/TICKET_WORKTREES.md)

Concilia las GitHub Issues vinculadas explícitamente con la proyección del proyecto. Encarga a un equipo de QA independiente que vincule los criterios de aceptación y las pruebas de riesgo con evidencias del candidato exacto. Si el efecto de una operación externa es incierto, compruébalo en el sistema de destino antes de decidir. [Conciliar GitHub Issues](../technical/TICKET_GITHUB.md) · [Revisar la evidencia del candidato](../technical/TICKET_QUALITY_GATE.md)

Para una decisión importante, recoge posiciones de distintos especialistas a partir de la misma evidencia. Pídeles que respondan a la objeción más relevante. La persona responsable de decidir elige el siguiente paso. [Deliberar en equipo](../../optional-skills/atelier-orchestrator/references/team-deliberation.md)

Conserva el plan original del sprint mientras cambia el backlog. Revisa las incorporaciones y dependencias antes de modificar el alcance. Comprueba los requisitos aplicables en el PRD y la arquitectura y solicita una revisión de la versión nueva. [Planificar el sprint](../technical/TICKET_TREE.md#keep-a-sprint-plan-while-the-backlog-changes) · [Revisar la especificación](../technical/TICKET_PRODUCT_SPEC.md)

Continúa una lluvia de ideas o la evaluación de una propuesta en otra sesión a partir del registro guardado. Prepara un resumen, un PRFAQ o documentos de diseño y experiencia separados, con sus fuentes y decisiones pendientes. Revisa las habilidades y roles importados antes de prepararlos en un proyecto nuevo de Codex. Para una incidencia de GitHub vinculada, revisa el cambio propuesto y consulta el resultado antes de repetirlo. [Taller](../technical/WORKSHOP.md) · [Facilitación de producto](../technical/PRODUCT_FACILITATION.md) · [Importación con Foundry](../technical/CONSTRUCTOR_IMPORT.md) · [Cambios en GitHub](../technical/TICKET_GITHUB.md#apply-a-reviewed-change-to-a-mapped-issue)

Crea un prototipo interactivo en el navegador a partir de DESIGN y EXPERIENCE revisados o vincula borradores, revisiones e inspecciones a fuentes exactas mediante el registro de plantillas. Audita un módulo BMad y prepara una migración revisada en un directorio nuevo. Para el árbol de tareas, concilia un efecto tras comprobar el estado local, previo y remoto. [Prototipo UX](../technical/UX_PROTOTYPE.md) · [Plantillas](../technical/DOCUMENT_TEMPLATES.md) · [Migración de BMad](../technical/BMAD_MODULE_MIGRATION.md) · [Árbol del gestor](../technical/TRACKER_SYNC.md) · [Proveedores](../technical/TRACKER_PROVIDERS.md)

<a name="context"></a>
### Cápsulas de contexto

Abre los requisitos autorizados, la identidad, las decisiones y el punto de control. Fija las huellas exactas e incluye requisitos aplicables, efectos permitidos, trabajo aplazado, resultado, efectos pendientes y próxima acción. Si una fuente cambia o falta, vuelve a verificar la obligación afectada. El traspaso lleva esta selección a otra tarea o entorno y conserva la autoridad de las fuentes originales.

Registra `preferred_language` en el contexto y transmítelo al traspasar trabajo. Conserva comandos, selectores, identificadores, referencias y citas exactas. [Modelo operativo](../OPERATING_MODEL.md#project-context-and-handoffs) · [Contexto de proyecto](../../templates/project-context.json) · [Traspaso](../../templates/HANDOFF.md)

<a name="models"></a>
### Modelos y costes

Al comparar flujos, registra el modelo, el nivel de razonamiento y el resultado. Usa una variante de menor coste si supera las mismas comprobaciones de aceptación con los mismos datos de entrada. [Selección de modelos y costes](../OPERATING_MODEL.md#models-and-cost)

<a name="retrieval"></a>
## Añade búsqueda de conocimiento y RAG

Empieza con rutas verificadas, identificadores precisos, consultas estructuradas y búsqueda léxica. Añade generación aumentada por recuperación cuando cuesta encontrar pruebas relevantes de forma repetida. Compara búsqueda léxica, semántica e híbrida en el mismo corpus autorizado antes de elegir índice o almacén vectorial. Mide resultados pertinentes, fidelidad de citas, casos sin respuesta, varios idiomas, fuentes revocadas o desactualizadas, proyectos privados cercanos, latencia y coste. Conserva permisos y revisión de origen por fragmento, comprueba derechos antes de buscar y citar, y permite borrado o reconstrucción. El texto encontrado aporta datos. La autoridad procede del proyecto y de las herramientas reales.

Usa `$chatbot-atelier-knowledge` para preparar corpus, recuperación, respuestas fundamentadas y mantenimiento. DATA, ANALYSIS, LLM, PREDICTION, ADAPTATION, MEDIA y EVALUATION son perfiles para las tareas pertinentes. Escoge el mínimo necesario y verifica el resultado en su consumidor real. [Guía técnica de recuperación](../OPERATING_MODEL.md#retrieval-and-rag) · [Perfiles de IA y datos](../../standards/ai-production.md)

<a name="evals"></a>
## Evalúa comportamiento y evidencia

Fija entradas representativas, revisión, modelo, entorno, resultado esperado, fallos y límites de tiempo o coste. Prueba invocación explícita y selección natural, peticiones cercanas, accesos denegados, fuentes desactualizadas y recuperación. Verifica el artefacto exacto en su destino de uso. Registra por separado estructura, comportamiento nativo, recibos y aceptación independiente. Guarda solicitudes originales y rutas privadas en el material aislado de prueba.

Desde la raíz del repositorio, ejecuta una comprobación pequeña real con Codex CLI y una sesión compatible:

```bash
receipt_dir="$(mktemp -d)"
python3 -B evaluations/native_canary.py --case p01-direct --output "$receipt_dir/direct.jsonl"
```

La comprobación corrige la errata prevista en un proyecto temporal y comprueba el otro archivo. El conjunto también cubre un traspaso de alcance limitado, un pasaporte aprobado y el primer uso de una habilidad generada. Las afirmaciones sobre productos externos requieren pruebas en su entorno real. [Evaluaciones, datos y recibos](../../evaluations/README.md) · [Validación](../../governance/VALIDATION.md)

<a name="workbench"></a>
## Usa Agent Atelier en Mac

1. Abre el código actual y compila con el archivo de bloqueo de Node.js. Desde `apps/agent-atelier/` ejecuta:

```bash
npm ci --ignore-scripts
npm run build
node launcher/atelier.mjs start
node launcher/atelier.mjs status
node launcher/atelier.mjs doctor
```

2. Busca el proyecto en el panel local y comprueba la cobertura indicada. Algunos proyectos registrados en Codex aparecen sin chats. El historial y los artefactos se cargan al abrirlos. Revisa la carpeta exacta y vincúlala de forma explícita. El modo de demostración usa registros ficticios.
3. Abre el elemento y su siguiente acción documentada. Transfiérela al formulario y comprueba objetivo, aceptación, entradas, permisos, habilidades y ruta de Orchestrator. Prepara la tarea. Inicia solo el trabajo autorizado y verifica el resultado y el recibo. Reanuda un chat existente si se admiten su identidad y su contexto y el escritor está libre. Si el contexto no se puede recuperar, prepara una tarea nueva acotada.
4. En Conexiones, inspecciona aplicaciones, plugins y conectores. Si el entorno lo admite, el panel consulta documentación oficial de OpenAI, previsualiza y descarga un PNG de Codex, busca imagen y audio en Openverse con origen y licencia y lee metadatos de repositorios con una sesión GitHub CLI existente. Usa operaciones que admitan el entorno y la cuenta reales. [Guía del panel](../../apps/agent-atelier/README.md) · [API y conexiones](../../apps/agent-atelier/shared/API.md)

<a name="operations"></a>
## Opera, recupera y actualiza

<a name="permissions"></a>
### Herramientas y permisos

Antes de escribir con una herramienta comprueba operación, destino, autorización, coste, límites y recibo esperado. Si se agota el tiempo o falta un recibo, consulta el estado autorizado de la solicitud exacta. Repite la acción con autorización vigente y protección comprobada contra duplicados. Deja visibles los efectos pendientes y la evidencia. Evalúa el resultado en el producto real y registra de forma separada preparación, ejecución y creación de archivos. [Efectos de las herramientas y evidencias](../OPERATING_MODEL.md#tools-evidence-and-recovery)

### Recuperación y actualizaciones

Usa el paquete estable y su plan para actualizar componentes. Guarda los registros y los datos existentes. Tras una interrupción, examina el destino real antes de continuar. Revierte núcleo, perfil y habilidad opcional con sus registros respectivos. Haz una copia del panel y su base de datos según la guía, reinicia en el directorio de datos establecido y verifica proyectos y una tarea acotada. Los datos de producto, los chats nativos y las cuentas tienen propietarios y rutas de recuperación propios. [Instalación y recuperación](../INSTALL.md#rollback) · [Continuar trabajo](../../governance/RESUMABLE_WORK.md)

<a name="catalog"></a>
## Elige una habilidad o familia de productos

| Selector | Úsalo para empezar |
| --- | --- |
| `$atelier-orchestrator` | Seleccionar, continuar y coordinar el flujo de trabajo |
| `$agent-foundry` | Diseñar un agente o equipo para una tarea recurrente real |
| `$design-specialist-skills` | Diseñar una habilidad concreta o una familia reutilizable |
| `$app-atelier-director` | Investigación, conceptos, especificación, UX, desarrollo, soporte, crecimiento, QA, publicación y operación de una aplicación |
| `$chatbot-atelier-director` | Público y canales, producto, conversación, conocimiento, integraciones, multimedia, desarrollo, QA, publicación y operación |
| `$gamedev-director` | Estudio, conceptos, preproducción, recursos, desarrollo, QA, publicación y operación de un juego |
| `$codex-agents-maintenance` | Cambios autorizados de habilidades y guías, verificación y paquetes de publicación |

### Inventario completo de especialistas y roles

**Equipo de aplicaciones**

- [`$app-atelier-director`](../../kit/skills/app-atelier-director/SKILL.md) · Dirección del ciclo de vida
- [`$app-atelier-research`](../../kit/skills/app-atelier-research/SKILL.md) · Investigación de usuarios y mercado
- [`$app-atelier-concepts`](../../kit/skills/app-atelier-concepts/SKILL.md) · Conceptos de producto
- [`$app-atelier-specification`](../../kit/skills/app-atelier-specification/SKILL.md) · Requisitos y contratos
- [`$app-atelier-experience`](../../kit/skills/app-atelier-experience/SKILL.md) · Experiencia y accesibilidad
- [`$app-atelier-build`](../../kit/skills/app-atelier-build/SKILL.md) · Implementación
- [`$app-atelier-growth`](../../kit/skills/app-atelier-growth/SKILL.md) · Adquisición
- [`$app-atelier-support`](../../kit/skills/app-atelier-support/SKILL.md) · Flujo de soporte
- [`$app-atelier-qa`](../../kit/skills/app-atelier-qa/SKILL.md) · Revisión independiente de calidad
- [`$app-atelier-release`](../../kit/skills/app-atelier-release/SKILL.md) · Publicación
- [`$app-atelier-operations`](../../kit/skills/app-atelier-operations/SKILL.md) · Operación

**Equipo de chatbot**

- [`$chatbot-atelier-director`](../../kit/skills/chatbot-atelier-director/SKILL.md) · Dirección del ciclo de vida
- [`$chatbot-atelier-research`](../../kit/skills/chatbot-atelier-research/SKILL.md) · Investigación de usuarios y canales
- [`$chatbot-atelier-specification`](../../kit/skills/chatbot-atelier-specification/SKILL.md) · Contratos de comportamiento y estado
- [`$chatbot-atelier-conversation`](../../kit/skills/chatbot-atelier-conversation/SKILL.md) · Diseño de diálogos
- [`$chatbot-atelier-knowledge`](../../kit/skills/chatbot-atelier-knowledge/SKILL.md) · Conocimiento y recuperación
- [`$chatbot-atelier-integrations`](../../kit/skills/chatbot-atelier-integrations/SKILL.md) · Integraciones y recibos
- [`$chatbot-atelier-media`](../../kit/skills/chatbot-atelier-media/SKILL.md) · Multimedia
- [`$chatbot-atelier-build`](../../kit/skills/chatbot-atelier-build/SKILL.md) · Implementación
- [`$chatbot-atelier-qa`](../../kit/skills/chatbot-atelier-qa/SKILL.md) · Revisión de calidad
- [`$chatbot-atelier-release`](../../kit/skills/chatbot-atelier-release/SKILL.md) · Publicación
- [`$chatbot-atelier-operations`](../../kit/skills/chatbot-atelier-operations/SKILL.md) · Operación y recuperación

**Equipo de videojuegos**

- [`$gamedev-director`](../../kit/skills/gamedev-director/SKILL.md) · Dirección del ciclo de vida
- [`$gamedev-studio`](../../kit/skills/gamedev-studio/SKILL.md) · Práctica de estudio
- [`$gamedev-concepts`](../../kit/skills/gamedev-concepts/SKILL.md) · Conceptos jugables
- [`$gamedev-preproduction`](../../kit/skills/gamedev-preproduction/SKILL.md) · Sistemas y planificación
- [`$gamedev-assets`](../../kit/skills/gamedev-assets/SKILL.md) · Producción de recursos
- [`$gamedev-build`](../../kit/skills/gamedev-build/SKILL.md) · Implementación del juego
- [`$gamedev-qa`](../../kit/skills/gamedev-qa/SKILL.md) · Revisión de calidad
- [`$gamedev-release`](../../kit/skills/gamedev-release/SKILL.md) · Publicación
- [`$gamedev-liveops`](../../kit/skills/gamedev-liveops/SKILL.md) · Operación en vivo

**Roles especializados de Codex**

- [`foundry-architecture`](../../agent-profiles/foundry-architecture.toml) · Arquitectura
- [`foundry-backend`](../../agent-profiles/foundry-backend.toml) · Backend
- [`foundry-conversation`](../../agent-profiles/foundry-conversation.toml) · Diálogos
- [`foundry-cost`](../../agent-profiles/foundry-cost.toml) · Costes
- [`foundry-integrations`](../../agent-profiles/foundry-integrations.toml) · Integraciones
- [`foundry-judge`](../../agent-profiles/foundry-judge.toml) · Evaluación independiente
- [`foundry-platform`](../../agent-profiles/foundry-platform.toml) · Plataformas de destino
- [`foundry-privacy`](../../agent-profiles/foundry-privacy.toml) · Privacidad
- [`foundry-product`](../../agent-profiles/foundry-product.toml) · Producto
- [`foundry-qa`](../../agent-profiles/foundry-qa.toml) · Calidad
- [`foundry-reliability`](../../agent-profiles/foundry-reliability.toml) · Fiabilidad
- [`foundry-skeptic`](../../agent-profiles/foundry-skeptic.toml) · Revisión crítica

El catálogo incluye todas las habilidades por su nombre estable y los doce roles. [Catálogo completo](../CAPABILITIES.md#all-skills-and-roles) · [Ejemplos visuales](../../marketing/es/README.md) · [Otros idiomas](../../START_HERE.md#use-another-language)
