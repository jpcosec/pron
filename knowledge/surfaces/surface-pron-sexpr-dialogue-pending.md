---
id: surface-pron-sexpr-dialogue-pending
system: pron
surface: sexpr.dialogue.pending
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/dialogue/pending.py
---

# sexpr.dialogue.pending

## Purpose

A pending question of the dialogue (spec 06), of one of two kinds: a `choice` between
candidates the session already resolved, or the `data` a write still needs. It carries the
move that opened it, the sentence that did, and whatever state the session needs to resume.

## How It Works

A pending question of the dialogue (spec 06), of one of two kinds: a `choice` between
candidates the session already resolved, or the `data` a write still needs. It carries the
move that opened it, the sentence that did, and whatever state the session needs to resume.

## Commands

Pending
