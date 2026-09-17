---
id: surface-pron-sexpr-execution-relation_write
system: pron
surface: sexpr.execution.relation_write
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/execution/relation_write.py
---

# sexpr.execution.relation_write

## Purpose

Writing one new edge in a move (spec 07, spec 11 §7, spec 04).

## How It Works

Asserting a relation writes a RelationDoc; a composition that asserts one writes the same
document the same way. Both go through here: the document is created with the naming
template the projection gives RelationDoc, the call is traced, and the write is recorded
in the move in one shape, so `undo` can invert either of them without knowing which said it.

## Commands

write_edge
relation_write
