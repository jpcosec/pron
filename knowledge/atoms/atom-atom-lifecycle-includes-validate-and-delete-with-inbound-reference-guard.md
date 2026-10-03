---
id: atom-atom-lifecycle-includes-validate-and-delete-with-inbound-reference-guard
title: Atom lifecycle includes validate and delete with inbound-reference guard
five_wh_one_plus: what
tags: []
provenance: null
---

# Atom lifecycle includes validate and delete with inbound-reference guard

## Answer

'deskops atoms validate' checks atom integrity and 'deskops atoms delete' removes an atom only when no inbound references exist, untracking it from the store; split/merge/create-from-source remain deferred drawer work.
