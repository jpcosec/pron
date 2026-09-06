# Atom Model Alignment and Migration Notes

## Frontmatter provenance is the formal model

The formal `AtomDoc` model records provenance in frontmatter via the `provenance` field. Migration and review work should treat frontmatter provenance as the authoritative atom-level slot instead of adding ad hoc body sections such as `## Procedencia`.

## Why many legacy top-level atoms use provisional corpus-level provenance

Most legacy top-level atoms under `desk/atoms/*.md` were carried forward from the Deskops bootstrap corpus without curated per-atom source bindings, section anchors, or samples. To avoid false precision, the migration aligns those files to the model by adding a provisional corpus-level `provenance` statement that names the legacy corpus surface without claiming unverified source-document detail.

## What remains future backfill work

Exact per-atom source mapping is still pending backfill. That later work should add verified source stubs, document-level references, section-level anchors, and sample bindings where they can be curated confidently. Until then, the provisional corpus-level wording should be read as an honest migration placeholder rather than as validated fine-grained provenance.
