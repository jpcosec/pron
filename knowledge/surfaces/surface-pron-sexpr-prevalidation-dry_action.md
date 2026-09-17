---
id: surface-pron-sexpr-prevalidation-dry_action
system: pron
surface: sexpr.prevalidation.dry_action
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/prevalidation/dry_action.py
---

# sexpr.prevalidation.dry_action

## Purpose

Simulating an action part (spec 11 §7): what it would write, without writing it.

## How It Works

The projection has to allow the verb. A create is simulated whole and, when the form gave
it a name, the payload it would leave goes into the overlay under that name, so a later
part of the same move that names it sees it. Every other verb is its own `Verb.dry`
(kernel/actions/verb.py): the one place that verb's semantics live.

## Commands

DryAction
