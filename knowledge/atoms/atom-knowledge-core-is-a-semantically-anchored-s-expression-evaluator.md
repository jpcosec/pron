---
id: atom-knowledge-core-is-a-semantically-anchored-s-expression-evaluator
title: The knowledge core is a semantically anchored s-expression evaluator
five_wh_one_plus: what
tags:
- system:knowledge
- domain:knowledge_representation
- kind:concept
- impl:pending
- topic:semantic_anchoring
- entity:anchor
provenance: Derived from `source/spec/KNOWLEDGE_CORE_SEMANTIC_ANCHORING.md` (knowledge core spec), inspired by SHRDLU-style world-grounded resolution and the existing SMG / s-expression runtime atoms.
---

# The knowledge core is a semantically anchored s-expression evaluator

## Answer

The core of knowledge is an evaluator of s-expressions in which every symbol is anchored to a semantic motive resolvable against the infrastructure (sldb + kgdb + runtime state). A command is not a string parsed into flags: it is an expression whose meaning is resolved against the world before it executes. Everything else in the knowledge system is ordered after this core.
