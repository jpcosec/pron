---
id: atom-self-generating-spec-derived-cli
title: Self-generating spec-derived CLI
five_wh_one_plus: how
tags:
- system:deskops
- layer:cli
- topic:specs
---

# Self-generating spec-derived CLI

## Answer

The deskops CLI derives artifact add/list/show surfaces from artifact specs and field specs, so intentionally exposed workflow artifacts can share parser and dispatch behavior instead of duplicating argparse code for every model.
