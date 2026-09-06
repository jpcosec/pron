---
id: atom-code-materializes-specs-and-never-decides-design
title: "Code materializes specs and never decides design"
five_wh_one_plus: how_not
tags:
- system:knowledge
- domain:code_craft
- kind:concept
- impl:pending
- practice:clean_code
- lang:generic
- topic:semantic_anchoring
provenance: Derived from `source/spec/KNOWLEDGE_CODE_STANDARD.md`.
---

# Code materializes specs and never decides design

## Answer

Implementation code materializes the documented specs; it does not make design decisions. If an undocumented decision appears while coding, coding stops and the decision is resolved first as an atom or spec change. An if-branch the spec cannot explain means the spec was ambiguous.
