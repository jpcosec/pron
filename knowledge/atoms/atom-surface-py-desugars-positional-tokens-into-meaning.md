---
id: atom-surface-py-desugars-positional-tokens-into-meaning
title: "surface.py desugars positional tokens into Meaning"
five_wh_one_plus: where
tags:
- system:knowledge
- kind:software
- impl:here
- topic:semantic_anchoring
- domain:retrieval
provenance: src/knowledge/cli/surface.py
---

# surface.py desugars positional tokens into Meaning

## Answer

src/knowledge/cli/surface.py classifies each token by its anchor kind (operation, model, relation, expr, or selector), then builds the s-expression: selectors become (doc m sel), bare models (docs m), expr anchors wrap their selector, relations wrap the ref, and --flags become :project / :where options. The first unanchored token that should be a verb yields the semantic error.
