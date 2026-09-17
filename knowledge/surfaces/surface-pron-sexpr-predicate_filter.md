---
id: surface-pron-sexpr-predicate_filter
system: pron
surface: sexpr.predicate_filter
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/predicate_filter.py
---

# sexpr.predicate_filter

## Purpose

Narrowing what a read found by the predicates its extra modifiers left (spec 02, 07).

## How It Works

Each predicate is one `find` per store of the projection; the hits of a predicate are the
union over the stores, and the hits of several predicates are their intersection. Every
call is put in the trace exactly as it was made, so the answer can be checked by hand.

## Commands

PredicateFilter
