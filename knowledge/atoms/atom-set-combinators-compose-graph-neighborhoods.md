---
id: atom-set-combinators-compose-graph-neighborhoods
title: "Set combinators compose graph neighborhoods"
five_wh_one_plus: how
tags:
- system:knowledge
- kind:concept
- impl:here
- topic:semantic_anchoring
- domain:knowledge_representation
- entity:anchor
- graph:retrieval
provenance: Derived from the implemented evaluator (src/knowledge/core/evaluator.py) and verified by tests/test_acceptance.py.
---

# Set combinators compose graph neighborhoods

## Answer

Three combinators operate over grounded documents via their graph neighborhoods (outgoing plus incoming edges, any relation): (related X) yields everything one hop from X, (common X Y) intersects neighborhoods, and (also X Y) unions them. Combined with expr anchors they express queries like 'what do these two atoms share' that no single store query can answer.
