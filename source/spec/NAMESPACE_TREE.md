# Namespace Tree

## Estado
Draft

## Propósito
Proponer un árbol de namespaces sobre todo lo trabajado hasta ahora en `/home/jp/Upla/kb/spec`.

Este documento usa forma de árbol solo como proyección de trabajo.
No afirma que los namespaces formen una jerarquía única y fija.

La estructura real es mejor entendida como un conjunto de facetas o anillos
relacionados: cada namespace recorta una dimensión distinta del KB y desde
cada dimensión pueden derivarse árboles útiles.

Este árbol no es todavía un schema técnico definitivo.
Su función es:

- dar un mapa semántico coherente
- separar dominios y subdominios
- evitar que tags/ids futuros se vuelvan arbitrarios
- servir como base para:
  - `TagFacet`
  - `Concept`
  - `TaxonomyNode`
  - nodos de grafo
  - ids semánticos
  - clasificación documental

Este árbol está construido a partir de los documentos ya producidos:

- `/home/jp/Upla/source/spec/KB_SYSTEM_SPEC.md`
- `/home/jp/Upla/source/spec/KB_SYSTEM_CLARIFICATIONS.md`
- `/home/jp/Upla/source/spec/MULTI_SOURCE_ANCHORING.md`
- `/home/jp/Upla/source/spec/GRAPH_ARCHITECTURE.md`
- `/home/jp/Upla/source/spec/ATOM_CONCEPT_GRAPH.md`
- `/home/jp/Upla/source/spec/ATOM_CONCEPT_GRAPH_SCHEMA.md`
- `/home/jp/Upla/source/spec/BOOTSTRAP_KB_WITH_CURRENT_DESKOPS.md`
- `/home/jp/Upla/source/spec/LEGACY_EXTRACTION_FROM_HUM_ECOSYSTEM.md`
- `/home/jp/Upla/source/spec/DESKOPS_FOR_KNOWLEDGE_MANAGEMENT.md`
- `/home/jp/Upla/source/spec/THREE_GRAPH_MODEL_DIAGRAMS.md`
- `/home/jp/Upla/source/spec/source_apps/*`

---

## 1. Principio general

El árbol distingue varias familias semánticas de primer nivel.

### Familias principales
- `system`
- `layer`
- `entity`
- `relation`
- `source`
- `projection`
- `anchor`
- `graph`
- `concept`
- `workflow`
- `view`
- `app`
- `legacy`
- `bootstrap`

La idea es que no todo se meta en `topic:*`.
Cada familia expresa un tipo distinto de cosa.

## Uso mínimo actual

Para authoring y revisión corriente, la superficie mínima útil hoy es:

- `system:*`
- `topic:*`
- `layer:*` cuando aporta ubicación arquitectónica real
- `entity:*` cuando aclara qué cosa se está modelando
- `graph:*` cuando la afirmación trata una estratificación de grafo
- `domain:*` cuando la afirmación cruza un dominio más amplio

En cambio, `project:*`, `source:*`, `source_kind:*`, `grounding:*`, `status:*`,
`role:*` y namespaces equivalentes pertenecen primariamente al metadata
registry del átomo cuando describen curación, origen o estado editorial.

---

## 2. Árbol maestro

