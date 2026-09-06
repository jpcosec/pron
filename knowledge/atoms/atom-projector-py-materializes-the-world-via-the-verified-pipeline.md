---
id: atom-projector-py-materializes-the-world-via-the-verified-pipeline
title: "projector.py materializes the world via the verified pipeline"
five_wh_one_plus: where
tags:
- system:knowledge
- kind:software
- impl:here
- topic:semantic_anchoring
- domain:system_architecture
provenance: src/knowledge/infra/projector.py
---

# projector.py materializes the world via the verified pipeline

## Answer

src/knowledge/infra/projector.py implements model_add (sldb models add) and project (sldb stores semantic-export piped into kgdb ingest-sldb, writing .sldb/runtime/knowledge.nx.json). It is the only component that shells out, because both steps are owned by external CLIs.
