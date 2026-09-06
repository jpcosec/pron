---
id: atom-the-anchor-table-is-declared-as-sldb-documents-not-code
title: The anchor table is declared as SLDB documents, not code
five_wh_one_plus: why
tags:
- system:knowledge
- domain:knowledge_representation
- kind:concept
- impl:pending
- topic:semantic_anchoring
- entity:anchor
- cross:knowledge_sldb
provenance: Derived from `source/spec/KNOWLEDGE_CORE_SEMANTIC_ANCHORING.md` (knowledge core spec), inspired by SHRDLU-style world-grounded resolution and the existing SMG / s-expression runtime atoms.
---

# The anchor table is declared as SLDB documents, not code

## Answer

Anchors live as tracked SLDB documents (AnchorDoc), not as code, so each app declares its own grammar by registering anchors. knowledge adapts to each use case without code changes, the grammar is queryable and versioned with provenance, and the app becomes self-aware of its own command language: --help and the living grammar derive from the same documents.
