---
id: surface-pron-surface-interpret
system: pron
surface: surface.interpret
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/surface/interpret.py
---

# surface.interpret

## Purpose

The constructions a sentence can match, and the small operations every one of them needs
(spec 06, 11 §1).

## How It Works

The constructions are fixed and listed in patterns.yaml; a world never adds one, it
adds words. A sentence coordinated with "and" is one move with several parts, and that
split, the search for a verb word among the items, and what is left unattached to any
noun phrase are all here — the constructions themselves are Interpreter's methods.

## Commands

construction_names
