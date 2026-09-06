---
id: atom-resolution-outcomes-are-typed-values-not-exceptions
title: "Resolution outcomes are typed values, not exceptions"
five_wh_one_plus: how
tags:
- system:knowledge
- kind:concept
- impl:pending
- topic:semantic_anchoring
- domain:system_architecture
provenance: Derived from `source/spec/KNOWLEDGE_COMPONENTS.md`.
---

# Resolution outcomes are typed values, not exceptions

## Answer

noun_resolver returns exactly one of Resolved(doc), Ambiguous(candidates, question), or Missing(motive, nearest) as plain values. Cross-component errors are typed values (including SemanticError); exceptions are reserved for bugs, never for control flow.
