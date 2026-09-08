---
id: surface-pron-ops-write
system: pron
surface: pron.ops.write
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
provenance: src/pron/ops/write.py
---

# pron.ops.write

## Purpose

Write operations: create, assert, ingest

## How It Works

atom-the-canonical-operations-are-check-next-assert-create-ingest-return: The core operation set is: check (evaluate or read without mutation), next (the next element by state, order defined by the model), assert (add a fact as true), create (define entities: symbols, relations, models, docs), ingest (register a proposition or document), and return (query stored facts). Reads project payloads from sldb/kgdb; writes go through sldb with provenance.

atom-write-operations-record-provenance-of-the-command-that-produced-them: Every write operation (assert, create, ingest) goes through sldb document and field operations and records the evaluated command as provenance. This is SHRDLU's action memory made auditable: any stored fact can be traced back to the exact expression, anchors, and referents that produced it.

## Commands

create(evaluator, args: list, projection, command: str='') | (create <model-sym> "name" <key> <value> ...): define a tracked doc.

Entity creation for symbols/relations/models is the anchor/model infra
(pron anchor add / model add); create here defines doc entities of
any registered model.
assert_(evaluator, args: list, projection, command: str='') | (assert "hecho" <key> <value> ...): añade un hecho como verdadero.
ingest(evaluator, args: list, projection, command: str='') | (ingest "título" "cuerpo"): registra una proposición/documento.
