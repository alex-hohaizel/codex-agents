# Agent System — la guía completa de Work + Codex

[English](../en/GUIDE.md) · [Українська](../uk/GUIDE.md) · [Deutsch](../de/GUIDE.md) · [Italiano](../it/GUIDE.md) · [Español](../es/GUIDE.md) · [Français](../fr/GUIDE.md) · [中文](../zh-CN/GUIDE.md)

**Versión de referencia de la guía:** Agent System 6.0.0, 9 de noviembre de 2026. **Suite reutilizable:** 33 habilidades. Esta guía abarca una instalación nueva, el trabajo diario, compartir un proyecto entre Work y Codex y actualizar un proyecto existente. Las revisiones de la documentación y los paquetes del repositorio pueden cambiar sin modificar la versión de las habilidades subyacentes; consulta el registro de la versión antes de actualizar.


**Candidato de fuentes preparado:** repositorio **1.4.0-rc.1**, core **6.1.0**, Atelier Orchestrator opcional **1.2.0**, mantenimiento opcional **1.1.0**, Agent Atelier local **0.3.0**. No es la versión final 1.4.0 ni un comprobante de instalación. Antes de una actualización admitida, lea [la migración 6.1](../../releases/migrations/6.1.0.md). La campaña anterior 1.1.0 permanece sin cambios: [publicidad en inglés](../../marketing/campaign/README.md) y [publicidad en ucraniano](../../marketing/campaign/README.uk.md), diez materiales por idioma. La publicidad es EN/UK; las guías y la interfaz del servicio cubren los siete idiomas anunciados. La auditoría, actualización, instalación y control reales de Work siguen siendo una tarea separada en el entorno correspondiente; un archivo de fuentes o una conexión al repositorio no es un comprobante de instalación.

**El pasaporte 0.2 está aprobado para implementación.** Las 17 capacidades, R01–R27 y A01–A29 siguen incluidas con las mismas 35 fuentes reutilizables y 12 roles. Prioridad al contexto, diseño profesional y panel operativo. Se han ejecutado verificaciones reales acotadas de contexto/UI/Codex; no completan todos los casos íntegros, demuestran entrenamiento de modelos ni constituyen aceptación del propietario. Toda regresión confirmada impide la adopción; las pruebas necesarias ausentes siguen pendientes. Consulte [el estado de implementación](../evolution/2026-11-10/IMPLEMENTATION.en.md). Instalación final, adopción operativa, publicación y CI son hechos separados. WORK sigue aplazado. La documentación detallada es EN/UK.

## 0. Actualizar a 6.1 y abrir el espacio operativo local

Los comandos siguientes describen procedimientos compatibles. Aplique solo el candidato exacto admitido para el alcance previsto tras verificar la conservación; las fuentes preparadas no indican que deba reemplazarse una instalación o servicio activo.

1. Selecciona un commit exacto y verificado de la versión. Conserva las fuentes actuales de las 33 competencias, los archivos/vínculos/colores/clases de los iconos, los cambios locales y los registros de propiedad. Guarda los requisitos del proyecto, identidad/persona aceptadas, decisiones, permisos, tareas pendientes y efectos inciertos. La instalación no migra un producto.
2. Desde `kit/`, lee la ayuda del actualizador portátil y audita el candidato exacto. Antes de apply, examina las 33 entradas, los conflictos y la conservación visual. Mantén planes y copias fuera de las carpetas de detección de competencias.

```bash
python3 portable/update_skill_suite.py --help
python3 portable/update_skill_suite.py audit --kit . --plan /absolute/agent-system-plan.json
python3 portable/update_skill_suite.py apply --plan /absolute/agent-system-plan.json
python3 portable/update_skill_suite.py verify --kit . --journal /actual/apply/journal.json
```

3. Sustituye el marcador del registro únicamente por la ruta real devuelta por apply. Las diferencias desconocidas deben aclararse; no fuerces la sobrescritura. Verifica por separado la detección/carga real de fuentes y una tarea acotada. Se conservan los iconos existentes y las competencias ajenas al cambio.
4. Audita el perfil del entorno Codex por separado desde la raíz del repositorio: `python3 scripts/install_host_profile.py audit --plan /absolute/host-plan.json`. Aplica con `apply --plan /absolute/host-plan.json --journal /absolute/host-journal.json` y después verifica con `verify --journal /absolute/host-journal.json`. El bloque gestionado conserva las instrucciones globales existentes; los doce roles acotados mantienen sus modelos y restricciones de efectos externos. La carga en un entorno real se verifica por separado.
5. Instala el componente opcional `atelier-orchestrator` mediante el gestor de competencias compatible desde `optional-skills/atelier-orchestrator` en el commit seleccionado. Es independiente del actualizador de las 33 competencias de base; la presencia de fuentes no demuestra instalación ni ejecución correcta. La competencia de mantenimiento existente sigue siendo opcional y separada.

Atelier Orchestrator 1.2.0 es el punto de entrada único opcional: describe el resultado una vez y elegirá ejecución directa, un especialista existente, un agente del proyecto, un director, coordinación de componentes o Foundry. Las solicitudes sencillas siguen siendo sencillas. Un solo brief y los permisos existentes acompañan el trabajo. Después de crear, verificar y detectar un agente del proyecto en el entorno, recomienda continuar mediante él y mantiene ese vínculo cuando vuelves al orquestador. La creación del agente y la tarea de producto original tienen aceptaciones distintas; un paquete de agente no completa el producto solicitado.

Las solicitudes de mejorar o reescribir el propio orquestador, una competencia, constructor, familia o agente existente siguen una ruta de mantenimiento: leer fuentes y ajustes reales, revisar el impacto y las diferencias, conservar identidad y cambios locales, guardar la copia anterior y verificar el resultado guardado. La vista previa de una ruta y el comprobador de routing opcional no certifican idoneidad temática, consentimiento humano, ejecución ni calidad. Las invocaciones directas de las competencias existentes siguen disponibles.

Agent Atelier 0.3.0 es el candidato de fuentes de la aplicación/servidor local independiente, abierto con su propio lanzador. La competencia no es un proceso en segundo plano y la aplicación no es una entrada de la lista de competencias. Sus versiones son independientes. Se conservan el SVG original, los vínculos PNG y el color de marca. El core 6.1.0 añade métodos compatibles; no reinicia el producto ni adopta nuevas reglas automáticamente. Lea [actualización y reversión 6.1](../../releases/migrations/6.1.0.md). Compruebe la versión realmente activa con status/doctor; una instancia existente puede permanecer en su versión anterior hasta una sustitución verificada.

6. Para compilar el servicio local desde las fuentes, usa el archivo de bloqueo fijado con Node.js 24.22.2 o una versión posterior compatible. Desde `apps/agent-atelier/`, ejecuta lo siguiente. La primera instalación de dependencias requiere acceso a la red, sin implicar un nuevo servicio de pago.

