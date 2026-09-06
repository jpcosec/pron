# Graph Architecture

## Estado
Draft

## Propósito
Definir el papel del grafo dentro de la arquitectura de la base de conocimiento.

Este documento se centra en la parte **knowledge / provenance retrieval** del sistema.
No describe toda la app.
Describe específicamente:

- qué clase de grafo es este
- qué verdad expresa
- qué entidades y relaciones debe contener
- qué preguntas debe poder responder
- cómo se relaciona con documentos, samples, anchors y composiciones

---

## 1. Tesis principal

La nueva app debe entenderse como una **base de conocimiento document-first cuyo espinazo relacional es un grafo de provenance**.

Dicho de otro modo:

> el sistema es una KB centrada en documentos y evidencia, y el grafo es la capa que materializa lineage, provenance y relaciones de conocimiento recuperables.

## Fórmula corta

- **la verdad primaria** vive en documentos estructurados y binding a fuentes
- **el grafo** vive para hacer recuperables y navegables las relaciones

---

## 2. Qué clase de grafo es

No es solamente un knowledge graph genérico.
No es solamente un citation graph.
No es solamente un dependency graph.

El núcleo del sistema es un:

> **provenance graph system**

Pero más precisamente:

> **source-grounded provenance knowledge graph**

Eso significa que el grafo está organizado alrededor de:

- fuentes versionadas
- samples verificables
- átomos destilados
- composiciones derivadas

Y que sus relaciones principales no son ornamentales.
Son relaciones de trazabilidad, apoyo, derivación, composición y recuperación.

## Aclaración importante

Ese backbone de provenance no agota toda la dimensión grafo de la app.
A la luz de:

- `/home/jp/Upla/tutor_apoe/desk/atoms/tag-namespaces.yaml`
- `/home/jp/Upla/tutor_apoe/docs/diagrams/apos-atom-taxonomy.md`
- `/home/jp/proyectos/hum-ecosystem/tools/ontomap/README.md`
- `/home/jp/proyectos/hum-ecosystem/tools/kgdb/README.md`
- `/home/jp/proyectos/hum-ecosystem/tools/sldb/README.md`
- `/home/jp/proyectos/hum-ecosystem/tools/marcado/README.md`

conviene distinguir explícitamente **tres estratos de grafo conectados**:

1. **grafo de provenance**
2. **grafo conceptual centrado en átomos**
3. **grafo estructural proyectado**

Este documento sigue centrado sobre todo en el backbone de provenance y retrieval, pero debe leerse ya con esa estratificación en mente.

---

## 3. Qué no debe hacer el grafo

El grafo es central, pero no debe reemplazar el modelo documental.

## No debe:

- inventar provenance que no exista en documentos o validaciones
- sustituir el binding exacto a la fuente
- reemplazar la validación de anchors
- convertirse en la única verdad de los samples
- absorber por completo la semántica documental primaria

## Regla clave

La jerarquía de verdad del sistema debe ser:

1. **fuente registrada y versionada**
2. **sample anclado y validado**
3. **átomo documentado con provenance a sample ids**
4. **composición documentada**
5. **grafo como materialización relacional de esas verdades**

---

## 4. Qué sí debe hacer el grafo

El grafo debe volver operativas las relaciones que en puro documento son incómodas de consultar, navegar o visualizar.

## Funciones principales

### 4.1 Lineage
Responder:

- de qué fuente viene este sample
- de qué samples viene este átomo
- qué composiciones usan este átomo
- qué cadena conecta una vista derivada con la fuente original

### 4.2 Provenance retrieval
Responder:

- qué evidencia sostiene esta afirmación
- qué fuentes exactas sostienen este grupo de átomos
- qué ruta de support existe desde una composición hasta un source hash concreto

### 4.3 Semantic retrieval
Responder:

- qué átomos están relacionados con este tema
- qué samples y átomos comparten estructura conceptual
- qué conceptos aparecen juntos con frecuencia

### 4.4 Coverage y diagnostics
Responder:

- qué partes de una fuente tienen samples pero no átomos
- qué átomos tienen provenance débil o dispersa
- qué composiciones dependen de muy poca evidencia
- qué zonas del corpus están poco cubiertas

### 4.5 Projection substrate
Servir como base para:

- graph UI
- lineage views
- concept maps
- coverage maps
- dependency views

---

## 5. Planos del sistema

La arquitectura completa debe distinguir al menos tres planos.

## 5.1 Plano de artefactos

Las cosas originales o derivadas que existen como artefactos:

- PDFs
- webpages
- archivos
- blobs
- commits
- snapshots

## 5.2 Plano documental

Las superficies estructuradas donde vive la KB:

- source records
- samples
- markup overlays
- atoms
- compositions

## 5.3 Plano grafo

