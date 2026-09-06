# Synthesized Architecture for a Comprehensive Knowledge App

## Estado
Draft

## Propósito
Sintetizar una arquitectura unificada para una nueva aplicación comprehensiva de knowledge management, tomando como insumo las herramientas revisadas en:

- `/home/jp/proyectos/hum-ecosystem/tools`

Esta arquitectura no busca copiar una sola tool existente.
Busca:

- preservar lo mejor de cada una
- corregir sus límites históricos
- unificar documento, evidencia, grafo, CLI y UI en un sistema coherente

---

## 1. Principio rector

La nueva app debe organizar el conocimiento alrededor de esta cadena:

> fuente → sample/biopsia → átomo → composición/vista

Y debe separar claramente cuatro cosas:

1. **fuente original**
2. **evidencia anclada**
3. **conocimiento destilado**
4. **superficies operativas y de visualización**

Esta separación permite:

- provenance fuerte
- validación determinista
- anotación sobre superficies derivadas
- composición reutilizable
- operaciones CLI/UI claras

---

## 2. Qué toma esta arquitectura de cada tool

## De `sldb`
Tomamos:

- contratos documentales estructurados
- store/index de documentos y modelos
- tracking de documentos
- operaciones por campos/secciones/docs
- búsqueda física y semántica

Rol en la nueva app:
- **capa documental estructurada principal**

## De `marcado`
Tomamos:

- marcado inline sobre Markdown
- anchors/rangos
- validación y exportación canónica
- anotación semántica sobre samples

Rol en la nueva app:
- **capa de anotación y addressabilidad sobre samples**

## De `kgdb`
Tomamos:

- persistencia de relaciones
- modelo de nodos y edges tipados
- queries deterministas de trazabilidad
- superficie de lineage

Rol en la nueva app:
- **capa grafo para relaciones y navegación relacional**

## De `deskops`
Tomamos:

- disciplina del átomo pequeño
- pregunta 5WH1+
- UX CLI humana
- integración útil entre backlog y producción de conocimiento

Rol en la nueva app:
- **disciplina operativa y experiencia de uso**, no el contenedor principal de la KB

## De `ontomap`
Tomamos:

- ideas de modelado ontológico explícito
- multidimensionalidad semántica
- posibilidad de proyecciones más formales

Rol en la nueva app:
- **capa opcional de formalización semántica avanzada**

## De `sldb-ui`
Tomamos:

- dualidad source/rendered
- inspección de markers
- edición asistida de documentos marcados

Rol en la nueva app:
- **operator surface documental**

## De `graph_ui`
Tomamos:

- inspección/edición visual del grafo
- arquitectura de editor reusable y no monolítica

Rol en la nueva app:
- **operator surface relacional/graph**

## De `spec2viz`
Tomamos:

- idea de proyecciones visuales derivadas
- separación semántica vs render
- IR intermedia para vistas

Rol en la nueva app:
- **capa de vistas derivadas y reporting visual**

## De `hum-scrapper`
Tomamos:

- idea de ingestión/adquisición con memoria semántica
- posibilidad de automatizar captura de fuentes y candidates

Rol en la nueva app:
- **capa futura de ingestión automatizada**

## De `tractatusIR`
Tomamos:

- ideas conceptuales de semántica relacional si demuestran valor

Rol en la nueva app:
- **reserva conceptual / investigación**, no dependencia base

## De `repopackage`
Tomamos:

- ideas de contratos entre componentes
- futura federación o composición de repos/stores de conocimiento

Rol en la nueva app:
- **infraestructura opcional para escalado/federación**

---

## 3. Arquitectura por capas

## Capa 1. Sources

### Propósito
Registrar y preservar artefactos fuente originales.

### Entidades clave
- SourceDoc o SourceRecord

### Responsabilidades
- registrar ruta/localizador
- registrar hash fuerte (`source_hash_sha256`)
- preservar metadata descriptiva
- impedir edición accidental de la fuente

### Inspiración principal
- KB spec actual
- prácticas de provenance que faltan en los átomos heredados

---

## Capa 2. Samples / biopsias

### Propósito
Representar cortes trazables, recuperables y anotables de una fuente.

### Entidades clave
- SourceSampleDoc

### Responsabilidades
- declarar anchor bundle
- sostener validación determinista contra la fuente
- servir como superficie de anotación
- conservar quote/excerpt recuperable

### Reglas clave
- debe poder probarse que el fragmento existe en la fuente correcta
- la fuente correcta se identifica por `source_hash_sha256`
- la anotación vive aquí, no en el PDF

