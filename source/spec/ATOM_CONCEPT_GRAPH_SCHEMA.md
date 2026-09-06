# Atom Concept Graph Schema

## Estado
Draft

## Propósito
Proponer un esquema inicial de nodos y edges para el grafo conceptual centrado en átomos.

Este documento complementa:

- `/home/jp/Upla/source/spec/ATOM_CONCEPT_GRAPH.md`
- `/home/jp/Upla/source/spec/GRAPH_ARCHITECTURE.md`
- `/home/jp/Upla/source/spec/MULTI_SOURCE_ANCHORING.md`

Y toma como fuentes principales:

- `/home/jp/Upla/tutor_apoe/desk/atoms/tag-namespaces.yaml`
- `/home/jp/Upla/tutor_apoe/docs/diagrams/apos-atom-taxonomy.md`

---

## 1. Criterio general

El esquema debe distinguir explícitamente entre:

- nodos del backbone de provenance
- nodos conceptuales
- nodos estructurales proyectados
- facets ligeras de tag

No todo debe reducirse a `Tag`.

---

## 2. Node types

## 2.1 Backbone nodes

### `Source`
Representa una fuente registrada y versionada.

Campos sugeridos:
- `id`
- `kind`
- `locator`
- `version_binding`
- `content_hash`
- `title`

### `Sample`
Representa una biopsia / sample verificable.

Campos sugeridos:
- `id`
- `source_id`
- `projection_kind`
- `validation_state`
- `excerpt`
- `anchor_bundle_ref` o payload resumido

### `Atom`
Representa una unidad atómica de conocimiento.

Campos sugeridos:
- `id`
- `title`
- `question_type`
- `answer`
- `status` opcional

### `Composition`
Representa una composición, síntesis o vista derivada.

Campos sugeridos:
- `id`
- `title`
- `kind`
- `summary`

---

## 2.2 Conceptual nodes

### `Concept`
Concepto explícito del dominio.

Campos sugeridos:
- `id`
- `label`
- `slug`
- `description`
- `domain` opcional

Ejemplos APOS:
- `concept.action`
- `concept.encapsulation`
- `concept.genetic_decomposition`
- `concept.ace_cycle`

### `ConceptGroup`
Agrupación de alto nivel.

Campos sugeridos:
- `id`
- `label`
- `slug`
- `description`

Ejemplos APOS derivados de `/home/jp/Upla/tutor_apoe/docs/diagrams/apos-atom-taxonomy.md`:
- `group.foundations`
- `group.core_structures`
- `group.mechanisms`
- `group.research`
- `group.mathematical_domains`

### `TaxonomyNode`
Nodo del árbol conceptual/navegacional.

Campos sugeridos:
- `id`
- `path`
- `label`
- `slug`
- `group_id` opcional
- `parent_id` opcional

Ejemplos:
- `tax.apos.core_structures.action`
- `tax.apos.mechanisms.encapsulation`
- `tax.apos.research.paradigm`

### `QuestionType`
Categorías 5WH1+.

Campos sugeridos:
- `id`
- `code`
- `label`

Valores esperados:
- `what`
- `why`
- `how`
- `how_not`
- `when`
- `where`
- `for_whom`

### `TagFacet`
Facet ligera derivada del sistema de tags.

Campos sugeridos:
- `id`
- `namespace`
- `value`
- `raw_tag`

Ejemplos:
- `facet.system.apos`
- `facet.topic.action`
- `facet.layer.research`
- `facet.domain.mathematics_education`

---

## 2.3 Structural nodes

### `SourceSection`
Sección significativa de una fuente.

Campos sugeridos:
- `id`
- `source_id`
- `title`
- `path`
- `level`

### `Symbol`
Entidad estructural en código u otra fuente parseable.

Campos sugeridos:
- `id`
- `source_id`
- `symbol_kind`
- `qualified_name`
- `path`

### `StructureNode`
Nodo estructural genérico proyectado desde una estructura documental.

Campos sugeridos:
- `id`
- `source_id`
- `structure_kind`
- `path`
- `label`

### `ASTNode`
Nodo AST persistido selectivamente.

Campos sugeridos:
- `id`
- `source_id`
- `ast_kind`
- `node_type`
- `path`

### `LayoutRegion`
Región espacial relevante de una fuente con layout.

Campos sugeridos:
- `id`
- `source_id`
- `page`
- `region_kind`
- `bbox`

---

## 3. Edge types

## 3.1 Provenance edges

### `sampled_from`
- `Sample -> Source`

### `distilled_from`
- `Atom -> Sample`

### `supports`
- `Sample -> Atom`

### `composes`
- `Composition -> Atom`

### `derived_from`
- `Composition -> Atom | Sample | Source`

---

## 3.2 Conceptual edges

### `about_concept`
- `Atom -> Concept`
- principal conceptual target

### `secondary_about`
- `Atom -> Concept`
- conceptos secundarios

### `located_in_taxonomy`
- `Atom -> TaxonomyNode`
- ubicación conceptual principal

### `grouped_under`
- `TaxonomyNode -> ConceptGroup`

### `child_of`
- `TaxonomyNode -> TaxonomyNode`
- jerarquía del árbol taxonómico

