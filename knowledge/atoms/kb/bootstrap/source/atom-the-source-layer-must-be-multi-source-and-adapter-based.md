---
id: atom-the-source-layer-must-be-multi-source-and-adapter-based
title: The source layer must be multi-source and adapter-based
five_wh_one_plus: what
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

# The source layer must be multi-source and adapter-based

## Answer

The source layer should be designed as a multi-source, adapter-based subsystem so the KB can integrate PDFs, webpages, markdown, code, git objects, and structured data without forcing them into one narrow source model. Each source type should expose version binding, retrievable representations, and sampleable projections appropriate to its structure.
