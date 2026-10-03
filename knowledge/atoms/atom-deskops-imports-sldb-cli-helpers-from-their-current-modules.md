---
id: atom-deskops-imports-sldb-cli-helpers-from-their-current-modules
title: Deskops imports sldb CLI helpers from their current modules
five_wh_one_plus: what
tags: []
provenance: null
---

# Deskops imports sldb CLI helpers from their current modules

## Answer

Deskops depends on sldb's CLI helper API (get_store_context in sldb.cli.store_context; registered_model/resolve_model_ref in sldb.cli.model_utils); when sldb relocates helpers, deskops must repoint imports rather than pin stale paths, and TaskDoc frontmatter must render via render_payload (not model_dump) to keep extraction clean.
