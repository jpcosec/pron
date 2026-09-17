---
id: surface-pron-sexpr-planning-phrase_planner
system: pron
surface: sexpr.planning.phrase_planner
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/planning/phrase_planner.py
---

# sexpr.planning.phrase_planner

## Purpose

Resolving one noun phrase of a part against the world (spec 02, 06, 13).

## How It Works

Three ways a phrase can name documents, tried in this order: it was said by address —
`(doc "Model:name")` — and then every id must exist, unless it is a create of this same
move the store has not written yet; it is a referent of the dialogue ("it", "them", "me")
and the antecedent is whatever a recent turn left, of the class this part needs; or it
describes a query, and sldb answers it. Whatever a phrase read on the way is noted on the
move (spec 07).

## Commands

PhrasePlanner