### Inspiración principal
- KB spec
- `marcado`
- `sldb`

---

## Capa 3. Annotation / semantic markup

### Propósito
Permitir que los samples se anoten sin romper su rol de evidencia.

### Entidades clave
- markup overlays
- semantic ranges
- marker namespaces

### Responsabilidades
- marcar fragmentos significativos
- conservar separabilidad entre texto base y semántica añadida
- exportar representación estructurada del marcado

### Inspiración principal
- `marcado`
- `sldb-ui`

---

## Capa 4. Atoms

### Propósito
Guardar conocimiento destilado, pequeño y composable.

### Entidades clave
- KnowledgeAtomDoc

### Responsabilidades
- responder exactamente una pregunta 5WH1+
- mantener una respuesta durable y reusable
- apuntar a samples mediante provenance estructurado
- servir de unidad base para composición

### Reglas clave
- un átomo no depende directamente del PDF
- un átomo depende de uno o más samples
- si una pieza responde varias preguntas, probablemente no es un solo átomo

### Inspiración principal
- `deskops` atom discipline
- `sldb` local models
- KB clarifications

---

## Capa 5. Composition / derived knowledge

### Propósito
Construir síntesis, vistas y documentos compuestos a partir de átomos y samples.

### Entidades clave
- composed docs
- syntheses
- FAQs
- thematic views
- reports

### Responsabilidades
- combinar átomos sin inflarlos
- materializar perspectivas o narrativas más profundas
- soportar salidas humanas consumibles

### Inspiración principal
- composición documental sobre SLDB
- `spec2viz`
- prácticas de documentación derivada

---

## Capa 6. Graph / lineage

### Propósito
Hacer explícitas las relaciones entre fuentes, samples, átomos, composiciones, temas y tareas.

### Entidades clave
- source nodes
- sample nodes
- atom nodes
- composition nodes
- thematic/grouping nodes
- task/work nodes opcionales

### Relaciones esperables
- `sampled_from`
- `anchored_in`
- `distilled_from`
- `supports`
- `composes`
- `about_topic`
- `derived_view_of`

### Responsabilidades
- consultas de trazabilidad
- lineage visual
- navegación relacional
- detección de cobertura, huecos, clusters y dependencias

### Inspiración principal
- `kgdb`
- `graph_ui`
- parcialmente `ontomap`

---

## Capa 7. CLI

### Propósito
Ofrecer una interfaz humana, fluida y directa para operar el sistema.

### Inspiración principal
- `deskops`
- `sldb`
- parcialmente `kgdb`

### Familias de comandos esperables

#### Sources
- register source
- hash source
- inspect source

#### Samples
- create sample
- validate sample
- annotate sample
- show sample
- find samples

#### Atoms
- add atom
- show atom
- list atoms
- link atom to sample
- compose atoms

#### Graph
- trace atom
- show lineage
- list relations
- inspect neighborhood

#### Views
- render view
- export report
- project diagram

### Principio de UX
La CLI debe hablar el lenguaje del trabajo real, no solo exponer primitivas internas.

---

## Capa 8. UI

### Propósito
Proveer superficies gráficas para inspección, edición y navegación.

### Subsuperficies

#### Document UI
- source vs rendered
- marker inspection
- field inspection
- sample annotation
- provenance inspection

#### Graph UI
- lineage graph
- relation editing/inspection
- topic clusters
- coverage maps

#### Derived views UI
- dashboards
- reports
- conceptual maps
- timelines

### Inspiración principal
- `sldb-ui`
- `graph_ui`
- `spec2viz`

---

## Capa 9. Workflow layer

### Propósito
Coordinar trabajo humano o automatizado alrededor de la producción de conocimiento.

### Posición arquitectónica
Esta capa debe existir, pero no debe contener la KB misma.

### Responsabilidades
- backlog de extracción
- coverage tracking
- review workflows
- curation queues
- validation queues

### Inspiración principal
- `deskops`

### Regla importante
El workflow debe operar sobre:
- fuentes
- samples
- atoms
- composiciones

pero no ser su único contenedor material.

---

## 4. Componentes concretos de la nueva app

## A. Document runtime
Basado conceptualmente en `sldb`.

Funciones:
- modelos
- templates
- tracking
- parse/render/extract
- store/index

## B. Sample runtime
Extensión específica de la nueva app.

Funciones:
- registrar source binding
- validar anchor exacto
- gestionar sample docs
- preparar surfaces anotables

