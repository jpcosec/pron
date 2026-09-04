---
id: atom-task-bundles-are-tracked-in-the-store-at-creation-time
title: Task bundles are tracked in the store at creation time
five_wh_one_plus: what
tags: []
provenance: null
---

# Task bundles are tracked in the store at creation time

## Answer

deskops add task and promote track every generated bundle document (task, routine, conditions, checklists, operators, edges) into the local .sldb store via sldb.store.ops.track_document at write time; if a store exists but a bundle model is not registered, creation fails instead of silently leaving untracked docs.