La red explícita de relaciones entre entidades del plano documental y, selectivamente, del plano estructural.

## Regla

El plano grafo no reemplaza a los otros dos.
Los conecta.

## 5.4 Estratificación interna del plano grafo

Con base en los artefactos APOS y en herramientas previas del ecosistema, el plano grafo debe subdividirse explícitamente.

### A. Grafo de provenance

Backbone documental y de evidencia:
- `Source`
- `Sample`
- `Atom`
- `Composition`

### B. Grafo conceptual

Backbone semántico del dominio, especialmente importante alrededor de átomos:
- `Atom`
- `Concept`
- `ConceptGroup`
- `TaxonomyNode`
- `QuestionType`
- `TagFacet`

### C. Grafo estructural proyectado

Backbone de soporte estructural derivado de proyecciones ricas:
- `SourceSection`
- `Symbol`
- `StructureNode`
- `LayoutRegion`
- `ASTNode` cuando valga la pena persistirlo

## Observación clave

Esta estratificación hace explícito algo que los tags hoy ocultan: no toda relación semántica entre átomos es provenance, y no toda relación útil cabe en un tag plano.

---

## 6. El backbone del grafo

La columna vertebral del sistema debe ser esta cadena:

> Source → Sample → Atom → Composition

## Relaciones troncales mínimas

- `sampled_from`
- `anchored_in`
- `distilled_from`
- `supports`
- `composes`
- `derived_from`

### Lectura conceptual

- una **fuente** es el referente versionado
- un **sample** es evidencia direccionable y validable
- un **átomo** es conocimiento destilado reusable
- una **composición** es conocimiento compuesto o materializado

---

## 7. Entidades de primer nivel del grafo

## 7.1 Entidades mínimas del backbone de provenance

### Source
Nodo para una fuente registrada.

### Sample
Nodo para una biopsia / sample verificable.

### Atom
Nodo para un átomo de conocimiento.

### Composition
Nodo para síntesis, FAQs, reports, vistas derivadas u otras composiciones.

## 7.2 Entidades del grafo conceptual

### Concept
Concepto explícito del dominio.

Ejemplos sugeridos por `/home/jp/Upla/tutor_apoe/docs/diagrams/apos-atom-taxonomy.md`:
- Action
- Process
- Encapsulation
- Genetic Decomposition
- ACE Cycle
- Research Paradigm

### ConceptGroup
Agrupaciones de alto nivel del dominio.

Ejemplos explícitos del mismo archivo:
- Foundations
- Core Structures
- Mechanisms
- Pedagogy
- Research
- Mathematical Domains
- Applications
- Synthesis

### TaxonomyNode
Nodo de ubicación conceptual más preciso dentro del mapa del dominio.

Ejemplos derivados del árbol documentado en `apos-atom-taxonomy.md`:
- `apos/core-structures/action`
- `apos/mechanisms/encapsulation`
- `apos/research/paradigm`
- `apos/mathematical-domains/functions`

### QuestionType
Categoría 5WH1+ del átomo.

### TagFacet
Etiqueta namespaced modelada explícitamente como facet, no como ontología completa.

Esto se basa en la realidad observable de `/home/jp/Upla/tutor_apoe/desk/atoms/tag-namespaces.yaml`, que hoy define namespaces como:
- `system`
- `topic`
- `layer`
- `domain`

## 7.3 Entidades del grafo estructural proyectado

### SourceSection
Sección, heading, chapter o región significativa de una fuente.

### Symbol
Símbolo o entidad estructural en código.

### StructureNode
Nodo estructural proyectado selectivamente desde AST/DOM/layout.

### LayoutRegion
Región espacial o bloque relevante de una fuente con layout.

### ASTNode
Nodo AST cuando valga la pena persistirlo como entidad del grafo.

## 7.4 Entidades operativas opcionales

### WorkflowItem
Task, review item o cola editorial si se quiere integrar trabajo con KB.

---

## 8. Relaciones principales del grafo

## 8.1 Relaciones de provenance

### `sampled_from`
- `Sample -> Source`
- el sample fue tomado de esta fuente versionada

### `anchored_in`
- `Sample -> SourceSection` o `StructureNode`
- el sample se ancla en una zona o nodo estructural concreto

### `distilled_from`
- `Atom -> Sample`
- el átomo se destiló desde este sample

### `supports`
- `Sample -> Atom`
- este sample aporta evidencia que sostiene este átomo

### `derived_from`
- `Composition -> Atom | Sample | Source`
- esta composición deriva de estas piezas previas

### `composes`
- `Composition -> Atom`
- esta composición usa estos átomos como ladrillos

## 8.2 Relaciones del grafo conceptual

### `about_concept`
- `Atom -> Concept`
- relación principal entre un átomo y el concepto que trata