```text
system/
  kb/
    provenance/
    multi_source/
    atom_based/
    composition/
    graph_enabled/
    document_first/
  deskops/
  sldb/
  marcado/
  kgdb/
  ontomap/
  graph_ui/
  sldb_ui/
  spec2viz/
  hum_scrapper/
  tractatus_ir/
  repopackage/
  hum_ecosystem/

layer/
  source/
  projection/
  structure/
  anchoring/
  sample/
  markup/
  atom/
  composition/
  graph/
    provenance/
    concept/
    structure/
  retrieval/
  materialization/
  workflow/
  ui/
  cli/
  store/

entity/
  source/
    record/
    artifact/
    snapshot/
    section/
  sample/
    biopsy/
    excerpt/
    evidence/
  atom/
    knowledge_atom/
    answer_unit/
  composition/
    synthesis/
    faq/
    report/
    derived_view/
  concept/
    concept/
    concept_group/
    taxonomy_node/
    tag_facet/
    question_type/
  structure/
    ast_node/
    structure_node/
    symbol/
    layout_region/
    dom_node/
    heading/
    block/
  workflow/
    task/
    review_item/
    queue_item/

relation/
  provenance/
    sampled_from/
    distilled_from/
    supports/
    derived_from/
    composes/
    anchored_in/
  concept/
    about_concept/
    secondary_about/
    located_in_taxonomy/
    grouped_under/
    child_of/
    subconcept_of/
    has_question_type/
    tagged_with/
    related_to/
    contrasts_with/
    depends_on/
    extends/
    elaborates/
    applies_to/
    instance_of/
  structure/
    has_section/
    has_symbol/
    has_ast_node/
    has_layout_region/
    drawn_from_section/
    mentions_symbol/
    supported_by_structure/

source/
  kind/
    pdf/
    webpage/
    markdown/
    text/
    code_file/
    git_repo/
    git_commit/
    git_blob/
    json/
    yaml/
    notebook/
    api_snapshot/
    export/
  binding/
    path/
    url/
    hash/
    commit/
    blob/
    locator/
  retrieval/
    local_file/
    remote_fetch/
    repo_checkout/
    snapshot_capture/

projection/
  text/
    raw_text/
    normalized_text/
    reading_order_text/
  ast/
    code_ast/
    mdast/
    dom_ast/
    object_tree/
  document/
    heading_tree/
    section_tree/
    block_tree/
    symbol_table/
    repo_tree/
  layout/
    page/
    reading_block/
    coordinate_region/
  metadata/
    parser_metadata/
    extraction_metadata/
    source_metadata/

anchor/
  bundle/
    structural/
    textual/
    positional/
    contextual/
  structural/
    ast_path/
    dom_selector/
    heading_path/
    object_path/
    symbol_path/
    block_id/
    section_path/
  textual/
    exact_quote/
    normalized_quote/
    anchor_text/
  positional/
    line_range/
    char_offset/
    page_range/
    coordinates/
  contextual/
    prefix/
    suffix/
    parent_heading/
    surrounding_nodes/
    containing_symbol/
  validation/
    source_identity/
    structural/
    textual/
    contextual/

graph/
  provenance/
    source_sample_atom_composition/
  concept/
    atom_concept_taxonomy/
  structure/
    source_section_symbol_ast_layout/
  retrieval/
    lineage/
    support/
    coverage/
    topic_navigation/
    structural_queries/
  materialization/
    concept_map/
    lineage_map/
    coverage_map/
    dependency_view/

authoring/
  atom_discipline/
    one_question/
    five_wh_one_plus/
    composability/
    stable_answer/
  sample_discipline/
    verifiable_excerpt/
    source_binding/
    annotation_surface/
  composition_discipline/
    depth_by_composition/
    not_atom_inflation/

workflow/
  bootstrap/
    deskops_corpus/
    provenance_minimum/
    taxonomy_extraction/
    gradual_enrichment/
  review/
    curation/
    validation/
    coverage/
    migration/
  operations/
    board/
    task/
    ritual/
    queue/

view/
  document/
    source_view/
    rendered_view/
    annotated_sample_view/
    provenance_view/
    ast_view/
  graph/
    lineage_graph/
    concept_graph/
    support_graph/
    coverage_graph/
  derived/
    dashboard/
    report/
    diagram/
    conceptual_map/

app/
  source_apps/
    deskops/
    sldb/
    marcado/
    kgdb/
    ontomap/
    sldb_ui/
    graph_ui/
    spec2viz/
    hum_scrapper/
    tractatus_ir/
    repopackage/

legacy/
  hum_ecosystem/
    kg_trees/
    knowledge_structure_challenge/
    nl_sl_kg_pipeline/
    universal_knowledge_loop/
    knowledge_organ/
    graphlang/
    hum_core/

bootstrap/
  current_deskops/
    atomdoc/
    tag_facets/
    taxonomy_path/
    provenance_text/
    grounding_status/
    future_sample_link/
```

---

## 3. Tree by semantic role

## 3.1 System namespaces

Usar para identificar sistemas o subsistemas concretos.

```text
system:kb
system:deskops
system:sldb
system:marcado
system:kgdb
system:ontomap
system:graph_ui
system:sldb_ui
system:spec2viz
system:hum_scrapper
system:tractatus_ir
system:repopackage
system:hum_ecosystem
```

