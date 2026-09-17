---
id: surface-pron-sexpr-execution-compose_executor
system: pron
surface: sexpr.execution.compose_executor
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/execution/compose_executor.py
---

# sexpr.execution.compose_executor

## Purpose

Doing a composition (spec 05, 11 §7): several writes said as one word.

## How It Works

The steps run in the order the alias declares them and each may name what an earlier one
made, as `$created`; naming it before anything created it is a malformed declaration and
stops the composition before it asks the store for anything. The create runs first in
practice, and it is told what it is about to be related to, because the naming template of
the new document may name it (spec 04). The answer is composed at the end, once every
relation exists: "Created reservation for Ana, on the terrace, for Friday."

## Commands

ComposeExecutor
