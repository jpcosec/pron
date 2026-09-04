---
id: atom-each-source-type-should-expose-its-own-retrievable-projections
title: Each source type should expose its own retrievable projections
five_wh_one_plus: how
tags:
  - system:kb
  - layer:source
  - layer:projection
  - entity:source
  - topic:multi_source
  - topic:anchoring
  - domain:knowledge_representation
provenance: Derived from `kb/spec/MULTI_SOURCE_ANCHORING.md` and `kb/spec/source_apps/SYNTHESIZED_ARCHITECTURE.md`.

---

# Each source type should expose its own retrievable projections

## Answer

Each source type should expose retrievable projections suited to its structure, such as text, AST, section trees, DOM, layout regions, or object paths, so anchoring and sample validation can use the strongest available representation instead of forcing every source into the same retrieval model.
