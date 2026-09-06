---
id: atom-session-expires-by-ttl-and-store-hash
title: "Session expires by TTL and store hash"
five_wh_one_plus: when
tags:
- system:knowledge
- kind:concept
- impl:pending
- topic:semantic_anchoring
- domain:retrieval
provenance: Derived from `source/spec/KNOWLEDGE_COMPONENTS.md`, section 'Decisiones cerradas'.
---

# Session expires by TTL and store hash

## Answer

The clarification session lives in .knowledge/session.json under the cwd, holds exactly one pending expression with candidates, and is discarded when 15 minutes pass since creation or when the store's hash_a changes, since candidates may no longer exist after a store mutation. A new command always replaces the pending one.
