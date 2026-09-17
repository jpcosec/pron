---
id: surface-pron-sexpr-action_verb
system: pron
surface: sexpr.action_verb
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/action_verb.py
---

# sexpr.action_verb

## Purpose

Which plain action verb an action part does (spec 11 §7, spec 13).

## How It Works

A part may say the verb itself — `(change NOUN field value)` — or say an alias that stands
for one; the pre-validation and the execution of an action both ask the same question, and
they ask it here.

## Commands

action_verb
