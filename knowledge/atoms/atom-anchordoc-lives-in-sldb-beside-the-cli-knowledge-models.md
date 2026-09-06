---
id: atom-anchordoc-lives-in-sldb-beside-the-cli-knowledge-models
title: "AnchorDoc lives in sldb beside the CLI knowledge models"
five_wh_one_plus: where
tags:
- system:knowledge
- system:sldb
- kind:concept
- impl:pending
- topic:semantic_anchoring
- domain:system_architecture
- entity:anchor
- cross:knowledge_sldb
provenance: Derived from `source/spec/KNOWLEDGE_COMPONENTS.md`.
---

# AnchorDoc lives in sldb beside the CLI knowledge models

## Answer

AnchorDoc is a StructuredNLDoc defined in the sldb repo next to CliCommandDoc and SurfaceDoc, with fields symbol, kind, ref, motive, tags, and provenance. It lives in sldb because it is document infrastructure reused by every app; each app registers and tracks its own AnchorDoc instances in its own store.
