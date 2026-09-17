---
id: surface-pron-sexpr-execution-executor
system: pron
surface: sexpr.execution.executor
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/execution/executor.py
---

# sexpr.execution.executor

## Purpose

part.kind → what does it (spec 06, 11 §7), and whether it wrote.

## How It Works

One dispatcher over the eight kinds of part a move can have. Everything a kind needs to
know about itself lives in its own executor, so a new kind is a new class and a new line
here, not a longer ladder. What comes back is what to say and whether the world changed —
the move refreshes the graph once, at the end, if anything did.

## Commands

Executor
