---
id: atom-component-done-means-spec-tests-atoms-docs-and-store-pass
title: "Component done means spec, tests, atoms, docs, and store pass"
five_wh_one_plus: when
tags:
- system:knowledge
- domain:code_craft
- kind:concept
- impl:pending
- practice:traceability
- lang:generic
- topic:semantic_anchoring
provenance: Derived from `source/spec/KNOWLEDGE_CODE_STANDARD.md`.
---

# Component done means spec, tests, atoms, docs, and store pass

## Answer

A component is done when: its spec contract is implemented without undocumented extensions, contract tests pass, its atoms flip impl:pending to impl:here, CliCommandDoc/SurfaceDoc are regenerated from the real argparse tree, and 'sldb stores check' passes after tracking the new docs. Code and docs always land in the same commit.
