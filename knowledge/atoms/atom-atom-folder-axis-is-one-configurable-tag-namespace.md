---
id: atom-atom-folder-axis-is-one-configurable-tag-namespace
title: Atom folder axis is one configurable tag namespace
five_wh_one_plus: how
tags:
- system:deskops
- topic:atoms
- layer:cli
provenance: null
---

# Atom folder axis is one configurable tag namespace

## Answer

Desks can declare one tag namespace as the physical folder axis for atoms by setting `atom_folder_axis` in `desk/config.json` (for example `"atom_folder_axis": "object"`). The default is `null`, which keeps the existing flat layout unchanged.

Rules:

- Only the axis namespace decides folder placement; all other tags are preserved and never affect paths.
- An atom with exactly one `axis:<value>` tag is created under `desk/atoms/<value-as-folders>/`.
- Dot-notation values create nested folders: `object:mepu.licitaciones` materializes under `desk/atoms/mepu/licitaciones/`. Nesting is chosen because dot-notation already expresses hierarchy in the tag typing, and folder nesting keeps navigation aligned with that hierarchy.
- An atom carrying multiple values of the axis namespace is rejected with an explicit error. A deterministic fail-fast rule is chosen over picking a first value, because silent placement would depend on tag order and hide modeling problems; the fix is to remove extra axis tags or split the atom.
- Atoms without an axis tag stay flat, so desks without the config and atoms outside the axis are fully backwards compatible.
- `deskops atoms reorganize` moves existing atoms into their axis folders idempotently and retargets tracked document paths in the `.sldb` store, keeping store integrity checks green.