```bash
npm ci --ignore-scripts
npm run build
node launcher/atelier.mjs start
node launcher/atelier.mjs status
node launcher/atelier.mjs doctor
node launcher/atelier.mjs stop
```

7. En Mac, tras compilar, `apps/agent-atelier/launcher/Agent Atelier.command` permite iniciar con doble clic. El lanzador abre loopback, reutiliza su propia instancia activa y no habilita el inicio automático al acceder al sistema. Selecciona y previsualiza una raíz de proyecto concreta y después vincúlala. La vinculación descubre el proyecto en solo lectura: no adopta el nuevo método en el producto ni autoriza todas las tareas futuras. La demostración contiene datos ficticios y no ejecuta comandos.

En el panel, busca el trabajo Codex disponible y comprueba la cobertura del historial indicada. Los proyectos y trabajos se agrupan a partir del historial nativo real y los registros de fuentes, incluido el trabajo disponible iniciado directamente en Codex; no es un escaneo de la carpeta Home ni permiso para asumir otro proceso de escritura. Conecta la carpeta exacta del proyecto para obtener contexto y continuar. El mapa de trabajo distingue respuestas recibidas, resultados registrados en fuentes y resultados aceptados. El objetivo y la aceptación registrada conservan su fuente; una propuesta no es aprobación, la mención de una competencia no es ejecución y un agente planificado no está instalado. Describe el siguiente resultado mediante la entrada única, revisa la ruta propuesta y después prepara e inicia la tarea delimitada. Los chats existentes requieren un traspaso compatible cuando estén inactivos; los cambios protegidos del estado nativo usan el controlador revisado en lugar de escrituras arbitrarias de archivos.

El historial nativo no es el registro de proyectos vacíos de la aplicación; conecta explícitamente un proyecto sin historial disponible. Para la competencia opcional conocida de orquestación o mantenimiento del repositorio, elige **Revisar esta actualización de la competencia** en el catálogo, comprueba los cambios exactos de la fuente, la conservación, los conflictos y el plan de la copia anterior, y aplica solo la actualización lista y revisada. Verifica el registro real y actualiza por separado la detección del entorno. La reversión restaura la copia anterior gestionada exacta y rechaza cambios posteriores desconocidos. Estas operaciones sobre fuentes opcionales no actualizan las 33 competencias de base ni migran productos.

Las conversaciones nativas de Codex existentes se pueden consultar en la cartera mediante un acceso específico al historial de solo lectura. El ejecutor aislado no puede reanudar una conversación inactiva si no puede restaurar allí su contexto guardado. En ese caso, prepare una nueva tarea de proyecto con límites definidos a partir de fuentes revisadas, o continúe la conversación existente en un entorno nativo de Codex capaz de restaurar su contexto. El acceso a los metadatos o al historial de una conversación no garantiza un contexto utilizable para la ejecución. Se mantiene el aislamiento de la ejecución; no se realiza ninguna migración de las bases de datos nativas.

8. Prepara una tarea con ámbito, entradas, aceptación y límites exactos y ejecútala mediante el adaptador Codex compatible. Fuente, calidad del trabajo, integración, dispositivo, revisión independiente y aceptación del propietario son estados distintos. La cancelación solo se confirma tras el resultado real del entorno. Los chats existentes necesitan identidad/cwd exactos y una transferencia en reposo; el control del servicio no bloquea otro cliente de escritorio que escribe. Concilia un efecto incierto antes de reintentar. Durante la preparación de la tarea, el servicio registra las fuentes exactas de AGENTS que la rigen, su orden de prioridad o su ausencia confirmada, y los ajustes con los que el propio Codex carga las instrucciones. Comprueba que estos registros coincidan con las fuentes de instrucciones realmente cargadas y los vuelve a comprobar antes de una llamada al modelo. Si estas entradas cambian o una tarea anterior carece de estos registros, debe prepararse de nuevo; se conservan su historial y los archivos nativos del producto.
9. Las sesiones Foundry existentes usan `suite-update-plan` y un registro revisado `refresh --accept-suite-update` con huellas exactas del estado de origen y del destino. App state/1 no necesita migración de formato por el toolkit. Las pruebas de integración Chat necesitan referencias actuales al objeto del contrato y una nueva observación real; las pruebas antiguas no se completan retroactivamente. Game usa la actualización de flujo 5→6 compatible y mantiene runtime2/model4/handoff1. Los agentes generados necesitan comparación origen-destino y continuación sin historial oculto; ningún proyecto se reinicia.
10. La copia y restauración del servicio afecta solo a su estado: previsualiza y valida la copia exacta, concilia los trabajos y conserva las revocaciones de permisos; no restaura bases de datos de productos ni efectos externos. El rollback de competencias usa el registro real del actualizador; el del perfil de entorno usa su propio registro y rechaza cambios posteriores. La instalación y el control reales de WORK siguen aplazados. Lee la [migración detallada](../../releases/migrations/6.1.0.md) y la [guía del servicio](../../apps/agent-atelier/README.md) para recuperación y límites compatibles.

## 0.1. Qué añade el candidato y cuándo utilizarlo

El contexto procede de los requisitos, decisiones, identidad y checkpoints nativos del proyecto. Las competencias directas pueden compilar una proyección explícita con el asistente portátil; el panel compila por separado su paquete JavaScript de tarea. Las declaraciones opcionales `atelier.context-bindings/1` comprueban hashes de fuentes, identidad del proyecto, ID esperados, requisitos obligatorios y extractos literales. Las fuentes necesarias ausentes o modificadas bloquean la preparación dependiente. Los proyectos sin declaración conservan la ruta anterior con cobertura sin verificar. Ninguna ruta guarda automáticamente cada palabra ni ofrece un índice global de embeddings. RAG es búsqueda condicional para una necesidad de conocimiento demostrada, no la autoridad del estado actual de la tarea.

Active solo la responsabilidad necesaria DATA, ANALYSIS, LLM, PREDICTION, ADAPTATION, MEDIA o EVALUATION bajo el responsable existente. No hay siete nuevas competencias instaladas, trabajadores permanentes ni frameworks obligatorios. Trece tipos opcionales de artefacto describen los registros pertinentes de datos, modelos, ejecución, evaluación y lotes. El asistente de solo lectura comprueba estructura declarada, referencias locales, límites de fuga/reintento y contabilidad; no obtiene datos, entrena modelos, certifica calidad ni inicia trabajos de proveedores. Desde la raíz del repositorio, lea primero la ayuda de los asistentes reales:

```bash
python3 -B standards/context_capsule.py --help
python3 -B standards/ai_production.py --help
```

