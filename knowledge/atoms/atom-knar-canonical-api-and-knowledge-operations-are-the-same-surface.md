---
id: atom-knar-canonical-api-and-knowledge-operations-are-the-same-surface
title: "The KNAR canonical API and the knowledge operations are the same surface"
five_wh_one_plus: what
tags:
- system:knowledge
- system:knar
- kind:concept
- impl:pending
- cross:knar_knowledge
- topic:semantic_anchoring
- domain:retrieval
provenance: Bridge between `source/knar/spec.md` (KNAR runtime spec) and `source/spec/KNOWLEDGE_CORE_SEMANTIC_ANCHORING.md` (knowledge core spec).
---

# The KNAR canonical API and the knowledge operations are the same surface

## Answer

KNAR section 6 demands a stable API (knowledge.query, resolve, project, write, validate) so agents never parse Markdown arbitrarily. The knowledge core operations are that API: check/next/return cover query and resolve, the projector covers project, assert/create/ingest cover write with provenance, and validation is the authoring gate. KNAR names the consumer contract; knowledge names the evaluator that fulfills it.
