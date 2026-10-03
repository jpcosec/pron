# Compose large documents from atoms through sldb

## Issue

Large documents should be materializations/compositions of atoms through `sldb`, but the concrete composition contract is not defined yet.

## Core Need

Define how a larger document declares and renders the atoms it composes without pushing outgoing references into the atom itself.

## Constraints

- Atoms do not point outward.
- Large documents declare their own composition.
- Composition should use `sldb` mechanisms such as model fields, `__compositions__`, links, or a sidecar composition document.
- The result must be roundtrippable and testable.

## Follow-Up Shape

- Create or identify a document model for composed atom documents.
- Add a composition test that renders a document from multiple `AtomDoc` files.
- Decide whether atom references live in frontmatter fields, body links, or a dedicated composition spec.

## Tags

- system:deskops
- system:sldb
- topic:atoms
- topic:composition