Los nuevos paquetes de agentes generados para 6.1 incluyen 15 recursos operativos comunes y siete enlaces locales a instrucciones. Los paquetes 6.0 existentes conservan su contrato exacto de doce recursos, y los 5.x de ocho; no se certifican retroactivamente como 6.1. Actualice un agente mediante comparación fuente→destino, conserve sus reglas de dominio, identidad, ajustes y cambios desconocidos, y verifique después la continuación sin historial y una tarea original acotada. Instalar el toolkit no equivale a adopción por el proyecto.

El panel muestra requisitos legibles, decisiones actuales, trabajo aplazado y comprobaciones de fuentes. «Estado en la fuente» conserva el texto del registro y no sustituye una decisión actual posterior. Las conversaciones grandes usan páginas separadas y acotadas de turn/item, con continuación y cobertura incompleta visibles. La carga y las lecturas fallidas tienen estados y recuperación explícitos. Instalado, detectado por el host, conectado, ejecutado y aceptado por el propietario son hechos distintos. El [manual de componentes](../evolution/2026-11-10/IMPLEMENTED-COMPONENTS.en.md) y el [caso real de comentarios](../evolution/2026-11-10/REVIEW-STUDY.en.md) explican fuentes, activación, destinatarios y límites.

## 1. Qué te ofrece

Describe un resultado con palabras cotidianas. El sistema ayuda a convertirlo en una tarea concreta, incorpora las especialidades pertinentes, mantiene juntas las decisiones y los requisitos y comprueba el resultado frente al objetivo acordado.

Por ejemplo, «Ayúdame a reducir la carga de la base de datos en este backend» puede convertirse en una investigación centrada en consultas, límites de transacciones, caché, mediciones de rendimiento y un cambio probado. «Crea una aplicación móvil para este público» necesita un recorrido más amplio: investigación, decisiones de producto, diseño, arquitectura, implementación, controles de calidad, preparación del lanzamiento y operación. Una reparación pequeña debe seguir siendo una reparación pequeña. Un producto completo debe conservar todos sus requisitos, incluidas las partes previstas para después de la primera versión funcional.

Una **habilidad** es un conjunto reutilizable de instrucciones de trabajo, referencias y, en ocasiones, scripts. Un **agente** aplica un papel y esas instrucciones a una tarea. Un **director** coordina una familia de productos. Un **constructor** diseña un agente especializado o un conjunto reutilizable de habilidades cuando las familias existentes no cubren el trabajo. Funcionan mediante ChatGPT o Codex y las herramientas realmente disponibles en ese entorno. Instalar instrucciones no crea un servidor en ejecución, compra servicios, concede permisos sobre repositorios ni pone en marcha un proceso permanente en segundo plano.

El valor está en el flujo de trabajo organizado: un brief compartido, requisitos explícitos, especialistas pertinentes, decisiones conservadas, traspasos verificables y una forma de reanudar el trabajo. El repositorio no afirma una superioridad medida, ingresos garantizados, aceptación garantizada en las tiendas ni preparación automática para producción.

## 2. Elige por dónde empezar

| Tu situación | Empieza con | Una primera petición útil |
| --- | --- | --- |
| Quieres una sola entrada para una tarea, proyecto o mejora del sistema | `atelier-orchestrator` | «Este es el resultado que necesito. Recupera el contexto del proyecto, elige las competencias disponibles adecuadas y completa el trabajo acordado». |
| Quieres un agente especializado adaptado a un trabajo recurrente | `agent-foundry` | «Crea un agente que investigue problemas de rendimiento en nuestros servicios Go. Primero aclara sus responsabilidades, pruebas y accesos.» |
| Quieres una habilidad reutilizable o una familia coordinada de habilidades | `design-specialist-skills` | «Diseña un flujo de revisión reutilizable para nuestras integraciones basadas en eventos, incluida la recuperación ante fallos.» |
| Quieres desarrollar una aplicación o un producto existente | `app-atelier-director` | «Continúa esta aplicación desde su checkpoint. Conserva sus requisitos aceptados e identifica el siguiente resultado útil que entregar.» |
| Quieres un chatbot, un bot de soporte o un compañero de conversación | `chatbot-atelier-director` | «Diseña un bot para este público y estos canales, incluidos su idioma, memoria, acciones y costes operativos.» |
| Quieres un juego móvil o continuar uno existente | `gamedev-director` | «Desarrolla conceptos de juego en torno a esta experiencia, con controles significativos, progresión y una vía de producción viable.» |
| Ya conoces la fase exacta | El especialista pertinente que aparece abajo | «Revisa esta pantalla de pago frente al diseño aprobado y los criterios de aceptación.» |

No tienes que memorizar los 33 nombres. Usa un director para un producto o un constructor para un nuevo flujo especializado. También puedes solicitar explícitamente una habilidad desde el selector de habilidades del entorno. En Work la forma habitual es `@skill-name`; en Codex es `$skill-name`. Los selectores disponibles y los nombres mostrados pueden variar entre versiones del entorno. Cuando necesites certeza, pide que se muestre la fuente exacta cargada.

### El catálogo completo

#### Dos constructores

| Habilidad | Qué te ayuda a producir |
| --- | --- |
| `agent-foundry` | Un agente especializado o una familia coordinada de agentes, definidos en torno a un dominio real, responsabilidades, herramientas, conocimientos, controles y una vía operativa viable. Su primer cometido es diseñar el agente, en lugar de ejecutar sin indicarlo el futuro proyecto del agente. |
| `design-specialist-skills` | Habilidades reutilizables y familias de habilidades para una tarea definida: especialidades adecuadas, criterios de calidad, referencias, herramientas y secuencia de trabajo. |

#### Equipo de aplicaciones — 11 habilidades

| Habilidad | Qué hace en palabras sencillas |
| --- | --- |
| `app-atelier-director` | Mantiene coherente el proyecto de la aplicación desde la primera idea hasta el desarrollo y la operación. |
| `app-atelier-research` | Investiga usuarios, necesidades, alternativas y pruebas del mercado antes de que el equipo invierta en una dirección de producto. |
| `app-atelier-concepts` | Compara opciones de producto completas: utilidad, experiencia, modelo de negocio, costes y alcance realista. |
| `app-atelier-specification` | Convierte el producto elegido en requisitos precisos y contratos de comportamiento, datos, API, autenticación y pagos. |
| `app-atelier-experience` | Crea y comprueba la marca, pantallas, estados, incorporación de usuarios, accesibilidad, localización y materiales de diseño para producción. |
| `app-atelier-build` | Implementa los clientes Android, iOS y web acordados, el backend y las integraciones necesarias, con compilaciones reproducibles. |
| `app-atelier-support` | Diseña e implementa el bot de soporte del producto y el flujo de conocimientos, incluidas la escalación y las acciones controladas. |
| `app-atelier-qa` | Comprueba de forma independiente requisitos, diseño, implementación, pagos, privacidad, recuperación y preparación del lanzamiento cuando hay un actor independiente disponible. |
| `app-atelier-release` | Comprueba pronto la viabilidad del lanzamiento y después prepara firmas, fichas de las tiendas, despliegues, recibos y reversión dentro del alcance autorizado. |
| `app-atelier-growth` | Evalúa y prepara canales de adquisición pertinentes, contenido y medición, y después activa una vía autorizada cuando el producto está listo. |
| `app-atelier-operations` | Gestiona incidentes, métricas del producto, casos de soporte, costes, copias de seguridad, cambios y operación continua. |

