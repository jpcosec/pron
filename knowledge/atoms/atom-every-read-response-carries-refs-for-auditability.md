---
id: atom-every-read-response-carries-refs-for-auditability
title: "Every read response carries refs for auditability"
five_wh_one_plus: how
tags:
- system:knowledge
- kind:concept
- impl:pending
- topic:semantic_anchoring
- domain:provenance
- graph:lineage
provenance: Derived from `source/spec/KNOWLEDGE_USABILITY.md`.
---

# Every read response carries refs for auditability

## Answer

Every read result includes the refs (document paths and graph node ids) that produced it, so any answer can be audited back to the exact tracked documents and edges. JSON is the default output for agents and pipes; text is a projection.
