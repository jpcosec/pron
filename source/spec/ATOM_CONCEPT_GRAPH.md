# Atom Concept Graph

## Estado
Draft

## Propósito
Definir la parte del grafo centrada en los átomos como **grafo conceptual**, distinguiéndola de:

- el **grafo de provenance** (`Source -> Sample -> Atom -> Composition`)
- el **grafo estructural** derivado de AST, DOM, layout, trees y otras proyecciones de fuente

Este documento parte de una observación concreta: en el estado actual del proyecto, el sistema de tags está cargando más semántica de la que razonablemente puede expresar como superficie plana.

La meta aquí es explicitar:

- qué aportan los tags hoy
- qué no aportan
- por qué la taxonomía de átomos es más importante que la simple namespacing de tags
- cómo convertir esa taxonomía en grafo conceptual explícito
- cómo conectar ese grafo con provenance y con estructuras derivadas de AST/DOM/layout

---

## 1. Fuentes consideradas

Este documento se apoya explícitamente en estos artefactos:

### En `tutor_apoe`
- `/home/jp/Upla/tutor_apoe/desk/atoms/tag-namespaces.yaml`
- `/home/jp/Upla/tutor_apoe/docs/diagrams/apos-atom-taxonomy.md`

### En herramientas previas del ecosistema
- `/home/jp/proyectos/hum-ecosystem/tools/ontomap/README.md`
- `/home/jp/proyectos/hum-ecosystem/tools/kgdb/README.md`
- `/home/jp/proyectos/hum-ecosystem/tools/sldb/README.md`
- `/home/jp/proyectos/hum-ecosystem/tools/marcado/README.md`
- `/home/jp/proyectos/hum-ecosystem/tools/tractatusIR/README.md`

---

## 2. Observación principal

La situación actual sugiere que el proyecto está usando los tags como una especie de sustituto comprimido para varias cosas distintas:

- clasificación
- retrieval
- taxonomía conceptual
- ubicación semántica de un átomo
- agrupación por dimensión
- a veces incluso relaciones débiles entre conceptos

Eso es demasiado trabajo para una superficie plana de tags.

## Tesis

Los tags deben seguir existiendo, pero no deben seguir siendo el portador principal de la semántica conceptual del átomo.

La semántica conceptual principal debe migrar a un **grafo conceptual explícito**.

---

## 3. Qué nos dice `tag-namespaces.yaml`

Archivo fuente:
- `/home/jp/Upla/tutor_apoe/desk/atoms/tag-namespaces.yaml`

Este archivo define namespaces como:

- `domain`
- `layer`
- `system`
- `topic`

Y para cada uno describe:

- `meaning`
- `use_when`
- `do_not_use_when`
- ejemplos

### Qué valor aporta

Este archivo sí aporta algo importante:

- establece **dimensiones de etiquetado**
- sugiere reglas de uso
- normaliza una convención de namespacing
- habilita retrieval básico y facetado

### Qué no aporta

No aporta por sí mismo:

- jerarquías conceptuales explícitas
- relaciones entre conceptos
- subtopic trees
- relaciones de prerequisito, contraste o extensión
- ubicación fuerte de un átomo dentro de una ontología conceptual

## Conclusión

`tag-namespaces.yaml` describe una **gramática de etiquetas**.
No describe todavía una **ontología conceptual**.

---

## 4. Qué nos dice `apos-atom-taxonomy.md`

Archivo fuente:
- `/home/jp/Upla/tutor_apoe/docs/diagrams/apos-atom-taxonomy.md`

Este archivo es mucho más importante para el futuro del grafo conceptual.

### Evidencia explícita

El documento define un árbol taxonómico para `desk/atoms/` con ramas como:

- `sources`
- `apos/foundations`
- `apos/core-structures`
- `apos/mechanisms`
- `apos/genetic-decomposition`
- `apos/pedagogy`
- `apos/research`
- `apos/schema-development`
- `apos/mathematical-domains`
- `apos/applications`
- `apos/synthesis`

