# Build derived atom trace index

## Kind

feature

## Status

open

## Problem

Atoms should not contain outgoing use-site lists, but users and agents still need to answer which docs, specs, diagrams, tests, tasks, or code surfaces reference each atom.

## Desired Outcome

Build a derived read-side index or command that scans materializing artifacts and reports reverse traceability without mutating atom documents.

## Questions

- Should the index live in `.sldb/runtime`, `.sldb/core`, `docs/`, or be generated on demand?
- Should unresolved atom references fail validation?
- Should atom references in prose count, or only structured metadata?

## Related Atoms

- atom-reverse-traceability-is-derived
- atom-materialization-metadata-is-not-atom-content
- atom-materializations-declare-source-atoms
