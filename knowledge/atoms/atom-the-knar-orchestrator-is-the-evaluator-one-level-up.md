---
id: atom-the-knar-orchestrator-is-the-evaluator-one-level-up
title: "The KNAR orchestrator is the evaluator one level up"
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

# The KNAR orchestrator is the evaluator one level up

## Answer

KNAR's orchestrator pseudocode (satisfy goal context) maps step by step onto the knowledge evaluator: resolve-capability is anchor lookup, find-node is noun resolution, assert-compatible is dispatch-time kind checking, and run-completion-tests is a check operation. (satisfy ...) is itself an s-expression, so orchestration is evaluation over node-kind anchors rather than a separate machine.