#### Equipo de chatbot — 11 habilidades

| Habilidad | Qué hace en palabras sencillas |
| --- | --- |
| `chatbot-atelier-director` | Coordina todo el ciclo de vida de un bot y conserva sus capacidades existentes al reanudar el trabajo. |
| `chatbot-atelier-research` | Investiga el público, el ámbito temático, las restricciones de las plataformas, las integraciones y la viabilidad práctica. |
| `chatbot-atelier-specification` | Define las reglas, estado, datos, herramientas, eventos, errores, privacidad y criterios de aceptación del bot. |
| `chatbot-atelier-conversation` | Desarrolla su idioma, carácter, preguntas útiles, iniciativa, botones y comportamiento en conversaciones personales o de grupo. |
| `chatbot-atelier-knowledge` | Diseña fuentes de conocimiento y memoria con ámbitos definidos, recuperación de información cuando resulte útil, correcciones, caducidad, eliminación y privacidad. |
| `chatbot-atelier-integrations` | Construye adaptadores de plataformas, callbacks, herramientas, tareas programadas y acciones externas fiables con recuperación y pruebas de entrega. |
| `chatbot-atelier-media` | Crea e integra la identidad visual, imágenes, animación, audio y voz del bot mediante las herramientas disponibles. |
| `chatbot-atelier-build` | Implementa el bot completo acordado, incluidos el runtime necesario y el trabajo de integración en producción. |
| `chatbot-atelier-qa` | Comprueba conversación, conocimientos, privacidad, acciones, medios, runtime y escenarios negativos frente a pruebas reales. |
| `chatbot-atelier-release` | Prepara y ejecuta un lanzamiento autorizado con identificación exacta de fuente/compilación, controles de entrega, compatibilidad de datos y reversión. |
| `chatbot-atelier-operations` | Mantiene la fiabilidad, calidad de la conversación, soporte, costes, migraciones y desarrollo continuo. |

#### Equipo de juegos — nueve habilidades

| Habilidad | Qué hace en palabras sencillas |
| --- | --- |
| `gamedev-director` | Coordina el proyecto del juego conservando su dirección creativa aceptada, decisiones y checkpoints. |
| `gamedev-studio` | Establece o restaura la identidad del estudio, originales de marca aceptados, identidad del desarrollador y preparación de las cuentas. |
| `gamedev-concepts` | Produce conceptos de juego distintos con controles, sistemas que interactúan, progresión, dirección artística y una vía de producción viable. |
| `gamedev-preproduction` | Amplía el concepto elegido en un diseño de juego y técnico detallado, reglas numéricas, catálogos, estados y un plan de producción. |
| `gamedev-assets` | Crea e integra arte, animación, interfaz, sonido y respuesta háptica, conservando las fuentes aceptadas y su relación con los recursos en ejecución. |
| `gamedev-build` | Implementa el juego móvil nativo: controles, cámara, jugabilidad, enemigos, mundo, progresión, economía, guardados y compilaciones por plataforma. |
| `gamedev-qa` | Comprueba la jugabilidad real, comportamiento en dispositivos, controles, guardados, rendimiento y requisitos, distinguiendo pruebas reales en ejecución de comprobaciones documentales. |
| `gamedev-release` | Prepara firmas, binarios exactos, materiales de las tiendas, compras, privacidad, despliegue gradual y recuperación para un lanzamiento autorizado. |
| `gamedev-liveops` | Desarrolla y mantiene el juego publicado usando telemetría observada, incidentes, progresión, contenido, economía y cambios compatibles. |

Son responsabilidades, no una promesa de que 33 agentes se ejecuten simultáneamente. El sistema debe seleccionar el equipo y el nivel de esfuerzo que necesite la tarea. Una revisión solo es independiente cuando la realiza realmente otro actor; la autocomprobación del autor debe identificarse como tal.

## 3. Elige tu idioma antes de instalar

Abre la guía traducida mediante los enlaces anteriores. El inglés es el idioma predeterminado cuando no se indica una preferencia. Las guías traducidas cubren los mismos pasos; el código, los nombres estables de las habilidades, los nombres de archivo y los identificadores de protocolo permanecen sin cambios para que los comandos funcionen de manera coherente.

Al empezar la instalación o el proyecto, pega este texto y sustituye el idioma:

```text
Mi idioma de trabajo es el español (es). Úsalo para explicaciones, preguntas,
actualizaciones de estado, instrucciones de traspaso e informes dirigidos al
usuario. Mantén sin cambios los nombres estables de las habilidades, la sintaxis
de los comandos y los identificadores técnicos. Registra esta preferencia en el
contexto guardado del proyecto y en los traspasos. Pregunta por separado por el
idioma del producto que estamos construyendo.
```

El idioma de la documentación, el de la conversación y el del producto son decisiones distintas. Por ejemplo, puedes leer la guía ucraniana, trabajar con el agente en ucraniano y publicar una aplicación en inglés y alemán. Indica los tres cuando corresponda. Registra la preferencia en la plantilla de contexto del proyecto o en un archivo equivalente existente e inclúyela en cada traspaso. Cambiar únicamente el idioma de la página del navegador no establece el idioma de otra conversación.

## 4. Prepara tus cuentas y fuentes

1. Inicia sesión en la cuenta de ChatGPT o Codex donde quieras usar la suite. Comprueba que el modo necesario y las herramientas de gestión de habilidades estén realmente disponibles en esa cuenta o espacio de trabajo.
2. Abre `https://github.com/alex-hohaizel/codex-agents`. Actualmente el propietario controla la visibilidad del repositorio. Un repositorio privado requiere una cuenta de GitHub autorizada y una conexión con acceso a ese repositorio exacto.
3. En Work, conecta o selecciona GitHub mediante la interfaz disponible de Plugins/conexiones. Si el acceso está restringido a repositorios seleccionados, incluye `alex-hohaizel/codex-agents`. Pide a Work que lea `README.md` e informe de la rama y revisión a las que puede acceder realmente.
4. En Codex local, autoriza el acceso Git local si quieres clonar un repositorio privado. Una conexión GitHub de Work no demuestra que Terminal en tu ordenador pueda autenticarse.
5. Usa una versión publicada identificada o un commit exacto para la instalación. Guarda ese identificador. Leer una rama `main` sin fijar mientras cambia puede mezclar versiones.
6. Descarga la revisión elegida del repositorio mediante **Code → Download ZIP** de GitHub o clónala con Git. Extrae el archivo descargado antes de instalar. Debes ver `kit/manifest.json`, `kit/portable/` y `kit/skills/`.
7. No coloques la descarga, los planes ni las copias de seguridad dentro de un directorio de detección de habilidades. Una carpeta normal como Descargas o un espacio dedicado a gestionar habilidades es adecuado.

