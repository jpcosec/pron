---
id: task-implement-canonical-write-ops-create-assert-ingest
status: draft
summary: ''
tags:
- workspace:desk
- artifact:task
routine: routine-task-implement-canonical-write-ops-create-assert-ingest
current_node: checklist-task-implement-canonical-write-ops-create-assert-ingest-execution-ready
history: []
references: []
depends_on:
- task-implement-knowledge-anchor-add
pills: []
files: []
checklists:
- checklist-task-implement-canonical-write-ops-create-assert-ingest-execution-ready
- checklist-task-implement-canonical-write-ops-create-assert-ingest-testing-ready
- checklist-task-implement-canonical-write-ops-create-assert-ingest-closeout-ready
task_type: implementation
inherits_from: []
inherit_acceptance_context: false
atoms:
- atom-write-operations-record-provenance-of-the-command-that-produced-them
- atom-knowledge-core-is-a-semantically-anchored-s-expression-evaluator
---

# Implement canonical write ops (create, assert, ingest)

## Rationale

_Explain why this task exists or the business driver behind it._

El spec KNOWLEDGE_CORE_SEMANTIC_ANCHORING define assert/create/ingest/return; solo check/next/return existen. Sin escritura el CLI es un lector de solo-lectura.

## Goal

_Describe the concrete result this task must produce._

Implementar las operaciones de escritura canónicas como anchors kind=operation con implementación en ops/write.py: (create ...) define entidades (symbol/relation/modelo/doc), (assert ...) añade un hecho como verdadero, (ingest ...) registra una proposicion/documento. Toda escritura debe ir vía sldb document/field operations y registrar provenance: el s-expr evaluado completo que produjo el cambio (atom-write-operations-record-provenance-of-the-command-that-produced-them, hoy impl:pending -> voltear a impl:here). Declarar los AnchorDocs anchor-create.md, anchor-assert.md, anchor-ingest.md.

## Scope

_State what is in scope and what is out of scope._

src/knowledge/ops/ (nuevo write.py), src/knowledge/core/evaluator.py (despacho de los verbos), knowledge/anchors/, knowledge/atoms/ (voltear impl del atom de provenance), tests/

## Implementation Path

_Outline the expected implementation route or affected surface._

1. Leer ops/read.py como patrón de operación (firma check(evaluator, args, projection)). 2. ops/write.py con create/assert/ingest escribiendo vía sldb bridge (ver bridges/sldb_bridge.py). 3. provenance: guardar en el frontmatter del doc producido el s-expr serializado (serialize del sexpr parser) + timestamp. 4. Despachar los verbos en evaluator.py según anchor kind=operation ref op:<fn>. 5. Tras cada write disparar rebuild de índices + graph. 6. Test con store temporal (--kb) verificando roundtrip: assert -> return recupera el hecho; provenance contiene el comando.

## Validation

_List the checks required before this task can close._

- python -m pytest tests -q

## Done When

_Name the observable condition that makes the task complete._

assert/create/ingest evaluables via 'knowledge eval' crean docs en el store con provenance del comando; 'return' los recupera; atom-write-operations-record-provenance pasa a impl:here; pytest verde
