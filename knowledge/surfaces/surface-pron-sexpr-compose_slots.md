---
id: surface-pron-sexpr-compose_slots
system: pron
surface: sexpr.compose_slots
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/compose_slots.py
---

# sexpr.compose_slots

## Purpose

The phrase of the sentence each slot of a compose alias takes (spec 05, 13).

## How It Works

`$referent:M` takes the referent of the sentence — the pronoun it said, or an implicit one
built from the words that were there; `$object:M` takes a phrase whose class is in M's
family. A composition compiled from forms already carries its slots filled, and then
nothing is guessed: the form said which phrase goes where.

## Commands

ComposeSlots
