## Review
- Correct: The top-level corpus already has an established free-text `provenance` frontmatter style when the source mapping is actually known. See `desk/atoms/atom-anchor-bundles-should-combine-structural-textual-and-contextual-locators.md:5-15` and `desk/atoms/atom-sldb-should-own-tracked-document-structure-for-future-kb-documents.md:5-16`, both of which use `source:*` tags plus a sentence beginning `Derived from ... as a synthesis ...`.
- Blocker: Do not batch-add per-file source claims to the full top-level corpus yet. Inspection of `desk/atoms/*.md` found 74 top-level atoms, but only 2 currently contain any `provenance:` field and only 2 contain any `source:*` tags; 72 still have `tags: []` and the template placeholder body text (for example `desk/atoms/atom-about-concept-should-express-the-primary-semantic-target-of-an-atom.md:1-10,16-18` and `desk/atoms/atom-the-bootstrap-kb-should-welcome-partial-provenance-without-confusing-it-with-validation.md:1-10,17-19`). Adding specific file paths now would create false precision, which the corpus itself warns against in `desk/atoms/atom-the-kb-should-avoid-fake-retroactive-samples-with-no-recoverable-evidence-path.md:16-18`.
- Note: The corpus already endorses provisional provenance and staged backfill. `desk/atoms/kb/bootstrap/provenance/atom-bootstrap-provenance-should-begin-with-source-stubs-before-full-samples.md:32` says bootstrap provenance should start with named source surfaces, source type, and location hints before full samples; `desk/atoms/kb/bootstrap/provenance/atom-bootstrap-kb-should-track-grounding-status-explicitly.md:32` says weak textual provenance should be distinguished from sample-linked or validated support; `desk/atoms/kb/bootstrap/migration/atom-historical-atoms-should-be-backfilled-by-value-and-use-not-all-at-once.md:33` says backfill should be incremental.
- Note: Safe migration wording for atoms whose exact per-file mapping is not yet curated should stay explicitly corpus-level and provisional. Recommended frontmatter value:
  - `provenance: Bootstrap atom carried forward from the legacy Deskops atom corpus (\`desk/atoms/\`). Exact originating source document(s), section-level anchors, and sample bindings have not yet been curated; treat this as provisional corpus-level provenance pending source-stub and sample backfill.`
- Note: That wording aligns with the bootstrap guidance to treat the current Deskops atom corpus as a valid canonical starting surface while remaining open to later provenance enrichment; see `desk/atoms/kb/bootstrap/architecture/atom-bootstrap-kb-should-treat-deskops-atoms-as-the-canonical-bootstrap-surface.md:32-36`. It is safer than `Derived from <specific file>` unless that exact source file has been verified for the individual atom.
- Note: `/home/jp/Upla/kb/plan.md` and `/home/jp/Upla/kb/progress.md` were requested inputs but do not exist in this workspace, so this review is based on the atom corpus itself.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "The review stayed within scope: only `desk/atoms/*.md` plus closely related bootstrap atoms were inspected, no atom files were modified, and the recommendation is limited to safe frontmatter `provenance` wording for uncurated atoms."
    },
    {
      "id": "criterion-2",
      "status": "satisfied",
      "evidence": "Evidence includes file-path and line-range citations for current frontmatter patterns, corpus gaps, and bootstrap provenance rules, plus command outputs showing 74 top-level atoms with only 2 existing `provenance:` fields and 72 placeholder/template atoms."
    }
  ],
  "changedFiles": [
    "/home/jp/Upla/kb/provenance-review.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "ls . && ls desk && find desk -name '*.md'",
      "result": "passed",
      "summary": "Confirmed workspace structure and located the atom corpus under `desk/atoms/`."
    },
    {
      "command": "grep/search for `provenance` and frontmatter markers in `desk/atoms/*.md`",
      "result": "passed",
      "summary": "Found only two top-level atoms with existing `provenance:` frontmatter and verified the current free-text pattern."
    },
    {
      "command": "python count script over `desk/atoms/*.md`",
      "result": "passed",
      "summary": "Counted 74 top-level atoms, 2 with `provenance:`, 2 with `source:*` tags, and 72 with `tags: []`."
    },
    {
      "command": "python/grep check for placeholder answer text in `desk/atoms/*.md`",
      "result": "passed",
      "summary": "Confirmed 72 top-level atoms still contain the template placeholder answer line."
    },
    {
      "command": "nl -ba <file> | sed -n ... on representative top-level and bootstrap provenance atoms",
      "result": "passed",
      "summary": "Captured line-numbered evidence for existing provenance wording, bootstrap guidance, and the warning against false precision."
    },
    {
      "command": "git status --short && git status --short --staged",
      "result": "not_applicable",
      "summary": "Workspace is not a git repository (`fatal: not a git repository`), so staged-file inspection was unavailable here."
    }
  ],
  "validationOutput": [
    "top_level_count=74",
    "top_level_with_frontmatter_provenance=2",
    "empty_tags=72",
    "with_source_tag=2",
    "placeholder_answer_count=72",
    "Existing top-level `provenance:` wording is free-text and synthesis-oriented in the two curated examples."
  ],
  "residualRisks": [
    "Even safe corpus-level provenance remains coarse until per-atom source stubs or samples are curated.",
    "The workspace lacks `plan.md` and `progress.md`, so no prior migration plan could be validated against the corpus.",
    "No git metadata was present, so staged-file state could not be independently verified beyond the absence of a repository."
  ],
  "noStagedFiles": true,
  "diffSummary": "No corpus files were changed; only this review report was written.",
  "reviewFindings": [
    "blocker: avoid mass-applying atom-specific `Derived from <file>` provenance across `desk/atoms/*.md` until per-file mappings are curated.",
    "note: use explicitly provisional corpus-level wording that names `desk/atoms/` as the source surface and says exact document/section/sample mapping is pending."
  ],
  "manualNotes": "If migration proceeds, reserve the current `Derived from ... as a synthesis ...` wording for atoms with verified per-file mappings, and use the provisional corpus-level sentence for the rest until source-stub backfill is done."
}
```