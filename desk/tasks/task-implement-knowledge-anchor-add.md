---
id: task-implement-knowledge-anchor-add
status: ready_for_testing
summary: ''
tags:
- workspace:desk
- artifact:task
routine: routine-task-implement-knowledge-anchor-add
current_node: checklist-task-implement-knowledge-anchor-add-closeout-ready
history:
- operator-task-implement-knowledge-anchor-add-activate
- operator-task-implement-knowledge-anchor-add-ready-for-testing
references: []
depends_on: []
pills: []
files: []
checklists:
- checklist-task-implement-knowledge-anchor-add-execution-ready
- checklist-task-implement-knowledge-anchor-add-testing-ready
- checklist-task-implement-knowledge-anchor-add-closeout-ready
task_type: implementation
inherits_from: []
inherit_acceptance_context: false
atoms:
- atom-an-anchor-binds-a-symbol-to-a-semantic-motive-and-a-resolvable-referent
- atom-anchor-ref-is-a-typed-string-with-a-scheme-per-kind
- atom-anchor-kinds-partition-what-a-symbol-can-refer-to
- atom-the-anchor-table-is-declared-as-sldb-documents-not-code
- atom-anchors-py-loads-the-grammar-from-tracked-anchordocs
closeout_evidence_verified: false
pill_graduation_verified: true
---

# Implement knowledge anchor add

## Rationale

_Explain why this task exists or the business driver behind it._

El CLI sugiere 'knowledge anchor add' en cada error semántico pero el comando no existe; sin escritura el conocimiento no crece desde el evaluator.

## Goal

_Describe the concrete result this task must produce._

Implementar 'knowledge anchor add <symbol> --kind <model|doc|relation|operation|projection> --ref <typed-ref> --motive <text>' que crea un AnchorDoc sldb en knowledge/anchors/ con frontmatter id/symbol/kind/ref/tags/provenance y seccion ## Motive; validar ref por regex segun kind (model:<Name>, doc:<name>, edge:<rel>[:dir], op:<fn>, fields:<f1,f2>, view:<name>); rechazar kinds fuera de la particion; disparar reindex sldb + graph rebuild (project) tras escribir; anadir anchor para el nuevo verbo (anchor-add.md) para que el surface grammar lo reconozca.

## Scope

_State what is in scope and what is out of scope._

src/knowledge/cli/main.py, src/knowledge/core/anchors.py, src/knowledge/anchors/, tests/; NO modificar el evaluador ni los bridges

## Implementation Path

_Outline the expected implementation route or affected surface._

1. Leer knowledge/anchors/anchor-check.md como formato canónico y knowledge/core/anchors.py (AnchorRegistry, _load) para el contrato de lectura. 2. Añadir subcomando 'anchor add' en cli/main.py (junto a 'anchors'). 3. Validación regex del ref por kind (atom-anchor-ref-is-a-typed-string-with-a-scheme-per-kind). 4. Escribir el AnchorDoc vía escritura de doc sldb respetando frontmatter (id: anchor-<symbol>, symbol, kind, ref, tags: [system:knowledge, entity:anchor, domain:knowledge_representation, kind:software, impl:here], provenance). 5. Tras escribir, regenerar índices y snapshot kgdb. 6. Declarar anchor-add.md para el verbo add.

## Validation

_List the checks required before this task can close._

- python -m pytest tests -q
- python -m knowledge anchors | grep -c symbol

## Done When

_Name the observable condition that makes the task complete._

knowledge anchor add <sym> --kind op --ref 'op:f' --motive 'x' crea el AnchorDoc, 'knowledge anchors <sym>' lo lista con motive correcto, y 'knowledge eval' resuelve el símbolo nuevo sin semantic error; kinds/refs inválidos fallan con error explícito; pytest 44+ verde
