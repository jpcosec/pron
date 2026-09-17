---
id: surface-pron-sexpr-turn-evaluator
system: pron
surface: sexpr.turn.evaluator
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/turn/evaluator.py
---

# sexpr.turn.evaluator

## Purpose

Evaluating the forms of one move (spec 11, 13): compile, plan, check, run.

## How It Works

The forms are compiled to parts; every noun of every part is resolved before anything is
executed; the whole move is pre-validated over an overlay (spec 11 §7); hash_mundo is read
once more just before executing (spec 11 §5), and if the world moved while we were
understanding it, the move is understood again over the world as it is now — once, and
then it gives up rather than race forever. Only then do the parts run, in dependency order,
with a single graph refresh at the end if any of them wrote.

## Commands

Evaluator
