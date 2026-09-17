---
id: surface-pron-sexpr-move
system: pron
surface: sexpr.move
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/move.py
---

# sexpr.move

## Purpose

One move (spec 07, 11 §5): whatever a turn does, bracketed and recorded.

## How It Works

A move opens an sldb operation, reads hash_mundo (reloading the lexicon and projection if
the world changed outside pron), runs the turn, and writes the MoveDoc: who said what, the
outcome, the dialogue state before and after, hash_mundo before and after, the move it
refers to, and the full record — queries, reads, writes, edges and the trace. A StoreError
anywhere in the turn is an answer, not a crash, and it is recorded like any other outcome.

## Commands

Move
