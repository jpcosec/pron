---
id: atom-main-py-routes-surface-eval-anchors-and-infra
title: "main.py routes surface, eval, anchors, and infra"
five_wh_one_plus: where
tags:
- system:knowledge
- kind:software
- impl:here
- topic:semantic_anchoring
- domain:system_architecture
provenance: src/knowledge/cli/main.py
---

# main.py routes surface, eval, anchors, and infra

## Answer

src/knowledge/cli/main.py is the entry point: anchors (living grammar), model add, project, eval (direct Meaning), and the surface path with clarification handling: a pending session whose candidates match the sole input token resumes the saved expression; otherwise the pending state is discarded and the input runs as a new command.
