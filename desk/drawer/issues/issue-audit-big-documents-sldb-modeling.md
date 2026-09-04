# Audit big documents SLDB modeling

## Kind

feature

## Status

open

## Problem

Large documents such as README, FAQ, knowledge materialization docs, and diagram explanations are not clearly classified as shallow SLDB documents, composed atom materializations, strict typed documents, or unmodeled prose.

## Desired Outcome

Inventory the big documents and decide their model strategy: shallow body, composed materialization, typed sections, generated projection, or intentionally unmodeled.

## Questions

- Which large docs must be tracked by SLDB now?
- Which big docs should declare source atoms and materialization metadata?
- When does a large document need typed sections instead of a shallow body?

## Related Atoms

- atom-big-documents-need-explicit-modeling-strategy
- atom-main-docs-are-composed-materializations
- atom-materialization-contracts-bind-source-output-validation