### `secondary_about`
- `Atom -> Concept`
- concepto secundario relevante sin romper la atomicidad principal

### `located_in_taxonomy`
- `Atom -> TaxonomyNode`
- ubica el átomo dentro del mapa conceptual del dominio

### `grouped_under`
- `TaxonomyNode -> ConceptGroup`

### `child_of`
- `TaxonomyNode -> TaxonomyNode`
- relación jerárquica dentro del árbol conceptual

### `subconcept_of`
- `Concept -> Concept | ConceptGroup`

### `has_question_type`
- `Atom -> QuestionType`

### `tagged_with`
- `Entity -> TagFacet`
- mantiene la utilidad de tags para retrieval ligero y facetado

## 8.3 Relaciones conceptuales opcionales entre átomos y conceptos

### `related_to`
### `contrasts_with`
### `depends_on`
### `extends`
### `prerequisite_for`
### `explains`
### `elaborates`
### `applies_to`

Estas pueden surgir por curación, inferencia controlada o composición explícita.

## 8.4 Relaciones del grafo estructural proyectado

### `anchored_in`
- `Sample -> SourceSection | StructureNode | LayoutRegion | ASTNode | Symbol`
- esta ampliación es coherente con `/home/jp/Upla/source/spec/MULTI_SOURCE_ANCHORING.md`, donde se propone usar estructura rica como base de anclaje cuando exista

### `mentions_symbol`
- `Sample | Atom -> Symbol`

### `drawn_from_section`
- `Sample -> SourceSection`

### `supported_by_structure`
- `Atom -> StructureNode | LayoutRegion | ASTNode | Symbol`
- útil cuando se quiera materializar explícitamente soporte estructural relevante

---

## 9. Provenance retrieval

La capacidad distintiva del sistema no es solo guardar relaciones.
Es permitir **recuperación de provenance** útil y fuerte.

## Provenance retrieval significa poder preguntar:

- ¿qué evidencia sostiene este átomo?
- ¿qué samples conectan esta composición con la fuente?
- ¿qué source hashes respaldan esta afirmación?
- ¿qué partes exactas del corpus sostienen este clúster conceptual?
- ¿qué átomos dependen de este source version?

## Esto requiere que el grafo preserve o referencie:

- identidad de fuente
- binding de versión
- sample ids
- tipo de relación
- contexto estructural cuando sea útil

---

## 10. Knowledge retrieval

Además de provenance retrieval, el grafo debe soportar **knowledge retrieval**.

## Knowledge retrieval significa poder preguntar:

- ¿qué átomos existen sobre este tema?
- ¿qué átomos están conectados con este otro átomo?
- ¿qué composiciones reúnen estos conceptos?
- ¿qué fuentes contribuyen más a un tópico?
- ¿qué cadenas de composición conectan ideas distantes?

## Distinción importante

- **provenance retrieval** = recuperar sostén, origen, lineage
- **knowledge retrieval** = recuperar conceptos, relaciones, agrupaciones, composiciones

El grafo debe soportar ambos.

---

## 11. Relación con AST, DOM, layout y otras estructuras

Como la app es multi-source y structure-aware, el grafo no puede ignorar por completo la estructura interna de las fuentes.

Esto es aún más importante dado que `/home/jp/Upla/source/spec/MULTI_SOURCE_ANCHORING.md` ya propone explícitamente tratar:

- texto
- AST
- estructura documental
- layout
- metadata

como categorías de primer nivel dentro de la estructura documental de la app.

## Pero tampoco debe persistir todo indiscriminadamente.

### Regla práctica

Distinguir al menos tres niveles interrelacionados:

## 11.1 Grafo de provenance

Persistido por defecto.

Entidades típicas:
- Source
- Sample
- Atom
- Composition

## 11.2 Grafo conceptual

Persistido por defecto cuando la KB ya necesita navegación semántica real sobre átomos.

Entidades típicas:
- Concept
- ConceptGroup
- TaxonomyNode
- QuestionType
- TagFacet

## 11.3 Grafo estructural proyectado

Persistido selectivamente cuando agrega valor.

Entidades típicas:
- SourceSection
- Symbol
- StructureNode
- LayoutRegion
- ASTNode en casos especiales

### Principio

La estructura rica de las fuentes vive primariamente en el subsistema de estructura.
Solo las partes útiles para retrieval, provenance o navegación deben proyectarse al grafo persistido.

## Conexión explícita con las fuentes observadas

