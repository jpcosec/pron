---
id: surface-pron-sexpr-collaborator
system: pron
surface: sexpr.collaborator
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/collaborator.py
---

# sexpr.collaborator

## Purpose

What every phase of a move shares (spec 06, 11): the session it works over.

## How It Works

Planning, pre-validating and executing a move are one class each, and each of them needs
the same handful of things — the world, the lexicon, the projection's kernel, the dialogue.
A collaborator keeps none of that: it holds the session and reads through it, so whatever
`Session._load` last left after a reload is what the phase sees, without a second copy to
keep current. Collaborators are built at the point of use and thrown away with the turn.

## Commands

Collaborator
