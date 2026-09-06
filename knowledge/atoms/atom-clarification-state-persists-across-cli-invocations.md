---
id: atom-clarification-state-persists-across-cli-invocations
title: "Clarification state persists across CLI invocations"
five_wh_one_plus: how
tags:
- system:knowledge
- kind:concept
- impl:here
- topic:semantic_anchoring
- domain:retrieval
- topic:query
provenance: Derived from `source/spec/KNOWLEDGE_USABILITY.md`.
---

# Clarification state persists across CLI invocations

## Answer

Ambiguity leaves a pending expression plus candidates persisted in a local session file, so the dialogue works across separate CLI invocations in a terminal. The next input is first matched against pending candidates; if it matches none, it is treated as a new command and the pending expression is discarded.
