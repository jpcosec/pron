---
id: atom-the-projector-gives-the-evaluator-a-world
title: "The projector gives the evaluator a world"
five_wh_one_plus: why
tags:
- system:knowledge
- kind:concept
- impl:pending
- topic:semantic_anchoring
- domain:system_architecture
- cross:knowledge_kgdb
provenance: Derived from `source/spec/KNOWLEDGE_COMPONENTS.md`.
---

# The projector gives the evaluator a world

## Answer

The infra layer ('knowledge model add' to register models, 'knowledge project' to materialize the kgdb snapshot) exists so the evaluator has referents to resolve against. It is component number nine, subordinate to the core: projection freshness is a usability concern (warn and instruct), never a hidden failure.
