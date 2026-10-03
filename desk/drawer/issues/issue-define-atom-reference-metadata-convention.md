# Define atom reference metadata convention

## Kind

feature

## Status

open

## Problem

Artifacts can mention atoms today, but there is no standard machine-readable convention for declaring which atoms an artifact uses or what role each atom plays.

## Desired Outcome

Define a minimal atom reference shape usable by docs, specs, diagrams, tasks, tests, and future indexes.

Candidate shape:

```yaml
atoms:
  - id: atom-sldb-is-read-write-edit-surface
    role: constrains
    target_kind: doc
```

## Questions

- Should the shared field be called `atoms`, `related_atoms`, `source_atoms`, or `atom_refs`?
- Which roles are allowed initially?
- Should this live as a deskops convention first or become an SLDB-level reusable reference type?

## Related Atoms

- atom-materializations-declare-source-atoms
- atom-atom-references-carry-roles
- atom-materialization-metadata-is-not-atom-content
