---
id: surface-pron-sexpr-leftover_predicates
system: pron
surface: sexpr.leftover_predicates
tags:
- system:pron
- domain:system_architecture
- kind:software
- impl:here
- entity:module
provenance: src/pron/sexpr/leftover_predicates.py
---

# sexpr.leftover_predicates

## Purpose

The extra modifiers a read left over, as predicates on the asked side (spec 02, 13).

## How It Works

"what did Ana book for Friday" reads the edges of `book` from Ana, and "for Friday" is not
about Ana: it narrows what comes back. Those leftover items become sldb predicates on the
asked phrase — a date literal against the model's `date` field, a word through the same
modifier machinery a noun phrase uses — and the read intersects its answer with them. The
phrase itself is copied first: the predicates belong to this read, not to the phrase.

## Commands

LeftoverPredicates