Para Git local, usa una rama confirmada y una nueva ubicación de destino que no contenga otro trabajo:

```bash
git clone --branch main https://github.com/alex-hohaizel/codex-agents.git "codex-agents"
cd "codex-agents"
git rev-parse HEAD
git status --short
```

Un clon en `main` es una copia de trabajo de las fuentes cómoda. Antes de aplicar una actualización, confirma que su SHA coincida con la versión elegida. No pegues tokens de acceso en conversaciones, archivos de proyecto, comandos de shell ni documentos de traspaso. Usa la conexión de cuenta o el flujo de credenciales de la plataforma.

## 5. Instala en Work desde una cuenta nueva

### Qué hace esta vía

Guarda las 33 habilidades reutilizables como habilidades personales mediante el proceso de gestión admitido por el entorno. Conectar GitHub, subir un ZIP, leer esta guía o añadir archivos del repositorio como fuentes del proyecto no demuestra por sí solo que una habilidad se haya instalado o cargado.

### Paso a paso

1. Abre Work y crea o abre un proyecto de gestión de habilidades. Aquí gestionas el toolkit, en lugar del producto que construirás después.
2. Selecciona el idioma con el bloque de la sección 3.
3. Facilita acceso a la revisión seleccionada del repositorio. Si Work no puede leer archivos privados de GitHub, conecta ese repositorio o adjunta el paquete seleccionado mediante la interfaz de archivos disponible.
4. Invoca la capacidad disponible de Skill Creator/gestión de habilidades. Pídele que examine el paquete antes de cambiar las entradas instaladas.
5. Pega el bloque de instalación de abajo. Autoriza la instalación dentro del alcance indicado y la verificación necesaria.
6. Deja que Work examine el inventario de habilidades existente por nombre estable. En una cuenta nueva debe crear las entradas que falten; en una existente debe actualizar las entradas personales correspondientes y conservar las habilidades ajenas al cambio.
7. Conserva el informe de instalación. Debe identificar cada una de las 33 habilidades, versión, revisión de la fuente, resultado y fallos pendientes.
8. Actualiza o vuelve a abrir la página Skills si muestra información antigua. Abre una conversación nueva en el proyecto del producto previsto y realiza la comprobación de carga y la práctica descritas más abajo.

```text
Instala las 33 habilidades personales reutilizables de la revisión seleccionada
y verificada de alex-hohaizel/codex-agents, usando kit/manifest.json y kit/skills/.
Mi idioma de trabajo es el español (es).

Usa el proceso de gestión de habilidades personales admitido por el entorno.
Examina las entradas existentes por nombre estable, verifica el paquete,
conserva las habilidades ajenas al cambio y la identidad visual existente,
e instala o actualiza las entradas correspondientes. Conserva copias de
seguridad y la procedencia exacta de las fuentes. No instales globalmente
agentes específicos de proyecto. No cambies datos del producto, servicios
de producción ni ajustes de la cuenta.

Informa de cada nombre estable, versión, revisión de la fuente y estado
create/update/noop/failure. Distingue una habilidad guardada de la detección
por el entorno y del uso real en una tarea. Si la gestión de habilidades no
está disponible, explica la capacidad concreta que falta; no describas una
copia subida o de solo lectura como instalada.
```

El procedimiento de gestión admitido por Work puede guardar las habilidades de una en una. Un resultado parcial debe enumerar las entradas completadas y las pendientes, permitiendo continuar con seguridad en lugar de empezar de nuevo. Ejecutar el actualizador portátil de Codex en un sistema de archivos en la nube no demuestra que se haya actualizado tu directorio personal de habilidades de Work.

## 6. Instala o actualiza en Codex

### La vía más sencilla: pide a Codex que haga la instalación controlada

1. Descarga o clona la revisión elegida como se describe arriba.
2. Abre Codex en tu espacio existente de gestión de habilidades. Si es tu primera instalación, abre el checkout u otra carpeta normal de gestión; no hace falta un nuevo repositorio de producto.
3. Da a Codex la ruta exacta del checkout. En Mac, selecciona la carpeta en Finder y pulsa **Option + Command + C** para copiar su ruta completa.
4. Pega el bloque siguiente después de establecer tu idioma preferido.
5. Revisa el informe final de instalación y conserva el journal y la ubicación de la copia de seguridad.
6. Abre una conversación nueva en el proyecto real del producto para las comprobaciones de carga y prácticas.

```text
Instala las 33 habilidades personales de base desde el directorio kit/
verificado de este checkout de alex-hohaizel/codex-agents. Usa la revisión
de la versión publicada seleccionada. Mi idioma de trabajo es el español (es).

Esto autoriza audit → apply → verify locales, planes exactos y copias de
seguridad para esta suite. Lee kit/manifest.json y --help del actualizador.
Verifica la integridad del paquete. Audita los directorios personales y las
copias de proyecto conocidas. Guarda planes y copias de seguridad fuera de las
raíces de detección de habilidades. Aplica solo el plan exacto que esté listo.
Conserva los cambios locales desconocidos e informa de los archivos en
conflicto; no eludas las comprobaciones de divergencias.

Conserva icon_small, icon_large, brand_color, las rutas y los bytes de los iconos
existentes, incluidas las referencias históricas ./assets/. Verifica usando
el journal exacto devuelto por apply. Informa de canonical_core_verified,
visual_preservation_verified, recuentos updated/noop, blockers, failures y duplicates.

No cambies productos, producción, plugins ni la configuración del entorno.
Después comprueba por separado la detección de ambos constructores y de los
directores App, ChatBot y Game por el entorno. No trates los archivos instalados
como prueba del uso real en una tarea.
```

### Vía de Terminal para quien quiera los comandos exactos

El actualizador portátil requiere Python 3.9 o posterior y usa la biblioteca estándar. Ejecuta estos comandos desde la raíz del repositorio. La auditoría lee el paquete y las ubicaciones de instalación y escribe un plan propuesto. Apply realiza los cambios de instalación previstos y registra un journal.