Y bajo cada rama enumera subdominios concretos, por ejemplo:

- `core-structures/action`
- `mechanisms/encapsulation`
- `research/paradigm`
- `mathematical-domains/functions`
- `applications/elementary-math`
- `synthesis/future-of-apos`

Además, el mismo documento materializa esta organización en un `mindmap` Mermaid con raíz `APOS atoms`.

### Qué significa eso

Esto ya no es un simple sistema de tags.
Esto es un **mapa conceptual del dominio APOS**.

Ese mapa expresa al menos:

- categorías conceptuales
- subcategorías
- ámbitos de aplicación
- agrupaciones por rol teórico/pedagógico/metodológico
- una forma de ubicar átomos dentro del espacio conceptual

## Conclusión

`apos-atom-taxonomy.md` debe entenderse como un **borrador implícito de ontología / grafo conceptual**, no solo como documentación de carpetas.

---

## 5. Diferencia fuerte entre tags y taxonomía

## Tags
Sirven bien para:

- facetado
- filtros rápidos
- búsqueda
- agrupación ligera
- exportación legible
- hints de UI

## Taxonomía / concepto explícito
Sirve para:

- ubicar átomos en un espacio conceptual
- expresar jerarquías
- modelar relaciones entre conceptos
- construir vecindades semánticas
- proyectar mapas del dominio
- enriquecer retrieval conceptual

## Regla recomendada

Los tags deben ser una **superficie secundaria de retrieval**.
La taxonomía y las relaciones conceptuales deben convertirse en **nodos y edges explícitos del grafo**.

---

## 6. El abuso actual de tags

La hipótesis de abuso es esta:

- hoy se usan tags para cosas que deberían ser nodos o relaciones explícitas

Por ejemplo, un tag como:

- `topic:genetic-decomposition`

sirve para búsqueda, pero no expresa por sí solo:

- si `genetic decomposition` es una categoría mayor o menor
- si está dentro de APOS como teoría o metodología
- si se relaciona con `research role`, `teaching role`, `definition`, `design`, `non-uniqueness`, `refinement`
- si ciertos átomos la elaboran, la delimitan, la contrastan o la aplican

Lo mismo vale para:

- `topic:action`
- `topic:encapsulation`
- `topic:source-book`
- `layer:research`
- `layer:applications`

Todos esos tags son útiles, pero son una reducción plana de una semántica mucho más rica.

---

## 7. Propuesta: tres capas semánticas distintas alrededor del átomo

Cada átomo debería vivir simultáneamente en tres marcos relacionales.

## 7.1 Provenance layer

Responde:
- ¿de qué sample(s) viene?
- ¿qué source(s) lo sostienen?

Relaciones típicas:
- `distilled_from`
- `supported_by`
- `sampled_from`

## 7.2 Concept layer

Responde:
- ¿de qué concepto habla?
- ¿en qué parte de la taxonomía vive?
- ¿qué otros conceptos vecinos tiene?
- ¿qué relaciones conceptuales guarda con otros átomos?

Relaciones típicas:
- `about_concept`
- `located_in_taxonomy`
- `subconcept_of`
- `related_to`
- `contrasts_with`
- `elaborates`
- `applies_to`
- `has_question_type`

## 7.3 Structural support layer

Responde:
- ¿a qué estructura concreta de la fuente se ancla el sample que lo sostiene?
- ¿proviene de una sección, símbolo, nodo AST, bloque layout o heading?

Relaciones típicas:
- `anchored_in`
- `mentions_symbol`
- `drawn_from_section`
- `supported_by_structure`

---

## 8. El grafo conceptual del átomo

## 8.1 Nodo principal: Atom

El átomo sigue siendo el objeto curado y pequeño que responde una sola pregunta 5WH1+.

## 8.2 Nodos conceptuales explícitos

La arquitectura debería introducir nodos como:

