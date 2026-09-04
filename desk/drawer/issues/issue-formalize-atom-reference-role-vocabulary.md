# Formalize atom reference role vocabulary

## Kind

feature

## Status

open

## Problem

`docs/diagrams/codebase/codebase-knowledge-surfaces.md` sketches atom reference metadata with `target_kind` and `role`, and `docs/diagrams/codebase/codebase-document-relation-map.md` uses relation roles on edges, but no validated vocabulary exists yet.

## Desired Outcome

Promote the draft role and target-kind vocabulary into a small spec or model field definition that can be reused by materialization contracts, document atom references, and trace indexes.

## Questions

- Which initial roles are canonical: `documents`, `specifies`, `constrains`, `supports`, `validates`, `implements`, `uses`, `composes`, `transcludes`, `renders`, `violates`, or a smaller set?
- Should code relations use different roles from doc/spec/diagram relations?
- Should `target_kind` describe the referencing artifact, the referenced surface, or the intended output of the relation?

## Related Atoms

- atom-atom-references-carry-roles
- atom-documents-point-to-atoms
- atom-reverse-traceability-is-derived
