---
id: atom-001
title: Self-described store layout
five_wh_one_plus: what
tags:
- system:sldb
- topic:store
- layer:runtime
---

# Self-described store layout

## Answer

The `.sldb/` workspace separates durable shared state under `core/`, rebuildable execution-time state under `runtime/`, and machine-local overrides under `.config/` so contributors can tell what belongs in git, what can be regenerated, and what should remain local.