- `Concept`
- `ConceptGroup`
- `TaxonomyNode`
- `QuestionType`
- `TagFacet`

No hace falta que esos nombres sean definitivos, pero sí hace falta distinguir sus roles.

### `Concept`
Ejemplos:
- Action
- Process
- Encapsulation
- Genetic Decomposition
- ACE Cycle
- Research Paradigm
- Spanning Set and Span

### `ConceptGroup`
Ejemplos derivados de `apos-atom-taxonomy.md`:
- Foundations
- Core Structures
- Mechanisms
- Pedagogy
- Research
- Mathematical Domains
- Applications
- Synthesis

### `TaxonomyNode`
Puede representar nodos del árbol conceptual, por ejemplo:
- `apos/mechanisms/encapsulation`
- `apos/research/paradigm`
- `apos/mathematical-domains/functions`

### `QuestionType`
Los tipos 5WH1+ ya existentes:
- `what`
- `why`
- `how`
- `how_not`
- `when`
- `where`
- `for_whom`

### `TagFacet`
Una manera explícita de modelar la superficie de tags sin confundirla con ontología profunda.

Ejemplos:
- `system:apos`
- `layer:research`
- `domain:mathematics-education`
- `topic:encapsulation`

---

## 9. Relaciones recomendadas para el grafo conceptual

## 9.1 Entre Atom y Concept

### `about_concept`
- `Atom -> Concept`
- relación principal: este átomo trata sobre este concepto

### `secondary_about`
- `Atom -> Concept`
- útil cuando un átomo toca un segundo concepto sin dejar de ser atómico

## 9.2 Entre Atom y TaxonomyNode

### `located_in_taxonomy`
- `Atom -> TaxonomyNode`
- indica su ubicación principal en el mapa conceptual del dominio

## 9.3 Entre Concept y ConceptGroup / TaxonomyNode

### `subconcept_of`
- `Concept -> Concept | ConceptGroup`

### `grouped_under`
- `TaxonomyNode -> ConceptGroup`

### `child_of`
- `TaxonomyNode -> TaxonomyNode`

## 9.4 Entre Atom y Atom

### `elaborates`
- un átomo desarrolla o precisa otro

### `contrasts_with`
- un átomo delimita o contrasta con otro

### `depends_on`
- comprensión conceptual o composicional depende de otro átomo

### `applies_in`
- un átomo teórico se aplica en un dominio o contexto representado por otro nodo conceptual

## 9.5 Entre Atom y QuestionType

### `has_question_type`
- `Atom -> QuestionType`
- conserva explícitamente el principio deskops / 5WH1+

## 9.6 Entre entidades y TagFacet

### `tagged_with`
- `Atom | Sample | Composition -> TagFacet`
- mantiene la utilidad de tags para retrieval, sin inflar su papel ontológico

---

## 10. Qué hacer con los tags

Los tags no deben desaparecer.

## Deben conservarse como:

- filtros rápidos
- claves de búsqueda
- agrupaciones ligeras
- materialización legible de facets
- soporte para export, UI y navegación simple

## Pero no deben cargar por sí solos:

- toda la jerarquía conceptual
- las relaciones entre conceptos
- la ubicación taxonómica profunda
- las relaciones entre átomos

## Regla práctica

Cuando algo importa para:
- razonamiento
- lineage conceptual
- navegación de dominio
- composición
- proyecciones estructuradas

probablemente debe vivir como nodo/edge explícito, no solo como tag.

---

## 11. Conexión con `ontomap`

Archivo fuente:
- `/home/jp/proyectos/hum-ecosystem/tools/ontomap/README.md`

`ontomap` se describe como una implementación de un:

> "Grafo Ontológico Multidimensional sobre RDF/OWL"

Y dice explícitamente:

> "jerarquía y composición se modelan exclusivamente mediante propiedades de aristas, no anidamiento estructural"

