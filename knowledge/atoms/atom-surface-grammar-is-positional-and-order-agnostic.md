---
id: atom-surface-grammar-is-positional-and-order-agnostic
title: "Surface grammar is positional and order-agnostic"
five_wh_one_plus: how
tags:
- system:knowledge
- kind:concept
- impl:pending
- topic:semantic_anchoring
- domain:retrieval
- topic:authoring_workflow
provenance: Derived from `source/spec/KNOWLEDGE_USABILITY.md`.
---

# Surface grammar is positional and order-agnostic

## Answer

The surface grammar accepts noun-first ('user juanito check preferences') and verb-first ('next task --summary') orders, and both desugar deterministically to the same s-expression. There is no free NLP: every token must resolve against the anchor table, and the first unanchored token determines the error message.
