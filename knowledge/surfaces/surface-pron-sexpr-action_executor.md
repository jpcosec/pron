---
id: surface-pron-sexpr-action_executor
system: pron
surface: sexpr.action_executor
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/action_executor.py
---

# sexpr.action_executor

## Purpose

Doing an action part (spec 11 §7): a create, or the same verb over every target.

## How It Works

A create makes one document and answers with its natural name. Every other verb runs over
each document the subject resolved to: the whole batch is guarded and coerced before the
first of them is written, then each write is the verb's own `Verb.execute`
(kernel/verb_registry.py) — the one place that verb's semantics live — traced with what it
changed, and recorded for undo. A write that had nothing to do is not a failure: the answer
says how many were already like that.

## Commands

ActionExecutor
