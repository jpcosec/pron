---
id: surface-pron-sexpr-planning-compose_planner
system: pron
surface: sexpr.planning.compose_planner
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/planning/compose_planner.py
---

# sexpr.planning.compose_planner

## Purpose

Planning a composition (spec 05, 06): every slot of every step resolved, and every
step's permission checked, before the first of them writes anything.

## How It Works

A compose alias is several writes said as one word ("book her a table"). Its steps name
their sides with slots, and a slot is either `$created` — what the composition itself makes,
which cannot be resolved because it does not exist yet — or a phrase of the sentence. The
projection has to allow every verb the steps do, or the whole composition is refused.

## Commands

ComposePlanner
