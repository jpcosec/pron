---
id: atom-the-infra-layer-serves-the-anchoring-core-not-the-reverse
title: The infra layer serves the anchoring core, not the reverse
five_wh_one_plus: why
tags:
- system:knowledge
- domain:system_architecture
- kind:concept
- impl:here
- topic:semantic_anchoring
- cross:knowledge_sldb
provenance: Derived from `source/spec/KNOWLEDGE_CORE_SEMANTIC_ANCHORING.md` (knowledge core spec), inspired by SHRDLU-style world-grounded resolution and the existing SMG / s-expression runtime atoms.
---

# The infra layer serves the anchoring core, not the reverse

## Answer

Declaring sldb models and projecting them to the infrastructure (store registration plus kgdb materialization) exists so the evaluator has a world to resolve against. Dependency order: first the anchoring core, then the infra layer, then documentary surfaces (CliCommandDoc, SurfaceDoc) derived from anchors, and finally the atom corpus the core makes queryable. Everything else in knowledge comes after the core.