### `subconcept_of`
- `Concept -> Concept | ConceptGroup`
- jerarquía semántica más abstracta

### `has_question_type`
- `Atom -> QuestionType`

### `tagged_with`
- `Entity -> TagFacet`
- retrieval facetado, no ontología principal

### `related_to`
- `Atom -> Atom | Concept`
- relación asociativa controlada

### `contrasts_with`
- `Atom -> Atom | Concept`

### `depends_on`
- `Atom -> Atom`
- dependencia conceptual o composicional

### `extends`
- `Atom -> Atom | Concept`

### `elaborates`
- `Atom -> Atom`

### `applies_to`
- `Atom -> Concept | TaxonomyNode`
- útil para casos como teoría -> dominio matemático

### `instance_of`
- `TaxonomyNode -> Concept`
- opcional si se quiere separar claramente concepto abstracto de ubicación taxonómica

---

## 3.3 Structural edges

### `anchored_in`
- `Sample -> SourceSection | StructureNode | ASTNode | LayoutRegion | Symbol`

### `drawn_from_section`
- `Sample -> SourceSection`

### `mentions_symbol`
- `Sample | Atom -> Symbol`

### `supported_by_structure`
- `Atom -> SourceSection | StructureNode | ASTNode | LayoutRegion | Symbol`

### `has_section`
- `Source -> SourceSection`

### `has_symbol`
- `Source -> Symbol`

### `has_ast_node`
- `Source -> ASTNode`

### `has_layout_region`
- `Source -> LayoutRegion`

---

## 4. Entity identity guidance

## 4.1 Source identity

Debe estar ligada a binding de versión, no solo nombre humano.

## 4.2 Sample identity

Debe ser estable a nivel de KB y no depender solo del path local del archivo sample.

## 4.3 Atom identity

Debe conservar el patrón de id estable de la disciplina actual.

## 4.4 Concept identity

Conviene usar ids semánticos durables, no solo labels:
- `concept.action`
- `concept.reflective_abstraction`

## 4.5 TaxonomyNode identity

Conviene usar ids derivados de path conceptual:
- `tax.apos.mechanisms.encapsulation`

## 4.6 TagFacet identity

Conviene normalizar a:
- `facet.<namespace>.<value_normalized>`

---

## 5. Mapping from current APOS materials

## 5.1 From `tag-namespaces.yaml`

Archivo fuente:
- `/home/jp/Upla/tutor_apoe/desk/atoms/tag-namespaces.yaml`

Mapeo sugerido:

- namespace definitions -> schema/rules for `TagFacet`
- concrete tags -> `TagFacet` nodes

Ejemplo:
- `topic:action` -> `TagFacet(id="facet.topic.action", namespace="topic", value="action")`

## 5.2 From `apos-atom-taxonomy.md`

Archivo fuente:
- `/home/jp/Upla/tutor_apoe/docs/diagrams/apos-atom-taxonomy.md`

Mapeo sugerido:

- top categories -> `ConceptGroup`
- subtree paths -> `TaxonomyNode`
- some stable subject names -> `Concept`

Ejemplo:
- `Mechanisms` -> `ConceptGroup`
- `apos/mechanisms/encapsulation` -> `TaxonomyNode`
- `Encapsulation` -> `Concept`

## 5.3 From atoms

Ejemplo conceptual:
- atom file id -> `Atom.id`
- `five_wh_one_plus` -> `has_question_type`
- tags -> `tagged_with`
- folder location -> initial `located_in_taxonomy`
- title/answer -> atom payload

---

## 6. Recommended minimal first implementation

Si se quiere empezar sin sobrecargar el sistema, el mínimo útil sería:

### Nodes
- `Source`
- `Sample`
- `Atom`
- `Composition`
- `ConceptGroup`
- `TaxonomyNode`
- `QuestionType`
- `TagFacet`

### Optional in phase 1
- `Concept`

### Optional in phase 2
- `SourceSection`
- `Symbol`
- `StructureNode`
- `ASTNode`
- `LayoutRegion`

### Minimal edges
- `sampled_from`
- `distilled_from`
- `composes`
- `located_in_taxonomy`
- `has_question_type`
- `tagged_with`
- `child_of`
- `grouped_under`

Esto ya permitiría:
- provenance básica
- retrieval por taxonomy
- retrieval por question type
- facets de tag
- navegación conceptual inicial

---

## 7. Why not tags only

Porque un sistema solo de tags no representa bien:

- jerarquías
- relaciones entre conceptos
- ubicación conceptual fuerte
- vecindades semánticas explícitas
- relaciones átomo-átomo más allá de co-tagging

Los tags son útiles como surface ligera.
Pero el esquema del grafo debe cargar la semántica fuerte.

---

## 8. Short synthesis

Este esquema propone que:

- los tags sobrevivan como `TagFacet`
- la taxonomía sobreviva como `ConceptGroup + TaxonomyNode`
- los conceptos emerjan como `Concept`
- la atomicidad 5WH1+ sobreviva como `QuestionType`
- provenance y estructura se conecten sin colapsar todo en una sola categoría semántica
