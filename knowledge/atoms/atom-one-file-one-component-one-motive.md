---
id: atom-one-file-one-component-one-motive
title: "One file, one component, one motive"
five_wh_one_plus: how
tags:
- system:knowledge
- domain:code_craft
- kind:concept
- impl:here
- practice:patterns
- lang:python
- topic:semantic_anchoring
provenance: Derived from `source/spec/KNOWLEDGE_CODE_STANDARD.md`.
---

# One file, one component, one motive

## Answer

The source layout maps one file to one component from the components spec (sexpr, anchors, resolution, session, evaluator, ops, bridges, projector, surface, render), and each public function carries a one-line docstring stating its motive. The s-expression kernel depends on nothing in the project.
