---
id: surface-pron-sexpr-execution-undo_executor
system: pron
surface: sexpr.execution.undo_executor
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/execution/undo_executor.py
---

# sexpr.execution.undo_executor

## Purpose

Undoing the last move that wrote (spec 07, 11 §7).

## How It Works

The ledger says which move it was — this speaker's, if there is one — and the kernel
inverts each of its writes, refusing any document that has changed since. Nothing is
forced: a write that cannot be taken back is reported, not retried.

## Commands

UndoExecutor
