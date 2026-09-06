---
id: atom-resolution-py-implements-the-selector-cascade
title: "resolution.py implements the selector cascade"
five_wh_one_plus: where
tags:
- system:knowledge
- kind:software
- impl:here
- topic:semantic_anchoring
- domain:retrieval
provenance: src/knowledge/core/resolution.py
---

# resolution.py implements the selector cascade

## Answer

src/knowledge/core/resolution.py resolves (model, selector) through the cascade: exact name, exact title, name prefix, semantic tag for namespaced selectors, then substring over name and title. One match resolves; several return Ambiguous with sorted candidates; none returns Missing with fuzzy nearest suggestions.
