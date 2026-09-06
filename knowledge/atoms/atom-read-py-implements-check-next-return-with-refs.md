---
id: atom-read-py-implements-check-next-return-with-refs
title: "read.py implements check, next, return with refs"
five_wh_one_plus: where
tags:
- system:knowledge
- kind:software
- impl:here
- topic:semantic_anchoring
- domain:retrieval
provenance: src/knowledge/ops/read.py
---

# read.py implements check, next, return with refs

## Answer

src/knowledge/ops/read.py implements the read half of the canonical operations: check reads Resolved docs, docs sets, rel traversals, and node sets; next orders docs by status rank (active < ready < pending, done excluded) then name; return_ aliases check. Every result carries refs.