## 3.2 Layer namespaces

Usar para ubicar una cosa dentro de la arquitectura.

```text
layer:source
layer:projection
layer:structure
layer:anchoring
layer:sample
layer:markup
layer:atom
layer:composition
layer:graph
layer:retrieval
layer:materialization
layer:workflow
layer:ui
layer:cli
layer:store
```

Subcapas de grafo:

```text
layer:graph.provenance
layer:graph.concept
layer:graph.structure
```

## 3.3 Entity namespaces

Usar para tipar entidades del modelo.

```text
entity:source
entity:sample
entity:atom
entity:composition
entity:concept
entity:concept_group
entity:taxonomy_node
entity:tag_facet
entity:question_type
entity:source_section
entity:symbol
entity:structure_node
entity:ast_node
entity:layout_region
entity:workflow_item
```

## 3.4 Relation namespaces

Usar para relaciones explícitas del grafo.

```text
relation:sampled_from
relation:distilled_from
relation:supports
relation:derived_from
relation:composes
relation:anchored_in
relation:about_concept
relation:secondary_about
relation:located_in_taxonomy
relation:grouped_under
relation:child_of
relation:subconcept_of
relation:has_question_type
relation:tagged_with
relation:related_to
relation:contrasts_with
relation:depends_on
relation:extends
relation:elaborates
relation:applies_to
relation:instance_of
relation:has_section
relation:has_symbol
relation:has_ast_node
relation:has_layout_region
relation:drawn_from_section
relation:mentions_symbol
relation:supported_by_structure
```

---

## 4. Namespaces for source kinds

Esto sale directamente del trabajo de multi-source anchoring.

```text
source:pdf
source:webpage
source:markdown
source:text
source:code_file
source:git_repo
source:git_commit
source:git_blob
source:json
source:yaml
source:notebook
source:api_snapshot
source:export
```

## Namespaces de binding / locator

```text
source_binding:path
source_binding:url
source_binding:hash
source_binding:commit
source_binding:blob
source_binding:locator
```

---

## 5. Namespaces for projections

Como AST es categoría de primer nivel, eso debe verse también aquí.

```text
projection:text
projection:text.raw
projection:text.normalized
projection:text.reading_order

projection:ast
projection:ast.code
projection:ast.markdown
projection:ast.dom
projection:ast.object_tree

projection:document
projection:document.heading_tree
projection:document.section_tree
projection:document.block_tree
projection:document.symbol_table
projection:document.repo_tree

projection:layout
projection:layout.page
projection:layout.reading_block
projection:layout.coordinate_region

projection:metadata
projection:metadata.parser
projection:metadata.extraction
projection:metadata.source
```

---

## 6. Namespaces for anchors

```text
anchor_bundle:structural
anchor_bundle:textual
anchor_bundle:positional
anchor_bundle:contextual

anchor:ast_path
anchor:dom_selector
anchor:heading_path
anchor:object_path
anchor:symbol_path
anchor:block_id
anchor:section_path
anchor:exact_quote
anchor:normalized_quote
anchor:anchor_text
anchor:line_range
anchor:char_offset
anchor:page_range
anchor:coordinates
anchor:prefix
anchor:suffix
anchor:parent_heading
anchor:surrounding_nodes
anchor:containing_symbol
```

## Validation namespaces

```text
anchor_validation:source_identity
anchor_validation:structural
anchor_validation:textual
anchor_validation:contextual
```

---

## 7. Namespaces for graph strata

Esto resume el modelo de tres grafos.

```text
graph:provenance
graph:concept
graph:structure
graph:retrieval
graph:materialization
```

## Provenance graph scope

```text
graph_scope:source_sample_atom_composition
```

## Concept graph scope

```text
graph_scope:atom_concept_taxonomy
```

## Structural graph scope

```text
graph_scope:source_section_symbol_ast_layout
```

---

## 8. Namespaces for authoring discipline

Estos sirven para codificar reglas que ya surgieron en los docs.

```text
authoring:atom_discipline
authoring:sample_discipline
authoring:composition_discipline
```

Subreglas sugeridas:

