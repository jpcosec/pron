---
id: atom-semantic-milestone-markers-define-addressable-ranges-over-prose
title: Semantic milestone markers define addressable ranges over prose
five_wh_one_plus: how
tags:
- system:marcado
- topic:anchoring
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# Semantic milestone markers define addressable ranges over prose

## Answer

Markers use HTML-comment syntax <!-- namespace:classification -->...<!-- /namespace:classification --> where classification uses '.' for hierarchical refinement and '|' for parallel facets within the same namespace. Markers cannot mix namespaces in one expression. The body is parsed with a milestone/range parser, not an XML-tree parser, because markers can cross and overlap.