```bash
python3 kit/portable/update_skill_suite.py --help
python3 kit/portable/update_skill_suite.py audit --kit kit --plan ../agent-system-plan.json
python3 kit/portable/update_skill_suite.py apply --plan ../agent-system-plan.json
```

Lee el resultado de `apply`. Copia su ruta `journal` exacta en el comando de verificación:

```bash
python3 kit/portable/update_skill_suite.py verify --kit kit --journal /absolute/path/from-apply/journal.json
```

La ruta final anterior es un marcador de posición. Sustitúyela; no la ejecutes literalmente. Por defecto el actualizador usa `~/.agents/skills` como destino y comprueba la raíz antigua `~/.codex/skills`. Si tu entorno usa otra raíz personal admitida, utiliza de manera explícita y coherente los argumentos `--destination` y `--legacy-root`. Consulta primero `audit --help`. Añade `--project-root /absolute/path/to/product` para auditar las copias locales del producto pertinentes. El actualizador no elimina automáticamente una copia de proyecto que oculte una habilidad personal.

Una instalación de archivos correcta significa 33 fuentes verificadas en la versión prevista, sin blockers/failures/duplicates pendientes, `canonical_core_verified=true` y `visual_preservation_verified=true` procedentes de la verificación con el journal apply real. Una comprobación de hashes sin ese journal no demuestra que se hayan conservado tus iconos existentes. Detente ante un conflicto y conserva el trabajo local; no uses una sustitución forzada para que el informe parezca limpio.

### Comprueba la carga por separado de la instalación

Pide a Codex o Work en una nueva conversación de producto:

```text
Antes de cambiar nada, identifica la fuente cargada exacta y la versión de
agent-foundry, design-specialist-skills y los tres directores de producto.
Confirma qué instrucciones adaptativas, de investigación, identidad visual
y Work↔Codex has leído realmente. Informa por separado de las fuentes no disponibles.
```

Después asigna una tarea real pequeña con una entrada conocida y un criterio de aceptación. Por ejemplo, pide al director de aplicaciones que revise los estados de error de una pantalla frente a un requisito existente o a un constructor que esboce las responsabilidades de un agente especializado. Esto comprueba el comportamiento. No certifica todas las capacidades del producto. Mantén como resultados separados la instalación de archivos, la carga por el entorno, el uso práctico y la aceptación del producto.

## 7. Usa el sistema en una tarea real

### Una tarea de ingeniería acotada

```text
Investiga las consultas repetidas a la base de datos en este endpoint. Conserva
su API y comportamiento de negocio. Primero lee el código y las mediciones
existentes. Identifica qué pruebas faltan, propón la investigación útil más
pequeña e implementa una reparación justificada en esta rama. Verifica la
corrección y muestra mediciones antes/después cuando el entorno lo permita.
```

Esto no necesita una empresa, un producto, una marca ni un estudio de mercado completo nuevos. Un constructor puede diseñar un investigador reutilizable si quieres este flujo como agente duradero; para una tarea puntual, usa las herramientas e instrucciones pertinentes existentes. El sistema no debe crear un agente nuevo solo porque una tarea sea técnica.

### Una aplicación completa

```text
BRIEF: Quiero una aplicación para [público] que resuelva [problema]. Las plataformas
objetivo son [plataformas], el presupuesto es [presupuesto] y mi papel es [papel].
Aclara las incógnitas, investiga alternativas reales y prepara opciones completas.
Mantén visibles todos mis requisitos, incluidos diseño, idioma, soporte y
monetización, a lo largo del plan. No selecciones un concepto por mí sin indicarlo.
```

El equipo debe investigar lo que importa, comparar opciones e identificar obstáculos de lanzamiento o de cuentas antes de una gran implementación. Después de elegir un concepto, conserva los referentes de diseño seleccionados y todos los requisitos acordados. Una primera versión funcional es un checkpoint de ese plan, no permiso para descartar el resto.

### Un juego móvil

```text
BRIEF: Desarrolla conceptos de juego móvil distintos para [público/experiencia].
Cubre controles y respuesta, sistemas que interactúan, enemigos, progresión
significativa, dirección artística, monetización y una vía de producción
Android/iOS viable. Muestra conceptos visuales comparables. Conserva la identidad
seleccionada en los recursos y en la implementación jugable. Define comprobaciones
reales en dispositivos.
```

Una imagen conceptual no demuestra animación, controles táctiles, rendimiento ni recuperación de guardados. El flujo de juegos debe conectar la promesa visual seleccionada con recursos fuente editables y una sección jugable representativa antes de producir todo el conjunto de recursos.

## 8. Work y Codex en el mismo proyecto

Work resulta útil donde estén disponibles las fuentes necesarias, las herramientas de investigación y diseño y los servicios conectados. Codex resulta útil donde estén disponibles el checkout de las fuentes, el runtime, las herramientas de compilación y las integraciones locales o con dispositivos. Cualquiera de los modos puede hacer más cuando dispone de las capacidades adecuadas. Elige por el acceso y las pruebas reales, en lugar de asignar cada tarea de razonamiento a un modo y cada tarea de código al otro.

Crea una sola identidad para el producto. Nombres como `My Product [WORK]` y `My Product [CODEX]` ayudan a navegar, pero no demuestran que los dos proyectos contengan el mismo producto. Registra el repositorio, la rama, el subdirectorio, los identificadores de proyecto y las fuentes de los checkpoints. Una conversación nueva debe mantenerse dentro de ese proyecto existente.

### Mantén un pequeño contexto compartido

Usa la plantilla de contexto de proyecto del repositorio o un equivalente existente en tu producto. Registra al menos: identificador del proyecto; repositorio y rama; SHA completo del commit actual; identificador de la tarea; fase actual; idiomas de trabajo y del producto; versión del toolkit y recibo de instalación; decisiones aceptadas; fuente completa de los requisitos; fuente de los referentes de diseño; alcance autorizado; checkpoint actual; efectos o decisiones pendientes; y siguiente acción. Mantén las credenciales fuera de este registro.

### Work → Codex local, paso a paso

1. Pide a Work: «Continúa esta fase en Codex. Prepara el traspaso para este proyecto existente.»
2. Work debe identificar el siguiente resultado exacto que entregar y las pruebas necesarias para aceptarlo. Debe guardar o proporcionar los requisitos, decisiones, fuentes y checkpoint pertinentes.
3. Si hay un canal compartido autorizado, Work puede guardar el traspaso y verificar la revisión guardada. Guardar un archivo no demuestra que se haya iniciado otra sesión de Codex.
4. Abre el checkout local existente. Si no hay copia local, clona el repositorio y la rama confirmados en la carpeta elegida. Autentícate localmente para los repositorios privados.
5. Antes de actualizar el checkout, examínalo:

```bash
git remote get-url origin
git branch --show-current
git rev-parse HEAD
git status --short
```

