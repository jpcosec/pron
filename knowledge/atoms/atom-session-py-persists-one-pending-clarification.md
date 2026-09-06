---
id: atom-session-py-persists-one-pending-clarification
title: "session.py persists one pending clarification"
five_wh_one_plus: where
tags:
- system:knowledge
- kind:software
- impl:here
- topic:semantic_anchoring
- domain:retrieval
provenance: src/knowledge/core/session.py
---

# session.py persists one pending clarification

## Answer

src/knowledge/core/session.py stores {pending_sexpr, candidates, created_at, store_hash} in .knowledge/session.json under the cwd. load() returns None and clears when 15 minutes elapse or when the live store hash_a differs from the recorded one.
