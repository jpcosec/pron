---
id: surface-pron-sexpr-turn-note_reads
system: pron
surface: sexpr.turn.note_reads
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/turn/note_reads.py
---

# sexpr.turn.note_reads

## Purpose

Spec 07: every document a turn resolved, with the hash_c it had when it was read.

## How It Works

A move records what it wrote; it also records what it read, so the ledger can say what the
answer was based on and whether that has moved since. Both the phrase planner (nouns) and
the relation read (edges) note their reads here, once per document.

## Commands

note_reads
