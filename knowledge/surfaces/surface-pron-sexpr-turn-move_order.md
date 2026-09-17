---
id: surface-pron-sexpr-turn-move_order
system: pron
surface: sexpr.turn.move_order
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/turn/move_order.py
---

# sexpr.turn.move_order

## Purpose

The order the parts of one move run in (spec 06 §Coordinación, spec 13 §Sustantivos).

## How It Works

A move may create a document and, in the same breath, say something about it: "create a
client named Ana and book her a table". The creates with an explicit name are known before
anything runs — their export id is the name the form gave them — so a noun that says one of
them resolves without reading the store, and the part that says it is held back until the
create that makes it has run, even if the form said it first.

The order is a generator on purpose: each part is executed by whoever consumes it before
the next one is chosen, so "already done" means already written, not merely already picked.

## Commands

pending_creates
dependency_order
plan_references
