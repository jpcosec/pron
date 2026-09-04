---
id: atom-anchor-references-follow-a-three-tier-scheme
title: Anchor references follow a three-tier scheme
five_wh_one_plus: how
tags:
- system:marcado
- topic:anchoring
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# Anchor references follow a three-tier scheme

## Answer

Three tiers: (1) local #namespace:classification resolves within the same document; (2) qualified ASG asg://docs/<doc-id>#namespace:classification for cross-document references; (3) shorthand <doc-id>#namespace:classification for compact remote references. The parse_anchor_reference function in anchors.py parses each form by detecting the leading '#' or 'asg://docs/' prefix or plain doc-id with '#' separator.
