---
id: surface-pron-sexpr-execution-assert_executor
system: pron
surface: sexpr.execution.assert_executor
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/execution/assert_executor.py
---

# sexpr.execution.assert_executor

## Purpose

Asserting a relation (spec 03, 11 §7): one RelationDoc per source × target pair.

## How It Works

The projection has to allow asserting this relation and not only reading it — the same
check the pre-validation already made, made again here because this is the last thing
before the write. Each edge is a document created in sldb, recorded in the move so undo
can take it back, and said out loud as the sentence it is.

## Commands

AssertExecutor
