---
id: task-auto-refresh-indexes-and-graph-after-writes
status: draft
summary: ''
tags:
- workspace:desk
- artifact:task
routine: routine-task-auto-refresh-indexes-and-graph-after-writes
current_node: checklist-task-auto-refresh-indexes-and-graph-after-writes-execution-ready
history: []
references:
- 004019b
- tests/test_anchor_add.py
- tests/test_write_ops.py
- tests/test_refresh.py
- atom-write-operations-record-provenance-of-the-command-that-produced-them
depends_on:
- task-implement-knowledge-anchor-add
pills: []
files: []
checklists:
- checklist-task-auto-refresh-indexes-and-graph-after-writes-execution-ready
- checklist-task-auto-refresh-indexes-and-graph-after-writes-testing-ready
- checklist-task-auto-refresh-indexes-and-graph-after-writes-closeout-ready
task_type: implementation
inherits_from: []
inherit_acceptance_context: false
atoms:
- atom-a-zero-edge-graph-snapshot-should-be-treated-as-an-incomplete-provenance-build-rather-than-a-healthy-graph
---

# Auto-refresh indexes and graph after writes

## Rationale

_Explain why this task exists or the business driver behind it._

Tras cualquier escritura, el evaluator y kgdb leerian un grafo/indices viejos si no se reconstruyen; atom-a-zero-edge-graph-snapshot exige provenance de build, no grafos podridos.

## Goal

_Describe the concrete result this task must produce._

Centralizar el post-write hook: despues de anchor add, create, assert, ingest, regenerar los indices sldb (semantic/section) y el snapshot kgdb (.sldb/runtime/graphs/deskops.kg.json) en una sola llamada reutilizable (p.ej. infra.refresh(root)) usada por cli/main.py y ops/write.py; evitando duplicar la logica de rebuild.

## Scope

_State what is in scope and what is out of scope._

src/knowledge/infra/ (nuevo refresh o extension de projector.py), src/knowledge/cli/main.py, src/knowledge/ops/

## Implementation Path

_Outline the expected implementation route or affected surface._

1. Extraer la logica de rebuild que ya exista (project en infra/projector.py, snapshot en deskops graph build). 2. infra.refresh(root): reindex sldb + kgdb build, retornando estado. 3. Llamarla tras cada operacion de escritura. 4. Test: escribir y verificar que el snapshot cambia y los indices encuentran el doc nuevo.

## Validation

_List the checks required before this task can close._

- python -m pytest tests -q

## Done When

_Name the observable condition that makes the task complete._

Toda operacion de escritura deja indices y grafo consistentes sin comando manual; pytest verde
