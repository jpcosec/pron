---
id: atom-unanchored-symbols-fail-with-an-explicit-semantic-error
title: Unanchored symbols fail with an explicit semantic error
five_wh_one_plus: how_not
tags:
- system:knowledge
- domain:knowledge_representation
- kind:concept
- impl:here
- topic:semantic_anchoring
- topic:validation
provenance: Derived from `source/spec/KNOWLEDGE_CORE_SEMANTIC_ANCHORING.md` (knowledge core spec), inspired by SHRDLU-style world-grounded resolution and the existing SMG / s-expression runtime atoms.
---

# Unanchored symbols fail with an explicit semantic error

## Answer

A symbol without an anchor must not be guessed, fuzzy-matched into an operation, or silently ignored. The evaluator fails with an explicit semantic error stating that the symbol has no known motive. Growing the grammar means declaring a new anchor document, never patching the parser.
