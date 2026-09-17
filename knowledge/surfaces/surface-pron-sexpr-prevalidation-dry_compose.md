---
id: surface-pron-sexpr-prevalidation-dry_compose
system: pron
surface: sexpr.prevalidation.dry_compose
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/prevalidation/dry_compose.py
---

# sexpr.prevalidation.dry_compose

## Purpose

Simulating a composition (spec 11 §7, spec 05): every step, in order, over the overlay.

## How It Works

The steps of a composition run one after another and the later ones may name what the
earlier ones made, as `$created`. That is what makes the simulation worth doing here: a
step that names `$created` before any step created anything is a malformed declaration,
and it is caught before the first real write — and before anything is even asked of the
store. A `change` against `$created` is skipped: the document does not exist yet, so there
is no payload to check the transition against.

## Commands

DryCompose