```text
authoring:atom.one_question
authoring:atom.five_wh_one_plus
authoring:atom.composability
authoring:atom.stable_answer

authoring:sample.verifiable_excerpt
authoring:sample.source_binding
authoring:sample.annotation_surface

authoring:composition.depth_by_composition
authoring:composition.not_atom_inflation
```

---

## 9. Namespaces for bootstrap / transición

Esto es importante para no mentir ni congelar mal el presente.

```text
bootstrap:current_deskops
bootstrap:atomdoc
bootstrap:tag_facets
bootstrap:taxonomy_path
bootstrap:provenance_text
bootstrap:grounding_status
bootstrap:future_sample_link
```

## Grounding status tree sugerido

```text
grounding:none
grounding:textual_only
grounding:located_humanly
grounding:sample_linked
grounding:validated
```

---

## 10. Namespaces for legacy extraction

Esto permite marcar ideas heredadas de `hum-ecosystem` sin mezclarlas con categorías de producción final.

```text
legacy:hum_ecosystem
legacy:kg_trees
legacy:knowledge_structure_challenge
legacy:nl_sl_kg_pipeline
legacy:universal_knowledge_loop
legacy:knowledge_organ
legacy:graphlang
legacy:hum_core
```

---

## 11. Namespaces for source apps reviewed

```text
app:deskops
app:sldb
app:marcado
app:kgdb
app:ontomap
app:sldb_ui
app:graph_ui
app:spec2viz
app:hum_scrapper
app:tractatus_ir
app:repopackage
```

---

## 12. Recommended usage guidance

## 12.1 Qué usar como facets ligeras

Buenos candidatos para tags ligeros:
- `system:*`
- `layer:*`
- `source:*`
- `projection:*`
- `app:*`

## 12.2 Qué no reducir solo a tags

No conviene dejar solo como tag:
- taxonomía conceptual profunda
- relaciones entre conceptos
- relaciones átomo-átomo
- provenance estructurada
- anchors
- soporte estructural

Eso debería vivir en nodos/edges explícitos.

## 12.3 Qué usar para ids semánticos

Buenos candidatos para ids/nodos:
- `entity:*`
- `relation:*`
- `graph:*`
- `concept:*` si luego se especializa más
- `taxonomy:*` si se crea un espacio separado

---

## 13. Candidate future specializations

Algunos namespaces seguramente querrán crecer más adelante.

## Conceptual specializations

Podrían aparecer más adelante árboles como:

```text
concept/
  apos/
    foundations/
    core_structures/
    mechanisms/
    pedagogy/
    research/
    applications/
```

O incluso una familia separada:

```text
taxonomy/
  apos/
    foundations/
    core_structures/
    mechanisms/
    research/
```

## Structural specializations

Podrían aparecer:

```text
structure/
  markdown/
  code/
  dom/
  pdf_layout/
  repo/
```

Pero todavía no hace falta fijarlo completamente.

---

## 14. Minimal practical subset for now

Si hubiera que empezar hoy con un subconjunto manejable, yo usaría primero:

```text
system:kb
system:deskops
system:sldb
system:marcado
system:kgdb

layer:atom
layer:graph.provenance
layer:graph.concept
layer:structure
layer:sample

entity:atom
entity:sample
entity:source
entity:composition
entity:taxonomy_node
entity:concept_group
entity:tag_facet
entity:question_type

relation:distilled_from
relation:sampled_from
relation:anchored_in
relation:located_in_taxonomy
relation:grouped_under
relation:has_question_type
relation:tagged_with

source:pdf
source:markdown
source:code_file
source:webpage
source:git_repo

projection:ast
projection:text
projection:document
projection:layout

grounding:textual_only
grounding:located_humanly
grounding:sample_linked
grounding:validated

bootstrap:current_deskops
```

---

## 15. Síntesis final

Este árbol de namespaces intenta corregir un problema que ya vimos en la historia previa del sistema:

- demasiada semántica comprimida en tags planos

La idea ahora es:

- usar namespaces como mapa semántico limpio
- distinguir familias de cosas distintas
- dejar que los tags ligeros sigan existiendo
- pero abrir el camino para nodos/edges más ricos

En una frase:

> el árbol de namespaces debe servir como puente entre el presente facetado de Deskops y la futura KB con provenance graph, concept graph y structural graph explícitos.
