---
id: surface-pron-sexpr-planner
system: pron
surface: sexpr.planner
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/planner.py
---

# sexpr.planner

## Purpose

Planning one part of a move (spec 06, 13): every noun resolved before anything runs.

## How It Works

Nothing is written until every part of the move has been planned, so a move that cannot
be carried out whole is never carried out half. A part with no nouns — `(undo)`,
`(refresh)`, `(why)` — plans to nothing; a composition plans its steps; anything else
resolves the phrase in each role it has, against the class that role needs. A create's
subject is the exception: it does not exist yet, so there is nothing to resolve, only its
required fields to check.

## Commands

Planner
