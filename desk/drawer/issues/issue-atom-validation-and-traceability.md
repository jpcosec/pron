# Validate atoms and trace composed usage

## Issue

Atoms now have a stricter `AtomDoc` contract, but there is no project-level command or test that validates every atom and traces where composed documents use them.

## Core Need

Provide validation and traceability for `desk/atoms/**/*.md` without reintroducing outgoing relations in atoms.

## Constraints

- Validation should prove every atom roundtrips through `AtomDoc`.
- Trace should inspect documents/compositions that reference atoms.
- Traceability should not rely on `source-atom:*` tags produced by atom-to-task materializers.

## Follow-Up Shape

- Add a test that loads all `desk/atoms/**/*.md` as `AtomDoc`.
- Add a read-side trace command once document-to-atom composition is defined.
- Report unresolved atom references as findings.

## Tags

- system:deskops
- topic:atoms
- topic:validation
- topic:traceability
