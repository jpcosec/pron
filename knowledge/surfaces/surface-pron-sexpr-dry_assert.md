---
id: surface-pron-sexpr-dry_assert
system: pron
surface: sexpr.dry_assert
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/dry_assert.py
---

# sexpr.dry_assert

## Purpose

Simulating a new edge (spec 11 §7, spec 03): would this relation hold?

## How It Works

The projection has to allow asserting it at all, the classes of both sides have to be the
ones the relation type declares, the cardinality has to leave room for one more, and the
relation type's condition has to hold over the payloads this move would leave. A side that
is still `$created` has no document yet, so cardinality is not asked of it.

## Commands

DryAssert
