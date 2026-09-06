---
id: atom-declarative-agents-and-declarative-grammar-are-the-same-bet
title: "Declarative agents and declarative grammar are the same bet"
five_wh_one_plus: why
tags:
- system:knowledge
- system:knar
- kind:concept
- impl:pending
- cross:knar_knowledge
- topic:semantic_anchoring
- domain:knowledge_representation
provenance: Bridge between `source/knar/spec.md` (KNAR runtime spec) and `source/spec/KNOWLEDGE_CORE_SEMANTIC_ANCHORING.md` (knowledge core spec).
---

# Declarative agents and declarative grammar are the same bet

## Answer

KNAR states that agents should be mostly data (section 22), with code implementing only runtimes and primitives; the knowledge core states that the grammar lives as AnchorDoc documents, with code implementing only the evaluator kernel. Both are the same architectural bet: behavior is declared as tracked knowledge, executables stay generic, and evolving the system means authoring documents, not patching code.
