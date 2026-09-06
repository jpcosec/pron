# Code Context

## Files Retrieved
1. `.sldb/core/documents/AtomDoc.yaml` (lines 1-80) - establishes the tracked-document schema (`documents`, `name`, `path`, hashes, tags) and shows the top-level atom entries start immediately in this registry.
2. `.sldb/core/documents/AtomDoc.yaml` (lines 1080-1219) - shows the tail of the registry, including the later top-level atom entries and confirms the document list ends at line 1219.
3. `.sldb/core/documents/AtomDoc.yaml` (lines 395-1068 via targeted path matches) - contains every nested bootstrap atom entry under `desk/atoms/kb/bootstrap/**`.

## Key Code
Critical registry shape in `.sldb/core/documents/AtomDoc.yaml:1-7`:

```yaml
documents:
- name: atom-anchor-bundles-should-combine-structural-textual-and-contextual-locators
  path: desk/atoms/atom-anchor-bundles-should-combine-structural-textual-and-contextual-locators.md
  hash_c: ...
  hash_d: ...
  semantic_tags:
```

Representative nested bootstrap tracking entries from `.sldb/core/documents/AtomDoc.yaml`:
- `.sldb/core/documents/AtomDoc.yaml:395` → `desk/atoms/kb/bootstrap/architecture/atom-bootstrap-kb-should-treat-deskops-atoms-as-the-canonical-bootstrap-surface.md`
- `.sldb/core/documents/AtomDoc.yaml:621` → `desk/atoms/kb/bootstrap/graph/atom-the-kb-needs-three-connected-graph-strata.md`
- `.sldb/core/documents/AtomDoc.yaml:811` → `desk/atoms/kb/bootstrap/provenance/atom-bootstrap-kb-should-track-grounding-status-explicitly.md`
- `.sldb/core/documents/AtomDoc.yaml:1068` → `desk/atoms/kb/bootstrap/workflow/atom-deskops-is-a-bootstrap-surface-not-the-final-kb-container.md`

Representative later top-level tracking entries from `.sldb/core/documents/AtomDoc.yaml:1094-1213`:
- `desk/atoms/atom-the-ontology-loop-should-iterate-by-mapping-relations-before-freezing-entity-taxonomies.md`
- `desk/atoms/atom-derived-from-should-connect-transformed-knowledge-artifacts-across-representation-levels.md`
- `desk/atoms/atom-mentions-symbol-should-express-weaker-symbol-linkage-than-structural-support.md`

Audit result from filesystem-vs-registry comparison:
- Top-level atom markdown files found in `desk/atoms/*.md`: **74**
- Nested bootstrap atom markdown files found in `desk/atoms/kb/**/*.md`: **26**
- Total atom markdown files on disk: **100**
- Total tracked entries in `.sldb/core/documents/AtomDoc.yaml`: **100**
- Untracked top-level atoms: **0**
- Untracked nested bootstrap atoms: **0**
- Registry entries pointing to missing files: **0**

## Architecture
The audit surface is simple:
1. `desk/atoms/*.md` holds the top-level atom corpus.
2. `desk/atoms/kb/**/*.md` holds nested bootstrap atoms grouped by theme (`architecture`, `concept`, `governance`, `graph`, `legacy`, `migration`, `provenance`, `query`, `source`, `structure`, `workflow`).
3. `.sldb/core/documents/AtomDoc.yaml` is the authoritative tracking registry; each tracked atom appears as a `documents` item with a `path` pointing back to one markdown file.

The registry is not ordered strictly by filesystem depth: top-level atoms appear first, then nested bootstrap atoms, then more top-level atoms later in the file. So coverage must be checked by full path comparison, not by assuming one contiguous top-level block.

## Start Here
Open `.sldb/core/documents/AtomDoc.yaml` first, because it is the single source of truth for what is tracked and it already contains the exact filesystem paths needed to compare against `desk/atoms`.

## Findings
- **Are any top-level atoms untracked?** No. All **74/74** files under `desk/atoms/*.md` are present in `.sldb/core/documents/AtomDoc.yaml`.
- **Are nested bootstrap atoms also tracked?** Yes. All **26/26** files under `desk/atoms/kb/**/*.md` are present in `.sldb/core/documents/AtomDoc.yaml`.
- **Any stale tracked paths?** No. Every tracked `path` in `.sldb/core/documents/AtomDoc.yaml` resolves to an existing atom markdown file.

## Acceptance
```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Compared the full on-disk atom sets from desk/atoms/*.md (74 files) and desk/atoms/kb/**/*.md (26 files) against .sldb/core/documents/AtomDoc.yaml and found no untracked top-level or nested bootstrap atoms, with no scope beyond the requested audit."
    }
  ],
  "changedFiles": [
    "/home/jp/Upla/kb/tracking-review.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "python - <<'PY' ... compare filesystem markdown paths to .sldb/core/documents/AtomDoc.yaml ... PY",
      "result": "passed",
      "summary": "Computed counts and set differences: 74 top-level, 26 nested, 100 tracked, 0 untracked, 0 stale registry paths."
    },
    {
      "command": "git status --short",
      "result": "failed",
      "summary": "Current working directory is not inside a git repository."
    },
    {
      "command": "git -C /home/jp/Upla status --short",
      "result": "failed",
      "summary": "/home/jp/Upla is also not a git repository."
    }
  ],
  "validationOutput": [
    "Comparison output: top_count=74, nested_count=26, all_count=100, tracked_count=100, untracked_top=[], untracked_nested=[], tracked_extra=[]",
    "Git validation unavailable because no .git repository exists under /home/jp/Upla."
  ],
  "residualRisks": [
    "The audit only checks path coverage, not whether hashes or semantic tags in AtomDoc.yaml are current.",
    "No git repository is present, so staged-file status could not be verified through git tooling."
  ],
  "noStagedFiles": true,
  "diffSummary": "Added the requested audit report at /home/jp/Upla/kb/tracking-review.md; no source files were modified.",
  "reviewFindings": [
    "no blockers"
  ],
  "manualNotes": "Tracking coverage is complete for both top-level and nested bootstrap atoms. The registry order mixes top-level and nested entries, so future audits should continue comparing full paths rather than assuming contiguous sections."
}
```