## C. Markup runtime
Basado en `marcado`.

Funciones:
- parsear markers
- validar rangos
- resolver anchors
- exportar overlays estructurados

## D. Atom runtime
Inspirado en `deskops` + `KnowledgeAtomDoc`.

Funciones:
- crear átomos 5WH1+
- validar atomicidad estructural
- enlazar provenance a sample ids
- soportar composición

## E. Graph runtime
Basado en `kgdb`.

Funciones:
- persistir nodos/edges
- consultas de lineage
- trazabilidad entre capas

## F. Projection runtime
Inspirado en `spec2viz`.

Funciones:
- transformar semántica canónica en vistas derivadas
- generar source/diagramas/reports/dashboards

## G. Operator surfaces
Basadas en `sldb-ui` y `graph_ui`.

Funciones:
- editar samples
- navegar atoms
- inspeccionar provenance
- explorar grafos

## H. Workflow runtime
Inspirado en `deskops`, pero desacoplado.

Funciones:
- tareas de extracción
- revisión
- cobertura
- coordinación editorial

---

## 5. Modelo de verdad del sistema

La nueva app necesita dejar claro dónde vive la verdad de cada capa.

### Fuente de verdad por nivel

#### Fuente
- artefacto fuente registrado + hash

#### Sample
- documento sample estructurado + anchor validable + binding a source hash

#### Markup
- overlay/representación estructurada sobre el sample

#### Atom
- documento atómico estructurado con provenance a sample ids

#### Grafo
- representación derivada/persistida de relaciones explícitas

#### Vistas
- materializaciones derivadas, nunca fuente primaria

### Consecuencia
- diagramas no son verdad canónica
- UI no es verdad canónica
- el grafo no debe inventar semántica documental
- el workflow no debe absorber la KB

---

## 6. Migraciones conceptuales que esta arquitectura corrige

## Desde `deskops`
Se preserva:
- disciplina atómica
- UX CLI
- valor del workflow

Se corrige:
- que los átomos vivan dentro de `desk/`
- que provenance sea texto libre
- que operación y KB compartan el mismo contenedor

## Desde `sldb`
Se preserva:
- el poder del documento estructurado y trackeado

Se extiende:
- con primitivas nativas para source/sample/atom

## Desde `marcado`
Se preserva:
- el valor del marcado reversible y direccionable

Se integra:
- explícitamente con samples como superficie de evidencia anotada

## Desde `kgdb`
Se preserva:
- el valor de relaciones y trazabilidad

Se integra:
- como capa clara de lineage sobre las entidades KB

---

## 7. Orden de implementación sugerido

## Fase 1: núcleo documental y provenance
- sources
- samples
- atom model
- store/document tracking
- validación básica

## Fase 2: marcado y validación exacta
- integración con markup
- deterministic anchor validation
- sample annotation UX

## Fase 3: graph lineage
- relaciones source/sample/atom
- consultas de trazabilidad
- primeras vistas grafo

## Fase 4: composición y vistas derivadas
- composed docs
- reports
- diagrams/dashboards

## Fase 5: workflow y automatización
- backlog/editorial workflow
- ingestion helpers
- semiautomation

---

## 8. Decisiones de diseño que deberían mantenerse firmes

1. la KB no debe vivir dentro de una superficie operativa accidental
2. la provenance fuerte debe vivir en source hash + anchor validable
3. el sample es la superficie de evidencia/anotación
4. el átomo es una respuesta pequeña a una sola pregunta 5WH1+
5. la composición produce profundidad; el átomo no debe inflarse
6. el grafo expresa relaciones; no reemplaza el documento
7. la UI y las visualizaciones son materializaciones, no verdad primaria

---

## 9. Síntesis final

La nueva app debería ser entendida como la convergencia de cuatro núcleos:

1. **document runtime**
   - inspirado en `sldb`
2. **annotation/runtime de samples**
   - inspirado en `marcado`
3. **atom discipline + human CLI**
   - inspirada en `deskops`
4. **graph lineage and projections**
   - inspirado en `kgdb`, `graph_ui` y `spec2viz`

Con capas adicionales opcionales de:

- ontología formal (`ontomap`)
- ingestión automatizada (`hum-scrapper`)
- federación/contratos inter-repo (`repopackage`)

En una frase:

> la nueva arquitectura debe unir documento estructurado, evidencia validable, átomos composables, trazabilidad relacional y surfaces operativas claras, sin volver a mezclar conocimiento durable con contenedores operativos accidentales.
