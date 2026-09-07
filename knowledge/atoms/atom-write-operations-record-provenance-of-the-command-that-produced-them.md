---
id: atom-write-operations-record-provenance-of-the-command-that-produced-them
title: Write operations record provenance of the command that produced them
five_wh_one_plus: how
tags:
- system:knowledge
- domain:provenance
- kind:concept
- impl:here
- topic:semantic_anchoring
- graph:lineage
provenance: Derived from `source/spec/KNOWLEDGE_CORE_SEMANTIC_ANCHORING.md` (knowledge core spec), inspired by SHRDLU-style world-grounded resolution and the existing SMG / s-expression runtime atoms.
---

# Write operations record provenance of the command that produced them

## Answer

Every write operation (assert, create, ingest) goes through sldb document and field operations and records the evaluated command as provenance. This is SHRDLU's action memory made auditable: any stored fact can be traced back to the exact expression, anchors, and referents that produced it.
