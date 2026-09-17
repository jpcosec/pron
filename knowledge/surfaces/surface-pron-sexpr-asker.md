---
id: surface-pron-sexpr-asker
system: pron
surface: sexpr.asker
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/asker.py
---

# sexpr.asker

## Purpose

When a part cannot be planned, what the session says back (spec 06).

## How It Works

Three answers, none of which writes anything: a `choice` when a noun named more than one
document, `data` when a create still needs a required field, and `missing` when a noun
named nothing. The first two open a pending question the next turn answers; the third
closes the turn but keeps the hole it left, so a verbless fragment in the next turn can
correct it (spec 06 §Corrección).

## Commands

Asker
