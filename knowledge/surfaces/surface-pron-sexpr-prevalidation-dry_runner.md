---
id: surface-pron-sexpr-prevalidation-dry_runner
system: pron
surface: sexpr.prevalidation.dry_runner
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/prevalidation/dry_runner.py
---

# sexpr.prevalidation.dry_runner

## Purpose

Spec 11 §7: the parts of a move dispatched to their simulation, one kind each.

## How It Works

Only the parts that would write are simulated — an action, an assert, a composition, and
`undo`, which needs its permission checked like any other write. A read or a nominal
answer writes nothing, so there is nothing to check before it. The overlay is threaded
through every part in order, so each one is simulated over what the earlier ones would
have left.

## Commands

DryRunner
