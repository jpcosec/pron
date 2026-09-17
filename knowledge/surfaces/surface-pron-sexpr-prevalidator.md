---
id: surface-pron-sexpr-prevalidator
system: pron
surface: sexpr.prevalidator
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/prevalidator.py
---

# sexpr.prevalidator

## Purpose

Spec 11 §7: before the first write of a move, every write of the move is checked.

## How It Works

Coercion, state-machine transition, relation type, cardinality, condition and the sldb
roundtrip are all computed over an overlay — the payloads the earlier writes of the same
move would leave — so a move that would fail halfway fails before it touches anything.
The check raises StoreError; whatever the verbs verified on the way is put in the trace
and in the move's queries, whether the check passed or not.

## Commands

Prevalidator