6. Si el árbol de trabajo está limpio y hace falta actualizar esa rama, usa `git pull --ff-only origin <confirmed-branch>` con el nombre real de la rama. Confirma el SHA completo resultante. Si hay cambios locales o un historial divergente, consérvalos y resuelve la discrepancia antes del trabajo dependiente.
7. Abre la carpeta exacta en la interfaz de proyectos de Codex. Para un producto existente, usa su proyecto existente; añade la carpeta mediante la interfaz disponible de edición del proyecto si hace falta.
8. Pega el bloque de traspaso cumplimentado de abajo. Codex confirma primero la identidad del repositorio, revisión, cambios locales, permisos y checkpoint, y después trabaja en la acción acotada.
9. Conserva su informe de resultados, referencias a commits/compilaciones y pruebas de los tests para el traspaso de regreso.

### Codex → Work, paso a paso

1. Pide a Codex que prepare un traspaso de resultados o de una nueva tarea para el mismo proyecto existente.
2. Incluye los archivos realmente modificados, el SHA completo o revisión del artefacto, los controles realizados, limitaciones, decisiones abiertas y siguiente acción. Indica si los cambios son locales, están registrados en un commit o publicados.
3. Si está autorizado publicar los cambios acordados en una rama identificada, publica solo ese alcance y verifica la revisión remota. En caso contrario, proporciona un artefacto controlado mediante el canal disponible. Work no puede leer automáticamente una ruta local de un Mac.
4. Abre el proyecto Work existente, conecta el repositorio pertinente o adjunta el artefacto exacto y pega el traspaso.
5. Work lee las fuentes reales y comprueba la revisión de entrada antes de revisar o continuar. Debe informar explícitamente de los archivos inaccesibles.
6. Registra la aceptación por separado de la entrega y la ejecución. Un informe de que existe una compilación no equivale a la aceptación del producto.

### Traspaso para copiar

Sustituye todos los campos entre corchetes antes de usar este bloque:

```text
Continúa el proyecto existente [ID/nombre del proyecto] en [Work/Codex].
Idioma de trabajo: [idioma/código]. Idiomas del producto: [idiomas].
Repositorio: [URL]. Rama/subdirectorio: [rama/ruta].
Revisión de entrada: [SHA completo o revisión exacta del artefacto].
ID de tarea y fase: [ID/fase].
Checkpoint: [fuente exacta accesible].
Requisitos y decisiones aceptadas: [fuentes exactas].
Referentes de diseño e identidad: [fuentes exactas, si procede].
Resultado esperado y aceptación: [resultado/controles concretos].
Alcance autorizado: [qué puede cambiarse o publicarse].
Trabajo completado y pruebas: [hechos y referencias].
Decisiones abiertas, bloqueos o efectos externos inciertos: [detalles/ninguno].
Siguiente acción: [una acción concreta].

Verifica primero identidad del proyecto, revisión, herramientas disponibles y
permisos. Conserva todos los requisitos y decisiones aceptados. No reinicialices
el producto. Distingue traspaso preparado, entrega verificada, recepción, ejecución,
resultado y aceptación. Continúa el trabajo autorizado que sea realmente posible.
```

## 9. Reanuda tras una conversación interrumpida

Abre una conversación nueva en el mismo proyecto y pide que restaure el último checkpoint verificado. Facilita su fuente si aún no es accesible. Debe reconciliar la tarea, los requisitos, la revisión de las fuentes, los archivos actuales y los resultados externos reales antes de continuar.

```text
Restaura esta tarea existente a partir de su último checkpoint verificado y
las fuentes reales. Conserva requisitos, decisiones, permisos, resultados
completados y efectos externos inciertos. Verifica la revisión actual y quién
es responsable de la siguiente acción. Antes de repetir un despliegue, pago,
mensaje u otra acción externa, comprueba si el intento anterior se completó
realmente. Continúa el trabajo autorizado disponible y registra un nuevo checkpoint.
```

Una conversación bloqueada no demuestra que su última operación haya fallado. La recuperación debe comprobar el resultado real antes de repetir una acción que podría duplicarse.

## 10. Actualiza versiones sin perder un proyecto existente

### Lee primero el registro de la versión

Cada versión debe explicar qué cambió, a qué usuarios afecta, requisitos previos, pasos de instalación, pasos de adopción en el proyecto, verificación, limitaciones conocidas y reversión. La guía general también debe cambiar cuando cambie el flujo habitual. No te bases solo en un número de versión.

La versión 6.0.0 conserva los 33 nombres estables y la identidad de los iconos, y refuerza las pruebas, dependencias de fuentes, lectura JSON y escrituras de estado. Añade perfiles de producción/contexto autónomos y fidelidad explícita a las referencias. Los números históricos de protocolos y esquemas de ejecución del proyecto siguen siendo distintos; renombrar un esquema antiguo con el número de la suite sin migración rompe la compatibilidad.

### Proyectos existentes de Agent Systems 2.3 / Game 4.3

1. Guarda el checkpoint actual del proyecto, requisitos aceptados, decisiones, originales de diseño, revisión de las fuentes, versión del toolkit y efectos externos conocidos.
2. Registra desde dónde se carga realmente cada habilidad o agente de proyecto. Inventaría las copias personales y locales al proyecto; no supongas que cambiar un directorio global cambia todos los proyectos.
3. Instala la suite de destino mediante la vía Work o Codex correspondiente descrita arriba. Conserva la versión de la fuente y el recibo de instalación.
4. Vuelve a abrir el proyecto existente y realiza una revisión de compatibilidad de solo lectura antes de la siguiente acción dependiente.
5. Pide a su director o constructor que compare el estado actual del proyecto con el nuevo flujo. Identifica una actualización explícita del estado nativo o del flujo solo donde sea necesaria. Conserva el comportamiento del producto, las decisiones aceptadas y los efectos desconocidos.
6. Previsualiza los cambios exactos. Si hace falta una migración de estado, usa su herramienta admitida y su `--help` real; vincula la vista previa al hash del estado de origen, el hash de la suite de destino y la fuente de autorización. Aplica el plan revisado y autorizado en lugar de inventar una aprobación histórica.
7. Vuelve a comprobar todos los requisitos afectados y los criterios de aceptación de la fase actual. Ejecuta una tarea real pequeña de continuación y guarda sus pruebas.
8. Registra la versión adoptada del toolkit en el checkpoint del producto. Conserva el registro de migración para que la próxima conversación pueda explicar la transición.

Game6.0.0 contiene una vía revisada de actualización del flujo para proyectos 4.2.0/4.3.0/5.0.0 que conserva el esquema de runtime 2.0.0. Su uso depende del estado real del proyecto y de las entradas admitidas por la herramienta. Los proyectos App y ChatBot necesitan igualmente su propia revisión de estado y compatibilidad; no deben pasar por una migración Game solo porque la suite tenga una versión compartida.

