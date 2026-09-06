---
id: atom-an-anchor-binds-a-symbol-to-a-semantic-motive-and-a-resolvable-referent
title: An anchor binds a symbol to a semantic motive and a resolvable referent
five_wh_one_plus: what
tags:
- system:knowledge
- domain:knowledge_representation
- kind:concept
- impl:here
- topic:semantic_anchoring
- entity:anchor
provenance: Derived from `source/spec/KNOWLEDGE_CORE_SEMANTIC_ANCHORING.md` (knowledge core spec), inspired by SHRDLU-style world-grounded resolution and the existing SMG / s-expression runtime atoms.
---

# An anchor binds a symbol to a semantic motive and a resolvable referent

## Answer

An anchor links a grammar symbol to three things: a kind (model, doc, relation, operation, or projection), a ref (the concrete referent in the infrastructure), and a motive (the natural-language meaning of the symbol for a human). The motive is what keeps the grammar legible and auditable; the kind and ref are what make the symbol executable.
