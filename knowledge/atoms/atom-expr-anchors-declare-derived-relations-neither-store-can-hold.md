---
id: atom-expr-anchors-declare-derived-relations-neither-store-can-hold
title: "Expr anchors declare derived relations neither store can hold"
five_wh_one_plus: what
tags:
- system:knowledge
- kind:concept
- impl:here
- topic:semantic_anchoring
- domain:knowledge_representation
- entity:anchor
provenance: Derived from the implemented evaluator (src/knowledge/core/evaluator.py) and verified by tests/test_acceptance.py.
---

# Expr anchors declare derived relations neither store can hold

## Answer

A kind=expr anchor binds a symbol to an s-expression template with _ holes (e.g. overlap -> (common (doc atom _) (doc atom _))). When evaluated, holes are filled with the arguments and the expansion is grounded recursively. This is the layer where knowledge exceeds sldb+kgdb: the relation is computed by composing both stores at evaluation time, exists in neither, and is declared as a tracked document rather than code.