Además modela aristas con varias dimensiones semánticas (`where`, `what`, `when`, `how`, `why`, `who`).

## Qué recuperamos de ahí

No necesariamente todo RDF/OWL en la primera versión.
Sí recuperamos la intuición fuerte de que:

- las relaciones deben ser explícitas
- la jerarquía no debe esconderse solo en carpetas o strings
- distintas dimensiones semánticas pueden coexistir
- un mismo conjunto de nodos puede proyectarse de varias maneras

## Conexión con el grafo conceptual de átomos

La taxonomía APOS es justamente un caso donde:

- las carpetas y tags se quedan cortos
- necesitamos conceptos, grupos y relaciones explícitas
- la multidimensionalidad es real: teoría, pedagogía, investigación, aplicaciones, dominios matemáticos, etc.

---

## 12. Conexión con `kgdb`

Archivo fuente:
- `/home/jp/proyectos/hum-ecosystem/tools/kgdb/README.md`

`kgdb` se describe como:

> "the graph persistence, traversal, and query substrate for the HUM ecosystem"

Y enfatiza que:

- persiste graph records
- responde deterministic graph queries
- ofrece graph traceability
- no debe reinterpretar por sí mismo la verdad semántica upstream

## Qué recuperamos de ahí

Para el grafo conceptual de átomos, `kgdb` aporta el modelo correcto de runtime:

- persistencia de facts relacionales
- queries por identidad, semántica y scope
- traversal determinista
- separación entre productor semántico y runtime grafo

## Conexión concreta

El productor semántico de la nueva app podría exportar no solo:
- `Source`
- `Sample`
- `Atom`

sino también:
- `Concept`
- `TaxonomyNode`
- `TagFacet`
- relaciones conceptuales explícitas

---

## 13. Conexión con `sldb`

Archivo fuente:
- `/home/jp/proyectos/hum-ecosystem/tools/sldb/README.md`

`sldb` se describe como:

> "A structurally aware Markdown extraction and template mapping library based on `mdast` principles"

Y además indica que puede exportar semántica y que el store ya conoce:

- documentos
- secciones
- semantic tags
- semantic DAG relationships
- equivalences

## Qué recuperamos de ahí

- la noción de que la capa documental ya es estructurada
- que existe AST-awareness (`mdast`)
- que la app puede producir handoffs semánticos hacia el grafo
- que tags, sections y DAGs no deben quedarse enterrados en strings

## Conexión concreta

El grafo conceptual de átomos no debe nacer desconectado del documento.
Debe poder nutrirse de:

- campos estructurados del átomo
- secciones del documento
- taxonomías documentadas
- exports semánticos

---

## 14. Conexión con `marcado`

Archivo fuente:
- `/home/jp/proyectos/hum-ecosystem/tools/marcado/README.md`

`marcado` se define como:

- Semantic Markdown ASG
- con `syntax/graph validation`
- `stable anchor lookup`
- exportación canónica

## Qué recuperamos de ahí

- la idea de que los rangos y markers también pueden formar estructuras navegables
- que la anotación semántica de samples puede proyectarse al grafo
- que los anchors no son solo strings sino puntos recuperables en una estructura

## Conexión concreta

Los samples anotados pueden introducir relaciones conceptuales adicionales, por ejemplo:

- sample marca un rango como `concept.encapsulation`
- ese rango se conecta con un `Concept` del grafo
- el átomo derivado hereda o consolida esa relación

---

## 15. Conexión con `tractatusIR`

Archivo fuente:
- `/home/jp/proyectos/hum-ecosystem/tools/tractatusIR/README.md`

Aunque el README visible es breve y operacional, sí deja claro que hay un foco en:

- `tractatus-semantics.lisp`
- `tractatus-worlds.lisp`
- `tractatus-axes.lisp`
- `tractatus-discrimination.lisp`
- `tractatus-persistence.lisp`

## Qué recuperamos de ahí

No una implementación directa todavía.
Sí la intuición histórica de que:

