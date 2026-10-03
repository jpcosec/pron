# Document AtomDoc and namespace workflow

## Issue

`AtomDoc` and atom tag namespaces now have a real implementation, but onboarding/docs do not yet explain how to use them.

## Core Need

Document how to create atoms with `deskops add atom`, how `five_wh_one_plus` works, how tag namespaces are selected, and how to add a namespace when existing ones are insufficient.

## Constraints

- Explain that namespaces are controlled but extensible.
- Explain preference for existing namespaces before adding new ones.
- Explain that `.sldb/core` is versioned and `.sldb/runtime` is ignored.
- Keep docs aligned with actual CLI behavior, not the old noun-verb proposal.

## Follow-Up Shape

- Update README or add a focused atom workflow doc.
- Include examples for `deskops add atom` and `deskops atoms add-namespace`.
- Link to the `sldb` core/runtime follow-up issue.

## Tags

- system:deskops
- topic:atoms
- topic:docs
- topic:namespaces
