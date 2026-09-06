---
id: atom-knowledge-implements-the-knar-knowledge-and-projection-concepts
title: "knowledge implements the KNAR knowledge and projection concepts"
five_wh_one_plus: what
tags:
- system:knowledge
- system:knar
- kind:concept
- impl:pending
- cross:knar_knowledge
- topic:semantic_anchoring
- domain:system_architecture
provenance: Bridge between `source/knar/spec.md` (KNAR runtime spec) and `source/spec/KNOWLEDGE_CORE_SEMANTIC_ANCHORING.md` (knowledge core spec).
---

# knowledge implements the KNAR knowledge and projection concepts

## Answer

Of KNAR's five fundamental concepts (KNOWLEDGE, NODE, PORT, RUNTIME, PROJECTION), the knowledge system implements KNOWLEDGE and PROJECTION: it is the stable semantic layer (KNAR spec section 6: query/resolve/project/write/validate) that KNAR nodes consume. NODE, PORT, and RUNTIME are the runtime half that consumes this layer through the anchored command surface; neither half replaces the other.
