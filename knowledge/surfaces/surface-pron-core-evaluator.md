---
id: surface-pron-core-evaluator
system: pron
surface: pron.core.evaluator
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
provenance: src/pron/core/evaluator.py
---

# pron.core.evaluator

## Purpose

Evaluator: resolves each symbol through its anchor and dispatches by kind

## How It Works

atom-knowledge-core-is-a-semantically-anchored-s-expression-evaluator: The core of knowledge is an evaluator of s-expressions in which every symbol is anchored to a semantic motive resolvable against the infrastructure (sldb + kgdb + runtime state). A command is not a string parsed into flags: it is an expression whose meaning is resolved against the world before it executes. Everything else in the knowledge system is ordered after this core.

## Commands

Evaluator
Evaluator.eval(self, expr: SExpr) | Evaluate a full expression: (op arg* [:project sym]).
project_payload(payload: dict, projection: Anchor | None) -> dict | Apply a fields:/view: projection to a payload.