- la semántica relacional importa
- los ejes, discriminaciones y mundos conceptuales pueden ser relevantes
- una KB madura no se agota en documentos planos ni tags planos

---

## 16. Conexión con múltiples ASTs

Este punto es clave para unir lo viejo con lo nuevo.

Si la nueva app trata AST como categoría documental de primer nivel, entonces puede producir varias clases de grafo estructural:

- AST de código
- mdast de Markdown
- DOM/HTML tree
- object tree de JSON/YAML
- árboles de secciones
- layout trees derivados de PDF

## Qué cambia con eso

El átomo ya no solo puede estar relacionado con:
- un topic tag
- una carpeta
- un sample textual

También puede estar relacionado con:
- un `Symbol`
- un `StructureNode`
- una `SourceSection`
- un nodo AST concreto
- un nodo DOM concreto
- una región layout concreta

## Resultado

El grafo conceptual puede enriquecerse con soporte estructural explícito.

Ejemplos:
- `Atom -> about_concept -> Encapsulation`
- `Atom -> distilled_from -> Sample`
- `Sample -> anchored_in -> SourceSection`
- `Sample -> anchored_in -> ASTNode`
- `Concept -> grouped_under -> Mechanisms`
- `TaxonomyNode(mechanisms/encapsulation) -> child_of -> TaxonomyNode(mechanisms)`

---

## 17. Arquitectura propuesta: tres grafos conectados

## 17.1 Grafo de provenance

Backbone documental y de evidencia:
- `Source`
- `Sample`
- `Atom`
- `Composition`

## 17.2 Grafo conceptual de átomos

Backbone semántico del dominio:
- `Atom`
- `Concept`
- `ConceptGroup`
- `TaxonomyNode`
- `QuestionType`
- `TagFacet`

## 17.3 Grafo estructural proyectado

Backbone de soporte estructural:
- `SourceSection`
- `Symbol`
- `StructureNode`
- `ASTNode` cuando valga la pena
- `LayoutRegion`

## Relaciones puente

- `Sample -> anchored_in -> StructureNode`
- `Atom -> distilled_from -> Sample`
- `Atom -> about_concept -> Concept`
- `Atom -> located_in_taxonomy -> TaxonomyNode`
- `Entity -> tagged_with -> TagFacet`

---

## 18. Recomendación fuerte

La nueva arquitectura debería **degradar el rol de los tags** desde:

- portador principal de semántica

hacia:

- superficie ligera de facets y retrieval

Y debería **promover la taxonomía y las relaciones conceptuales** a:

- nodos explícitos
- edges explícitos
- vistas navegables
- queries de conocimiento reales

---

## 19. Síntesis final

Con base en:

- `/home/jp/Upla/tutor_apoe/desk/atoms/tag-namespaces.yaml`
- `/home/jp/Upla/tutor_apoe/docs/diagrams/apos-atom-taxonomy.md`
- `/home/jp/proyectos/hum-ecosystem/tools/ontomap/README.md`
- `/home/jp/proyectos/hum-ecosystem/tools/kgdb/README.md`
- `/home/jp/proyectos/hum-ecosystem/tools/sldb/README.md`
- `/home/jp/proyectos/hum-ecosystem/tools/marcado/README.md`
- `/home/jp/proyectos/hum-ecosystem/tools/tractatusIR/README.md`

la conclusión es:

> el sistema de tags actual es útil, pero insuficiente como estructura semántica principal.

La taxonomía de átomos ya existente debe reinterpretarse como semilla de un **grafo conceptual explícito**.

Y ese grafo conceptual debe conectarse con:

- el grafo de provenance
- el grafo estructural derivado de ASTs y otras proyecciones

En una frase:

> los tags deben seguir sirviendo para facetado y retrieval ligero, pero la semántica conceptual profunda del átomo debe vivir en un grafo conceptual explícito, conectado tanto a la evidencia como a la estructura.
