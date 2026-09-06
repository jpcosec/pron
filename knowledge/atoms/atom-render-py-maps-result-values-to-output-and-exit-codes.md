---
id: atom-render-py-maps-result-values-to-output-and-exit-codes
title: "render.py maps result values to output and exit codes"
five_wh_one_plus: where
tags:
- system:knowledge
- kind:software
- impl:here
- topic:semantic_anchoring
- domain:retrieval
provenance: src/knowledge/cli/render.py
---

# render.py maps result values to output and exit codes

## Answer

src/knowledge/cli/render.py renders OperationResult (exit 0/1), Ambiguous (exit 2, question plus candidates), Missing (exit 1, motive plus nearest), and SemanticError (exit 1, symbol/message/hint) as JSON by default or text. refs are always included in read outputs.
