---
id: atom-anchors-py-loads-the-grammar-from-tracked-anchordocs
title: "anchors.py loads the grammar from tracked AnchorDocs"
five_wh_one_plus: where
tags:
- system:knowledge
- kind:software
- impl:here
- topic:semantic_anchoring
- domain:knowledge_representation
- entity:anchor
provenance: src/knowledge/core/anchors.py
---

# anchors.py loads the grammar from tracked AnchorDocs

## Answer

src/knowledge/core/anchors.py implements AnchorRegistry: it loads every tracked AnchorDoc from the store via the sldb bridge, exposes lookup (symbol -> Anchor or SemanticError with declaration hint), all() for the living grammar, and by_kind(). It never invents anchors.
