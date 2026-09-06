---
id: atom-knowledge-decomposes-into-ten-single-motive-components
title: "Knowledge decomposes into ten single-motive components"
five_wh_one_plus: what
tags:
- system:knowledge
- kind:concept
- impl:pending
- topic:semantic_anchoring
- domain:system_architecture
provenance: Derived from `source/spec/KNOWLEDGE_COMPONENTS.md`.
---

# Knowledge decomposes into ten single-motive components

## Answer

The system decomposes into: surface_parser, desugarer, anchor_registry, noun_resolver, session, op_dispatcher, sldb bridge, kgdb bridge, projector, and renderer. Each has one motive, a fixed in/out contract, and declared dependencies; the evaluator does not know storage and the bridges do not know grammar.
