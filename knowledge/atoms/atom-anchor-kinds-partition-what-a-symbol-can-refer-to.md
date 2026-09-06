---
id: atom-anchor-kinds-partition-what-a-symbol-can-refer-to
title: Anchor kinds partition what a symbol can refer to
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

# Anchor kinds partition what a symbol can refer to

## Answer

Anchor kinds are: model (a registered StructuredNLDoc such as UserDoc or TaskDoc), doc (a concrete tracked document), relation (a kgdb edge type such as declares_preference), operation (a runtime verb such as check, next, assert, ingest, create, return), and projection (a payload view such as summary). The evaluator dispatches on kind, so the set of kinds is the closed contract of the core.
