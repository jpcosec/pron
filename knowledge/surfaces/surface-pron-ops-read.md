---
id: surface-pron-ops-read
system: pron
surface: pron.ops.read
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
provenance: src/pron/ops/read.py
---

# pron.ops.read

## Purpose

Read operations: check, next, return

## How It Works

atom-the-canonical-operations-are-check-next-assert-create-ingest-return: The core operation set is: check (evaluate or read without mutation), next (the next element by state, order defined by the model), assert (add a fact as true), create (define entities: symbols, relations, models, docs), ingest (register a proposition or document), and return (query stored facts). Reads project payloads from sldb/kgdb; writes go through sldb with provenance.

atom-every-read-response-carries-refs-for-auditability: Every read result includes the refs (document paths and graph node ids) that produced it, so any answer can be audited back to the exact tracked documents and edges. JSON is the default output for agents and pipes; text is a projection.

## Commands

check(evaluator, args: list, projection) | Read without mutation: docs sets, single docs, or rel traversals.
next_(evaluator, args: list, projection) | The next document by state order (model-defined; default: name order).
return_(evaluator, args: list, projection) | Query stored facts; alias of check over its argument for the read core.