### Agentes creados anteriormente con un constructor

Actualizar el constructor no reescribe los agentes que creó antes. Esos agentes pueden contener reglas, herramientas, conocimientos e identidad visual específicos del proyecto. Inventaríalos en sus propios proyectos. Compara la fuente antigua, los cambios locales y la nueva fuente propuesta. Conserva las pruebas originales de propiedad/instalación. Si faltan, prepara una comparación y un plan explícitos de adopción; no fabriques un recibo antiguo. Ejecuta casos de regresión para las responsabilidades reales del agente y registra la versión adoptada por separado.

El repositorio reutilizable excluye los paquetes de fuentes privados de agentes de producto. La actualización de un proyecto concreto pertenece a sus fuentes controladas y su registro de migración, no a la instalación global de habilidades de todo el mundo.

### Conserva la identidad visual

Los iconos existentes de Codex, sus rutas, color y bytes deben conservarse durante las actualizaciones habituales. Una nueva versión no es una instrucción para rediseñar una habilidad o un producto existentes. Las habilidades nuevas sin identidad pueden recibir el estilo apropiado de sistema o de proyecto. Work puede gestionar por sí mismo un avatar de servicio; mantén diferenciado el comportamiento visual del entorno de la identidad portátil de Codex. Conserva los originales de diseño seleccionados del producto y del juego, no solo una descripción verbal de ellos.

### Revierte con cuidado

Para una instalación de la suite Codex, usa el journal exacto de instalación:

```bash
python3 kit/portable/update_skill_suite.py rollback --journal /absolute/path/from-apply/journal.json
```

La reversión comprueba las copias de seguridad y protege los cambios posteriores desconocidos. Revierte la instalación de habilidades representada por ese journal. No deshace una migración de datos del producto, un despliegue, un mensaje, una compra ni otra acción externa. La restauración en Work debe usar su vía admitida de gestión de habilidades y la fuente anterior guardada. Una reversión del estado del producto necesita su propio procedimiento de recuperación revisado.

## 11. Mantén completas las actualizaciones futuras

Para cada cambio futuro del toolkit, actualiza este repositorio con las fuentes canónicas, requisitos afectados, contenido de los paquetes, registro de versión, pasos de migración, pruebas de verificación y los cambios necesarios en la guía o las traducciones. Conserva los registros de versiones anteriores. Reconstruye paquetes y metadatos de integridad desde las fuentes comprobadas; evita publicar un archivo ensamblado a partir de una caché desactualizada del entorno.

Ejecuta los comandos de comprobación y creación de paquetes del repositorio según su `--help` actual y la documentación para mantenedores. Confirma el commit remoto después de publicar. «Guardado localmente», «registrado en un commit», «publicado», «instalado», «cargado» y «adoptado por un proyecto» son estados distintos. Si el acceso impide publicar, conserva el trabajo completado e informa de la revisión exacta no sincronizada.

Una regla del repositorio es efectiva cuando un agente futuro la lee en un entorno con el acceso necesario. No es un detector global de todas las demás conversaciones y ordenadores. Empieza una futura tarea de gestión de habilidades conectando este repositorio y leyendo su `AGENTS.md`, requisitos y último registro de versión. Un servicio independiente de sincronización programada necesitaría su propio runtime real y autorización; la suite no crea uno de forma oculta.

## 12. Solución de problemas

| Síntoma | Qué comprobar después |
| --- | --- |
| Work no puede leer el repositorio | Verifica la cuenta GitHub, el permiso para el repositorio privado exacto y la conexión seleccionada; pide que lea un archivo conocido. |
| El clon local pide autenticación | Configura la autorización Git local mediante el flujo de credenciales de la plataforma. La conexión de Work es independiente. |
| Las habilidades no aparecen después de guardarlas | Actualiza o vuelve a abrir la página Skills, después usa una conversación nueva del proyecto y verifica la detección real de las fuentes. |
| Aparecen dos copias de la misma habilidad | Audita los nombres estables en las raíces personales y del proyecto. Conserva los cambios locales y resuelve la fuente duplicada exacta; no borres habilidades ajenas al cambio. |
| El actualizador informa de divergencias o un conflicto | Guarda el diff local y compara los archivos indicados con la fuente seleccionada. Usa un plan de reconciliación revisado. |
| Una comprobación de archivos pasó, pero el agente se comporta como antes | Verifica la fuente realmente cargada por el entorno y después ejecuta una tarea pequeña; la integridad de los archivos por sí sola no basta. |
| Work no ve código cambiado en un Mac | Publica el alcance autorizado o adjunta un artefacto exacto; una ruta local por sí sola no da acceso. |
| Una conversación nueva ha perdido decisiones | Restaura el checkpoint y las fuentes completas de requisitos antes de continuar. Actualiza el contexto guardado. |
| La primera versión funcional omite el diseño o idioma acordados | Reconcilia el registro de requisitos; mantén esos requisitos en el plan e identifica sus pasos de implementación y aceptación. |
| No están disponibles el despliegue, el envío a tiendas o las comprobaciones en dispositivos | Indica la cuenta, herramienta, dispositivo o acceso exactos que faltan y continúa la preparación independiente. No afirmes que una comprobación no disponible ha pasado. |
| Un agente afirma haber iniciado otra sesión | Pide una referencia verificada de inicio/recepción. Un archivo de traspaso solo demuestra el estado realmente observado. |
| Quieres tareas continuas | Confirma un programador, executor, credenciales, comprobaciones de actividad y vía de recuperación reales. La instalación de habilidades por sí sola no los proporciona. |

## 13. Documentación oficial y alcance de las pruebas

Las interfaces del entorno y la disponibilidad por cuenta pueden cambiar. Consulta la interfaz real y la documentación oficial vigente al instalar o conectar servicios. Referencias sobre el comportamiento del producto comprobadas para esta guía el 7 de noviembre de 2026:

- [Build skills — ChatGPT Learn](https://learn.chatgpt.com/docs/build-skills): estructura de habilidades reutilizables, detección local y conceptos de instalación.
- [Plugins — ChatGPT Learn](https://learn.chatgpt.com/docs/plugins): directorio de plugins, conexión y conceptos de distribución.

Este repositorio distribuye una suite reutilizable y su flujo de instalación controlado. Un plugin de marketplace público, una licencia comercial, un runtime alojado permanente, herramientas de pago de terceros y credenciales son entregables separados, salvo que una versión concreta los proporcione y verifique explícitamente. Los conceptos de marketing ilustran flujos de trabajo y usos previstos; las afirmaciones promocionales finales deben corresponder a capacidades y pruebas verificadas.
