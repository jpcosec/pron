---
# board-xxx
id: board-001
# Affected workspace or domain
scope: desk
# List of task-xxx paths
tasks:
- desk/tasks/task-implement-knowledge-anchor-add.md
- desk/tasks/task-implement-canonical-write-ops-create-assert-ingest.md
- desk/tasks/task-auto-refresh-indexes-and-graph-after-writes.md
# List of pill-xxx paths
pills:
- desk/contexts/pills.md
# List of ritual-xxx paths
rituals:
- desk/rituals/execution.md
- desk/rituals/testing.md
- desk/rituals/closeout.md
# e.g., system:sldb, workspace:desk
tags:
- workspace:desk
---

# Upla Board

## Purpose

_Explain what this board routes and why it exists._



## Notes

_Add short operational notes about the current routed set._

- Implement knowledge anchor add [draft] - Implementar 'knowledge anchor add <symbol> --kind <model|doc|relation|operation|projection> --ref <typed-ref> --motive <text>' que crea un AnchorDoc sldb en knowledge/anchors/ con frontmatter id/symbol/kind/ref/tags/provenance y seccion ## Motive; validar ref por regex segun kind (model:<Name>, doc:<name>, edge:<rel>[:dir], op:<fn>, fields:<f1,f2>, view:<name>); rechazar kinds fuera de la particion; disparar reindex sldb + graph rebuild (project) tras escribir; anadir anchor para el nuevo verbo (anchor-add.md) para que el surface grammar lo reconozca.
- Implement canonical write ops (create, assert, ingest) [draft] - Implementar las operaciones de escritura canónicas como anchors kind=operation con implementación en ops/write.py: (create ...) define entidades (symbol/relation/modelo/doc), (assert ...) añade un hecho como verdadero, (ingest ...) registra una proposicion/documento. Toda escritura debe ir vía sldb document/field operations y registrar provenance: el s-expr evaluado completo que produjo el cambio (atom-write-operations-record-provenance-of-the-command-that-produced-them, hoy impl:pending -> voltear a impl:here). Declarar los AnchorDocs anchor-create.md, anchor-assert.md, anchor-ingest.md.

## Task Details

_Generated from the task references above._

- Implement knowledge anchor add [draft] - Implementar 'knowledge anchor add <symbol> --kind <model|doc|relation|operation|projection> --ref <typed-ref> --motive <text>' que crea un AnchorDoc sldb en knowledge/anchors/ con frontmatter id/symbol/kind/ref/tags/provenance y seccion ## Motive; validar ref por regex segun kind (model:<Name>, doc:<name>, edge:<rel>[:dir], op:<fn>, fields:<f1,f2>, view:<name>); rechazar kinds fuera de la particion; disparar reindex sldb + graph rebuild (project) tras escribir; anadir anchor para el nuevo verbo (anchor-add.md) para que el surface grammar lo reconozca.
- Implement canonical write ops (create, assert, ingest) [draft] - Implementar las operaciones de escritura canónicas como anchors kind=operation con implementación en ops/write.py: (create ...) define entidades (symbol/relation/modelo/doc), (assert ...) añade un hecho como verdadero, (ingest ...) registra una proposicion/documento. Toda escritura debe ir vía sldb document/field operations y registrar provenance: el s-expr evaluado completo que produjo el cambio (atom-write-operations-record-provenance-of-the-command-that-produced-them, hoy impl:pending -> voltear a impl:here). Declarar los AnchorDocs anchor-create.md, anchor-assert.md, anchor-ingest.md.
- Auto-refresh indexes and graph after writes [draft] - Centralizar el post-write hook: despues de anchor add, create, assert, ingest, regenerar los indices sldb (semantic/section) y el snapshot kgdb (.sldb/runtime/graphs/deskops.kg.json) en una sola llamada reutilizable (p.ej. infra.refresh(root)) usada por cli/main.py y ops/write.py; evitando duplicar la logica de rebuild.
