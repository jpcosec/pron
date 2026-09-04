# `sldb fields show` fails on every AtomDoc with provenance validation error

## Kind

bug

## Status

closed (data-level fix, 2026-07-31)

## Problem

In store mode, any `sldb fields show docs/<atom>/<field>` query fails with:

```
Unexpected: 1 validation error for AtomDoc
provenance
  Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
```

Reproduced on old atoms without `provenance` in frontmatter (`atom-pills-reference-not-copy`, `atom-deskops`) and on a new atom that does define `provenance` (`atom-role-prompts-are-tracked-documents-agent-files-are-materializations`). Direct extraction (`sldb extract deskops.models:AtomDoc <file> --pythonpath .`) works and returns the correct provenance, and `sldb validate --input` passes idempotently. `sldb docs list --store .sldb` also works.

So the store-backed `fields` path appears to extract or hydrate AtomDoc differently, passing `provenance=None` instead of applying the model default (`""`) or reading frontmatter.

## Impact

- blocks field-level inspection/updates on atoms through the store
- blocks board/field operations that scan AtomDoc (`fields show docs/board-001/tasks` crashes on AtomDoc validation)

## Notes

Found 2026-07-31 while registering atom-anchored drawer task for role-prompt materialization.

## Resolution

Root cause: atoms legitimately lacked `provenance` in frontmatter, but `AtomDoc.provenance` was `str` with default `""` and sldb extraction yields `None` for absent reversible fields, which pydantic rejected.

Fixed at the model level (operator decision: optional field over mass `provenance: ''` insertion):

- `AtomDoc.provenance` is now `str | None = Field(default=None)` and its template marker is `optrev` (optional reversible), so absent provenance extracts as `None`, renders as `provenance: null`, and roundtrips stably. Atoms with a real provenance value keep it in frontmatter.
- Fixed `deskops/cli/model_introspection.py` conflating explicit `default=None` with "no default": added a `REQUIRED` sentinel so optional-None fields are not treated as CLI-required. `deskops/cli/parser.py` now skips both sentinels when carrying defaults.

Verified: `sldb stores check` PASS, `sldb fields show` returns `null` for provenance-less atoms and the real value where present, `deskops add atom` works without `--provenance`, pytest shows no new failures.

Residual: none for this class. Note the canonical location of provenance remains the frontmatter.
