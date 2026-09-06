---
id: atom-symbol-resolution-is-stateful-and-treats-ambiguity-as-dialogue
title: Symbol resolution is stateful and treats ambiguity as dialogue
five_wh_one_plus: how
tags:
- system:knowledge
- domain:knowledge_representation
- kind:concept
- impl:here
- topic:semantic_anchoring
- topic:query
provenance: Derived from `source/spec/KNOWLEDGE_CORE_SEMANTIC_ANCHORING.md` (knowledge core spec), inspired by SHRDLU-style world-grounded resolution and the existing SMG / s-expression runtime atoms.
---

# Symbol resolution is stateful and treats ambiguity as dialogue

## Answer

Noun resolution against the store has three outcomes, SHRDLU-style: a unique referent proceeds; an ambiguous one returns a question plus candidates and leaves the evaluator awaiting clarification, so the next input resolves the pending expression; a missing one fails with the symbol's motive so the error explains what was being looked for. Ambiguity produces dialogue, never a silent failure or a bare exception.