- `/home/jp/Upla/tutor_apoe/desk/atoms/tag-namespaces.yaml` muestra una semántica de facets útil pero plana
- `/home/jp/Upla/tutor_apoe/docs/diagrams/apos-atom-taxonomy.md` muestra una semántica conceptual mucho más rica, jerárquica y estructurante
- `/home/jp/proyectos/hum-ecosystem/tools/ontomap/README.md` aporta la idea de modelar jerarquía y composición mediante aristas explícitas y dimensiones semánticas
- `/home/jp/proyectos/hum-ecosystem/tools/kgdb/README.md` aporta el runtime de persistencia, traversal y query determinista para estas relaciones
- `/home/jp/proyectos/hum-ecosystem/tools/sldb/README.md` aporta una capa documental estructurada y AST-aware (`mdast`)
- `/home/jp/proyectos/hum-ecosystem/tools/marcado/README.md` aporta anchors, validación y rangos/markers navegables

---

## 12. Por qué esto importa en una app multi-source

Sin grafo, sería mucho más difícil navegar preguntas como:

- qué átomos vienen de una función concreta en un repo
- qué samples de markdown bajo cierto heading sostienen una teoría
- qué páginas de un PDF alimentan una composición dada
- qué fuentes distintas convergen en el mismo tópico
- qué composiciones comparten evidencia base

El grafo aporta una **superficie relacional común** entre fuentes heterogéneas.

Eso es una de sus mayores ventajas.

---

## 13. Consultas clave que el grafo debe soportar

## 13.1 Consultas de lineage

- mostrar lineage completo de un átomo hasta sus fuentes
- listar composiciones que dependen de un átomo
- listar átomos que provienen de una fuente exacta

## 13.2 Consultas de support

- listar samples que sostienen un átomo
- detectar átomos con un solo sample de soporte
- mostrar support graph de una composición

## 13.3 Consultas de coverage

- secciones de fuente con samples pero sin átomos
- temas con muchos átomos pero poca evidencia
- fuentes muy sampleadas pero poco compuestas

## 13.4 Consultas temáticas

- átomos sobre un topic
- composiciones que cruzan topics
- clusters de átomos relacionados

## 13.5 Consultas estructurales avanzadas

- átomos derivados de symbols específicos
- samples anclados en headings concretos
- evidencia proveniente de regiones layout particulares

---

## 14. UI y visualización del grafo

La graph UI no debe ser solo decorativa.

Debe permitir:

- tracing de lineage
- exploración de vecinos
- navegación topic-centric
- inspección de support networks
- análisis de coverage
- debugging de provenance

### Vistas recomendables

- source → sample → atom graph
- composition dependency graph
- topic clusters
- evidence support map
- source coverage map

---

## 15. Posicionamiento arquitectónico final

El grafo debe tratarse como uno de los pilares principales de la app.

## Pilares sugeridos

1. source subsystem
2. structure subsystem
3. anchoring subsystem
4. knowledge document subsystem
5. graph subsystem
6. projection / UI subsystem
7. workflow subsystem

## Papel del graph subsystem

- materializar relaciones
- habilitar lineage
- habilitar retrieval relacional
- servir de base para visualizaciones y diagnostics

---

## 16. Síntesis final

Sí: el sistema puede describirse razonablemente como un **provenance graph system**.

Pero esa descripción ya no es suficiente por sí sola.

La formulación más precisa pasa a ser:

> una base de conocimiento document-first y source-grounded cuyo espinazo relacional es un provenance knowledge graph, enriquecido por un grafo conceptual de átomos y un grafo estructural proyectado

En esa arquitectura:

- la fuente exacta importa
- el sample validado importa
- el átomo pequeño y composable importa
- la composición importa
- la taxonomía conceptual de los átomos importa
- la estructura rica de las fuentes importa
- y el grafo hace recuperable toda la red de soporte, derivación y relación entre ellos

## Relectura fuerte de las fuentes citadas

- `/home/jp/Upla/tutor_apoe/desk/atoms/tag-namespaces.yaml` debe leerse como una gramática de facets útil, no como ontología suficiente
- `/home/jp/Upla/tutor_apoe/docs/diagrams/apos-atom-taxonomy.md` debe leerse como una semilla de grafo conceptual/ontológico mucho más importante
- `/home/jp/proyectos/hum-ecosystem/tools/ontomap/README.md` anticipa bien la idea de relaciones explícitas multidimensionales
- `/home/jp/proyectos/hum-ecosystem/tools/kgdb/README.md` anticipa bien el runtime de query y trace para estas capas
- `/home/jp/proyectos/hum-ecosystem/tools/sldb/README.md` y `/home/jp/proyectos/hum-ecosystem/tools/marcado/README.md` anticipan la conexión entre estructura documental, anchors y recuperación semántica

En una frase:

> el grafo no reemplaza la verdad documental; la vuelve navegable, trazable y recuperable como sistema de conocimiento, y no debe reducir la semántica conceptual de los átomos a un simple sistema plano de tags.
