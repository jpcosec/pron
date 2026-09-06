# Knowledge CLI atom candidates for authoring and validation workflow

Basis reviewed:
- `knowledge`
- `source/spec/source_apps/deskops.md`
- `source/spec/DESKOPS_FOR_KNOWLEDGE_MANAGEMENT.md`
- `source/spec/atom_quality/ATOM_AUTHORING_PROCEDURE.md`
- supporting constraints from `source/spec/atom_quality/ATOM_AUTHORING_STANDARD.md`, `source/spec/atom_quality/ATOM_QUALITY_CHECKLIST.md`, `desk/atoms/tag-namespaces.yaml`

## Proposed atoms

### 1) List atoms should optimize corpus discovery and duplicate avoidance during authoring
- **five_wh_one_plus:** `why`
- **answer:** `knowledge list atoms` should optimize corpus discovery and duplicate avoidance because the first authoring move is often checking whether a claim already exists. A simple stable list of `id | title` keeps browsing fast in the terminal while still supporting machine-oriented JSON output when deeper tooling is needed.
- **semantic tags:** `system:knowledge`, `entity:atom`, `topic:knowledge_cli`, `topic:authoring_workflow`, `domain:knowledge_management`
- **metadata tags:** `project:kb`, `source:knowledge_cli`, `source:deskops_km_spec`, `source_kind:code`, `source_kind:spec`, `scope:authoring`, `role:workflow_rule`, `grounding:derived`
- **provenance:** Derived from `knowledge:172-180`, `source/spec/DESKOPS_FOR_KNOWLEDGE_MANAGEMENT.md` sections 5 and 6.2, and `source/spec/source_apps/deskops.md` on preserving a fluent human CLI.

### 2) Show atom should surface the full authoring payload in one inspection view
- **five_wh_one_plus:** `what`
- **answer:** `knowledge show atom` should surface the full authoring payload in one inspection view: stable id, title, dominant 5WH1+ question, path, semantic tags, provenance, and answer. That single-screen readback makes review and refinement faster because authors can confirm both the knowledge claim and its retrieval shape without opening the file manually.
- **semantic tags:** `system:knowledge`, `entity:atom`, `topic:knowledge_cli`, `topic:authoring_workflow`, `topic:atom_review`
- **metadata tags:** `project:kb`, `source:knowledge_cli`, `source:deskops_km_spec`, `source_kind:code`, `source_kind:spec`, `scope:authoring`, `role:workflow_rule`, `grounding:derived`
- **provenance:** Derived from `knowledge:183-201`, `source/spec/DESKOPS_FOR_KNOWLEDGE_MANAGEMENT.md` section 6.2, and `source/spec/atom_quality/ATOM_AUTHORING_PROCEDURE.md` step 9 on checklist review.

### 3) Add atom should create a valid atom from the minimum durable knowledge fields
- **five_wh_one_plus:** `how`
- **answer:** `knowledge add atom` should create a valid atom from the minimum durable knowledge fields: title, 5WH1+ question, answer, and semantic tags, with a stable id generated from the title unless explicitly overridden. This keeps atom creation low-friction while still enforcing the core atomic contract instead of allowing arbitrary note-shaped documents.
- **semantic tags:** `system:knowledge`, `entity:atom`, `topic:knowledge_cli`, `topic:atom_creation`, `domain:knowledge_management`
- **metadata tags:** `project:kb`, `source:knowledge_cli`, `source:atom_authoring_procedure`, `source_kind:code`, `source_kind:spec`, `scope:authoring`, `role:workflow_rule`, `grounding:derived`
- **provenance:** Derived from `knowledge:204-230`, `source/spec/DESKOPS_FOR_KNOWLEDGE_MANAGEMENT.md` section 5, and `source/spec/atom_quality/ATOM_AUTHORING_PROCEDURE.md` steps 3-5.

### 4) Add atom should keep knowledge semantics in the atom file and editorial metadata in the registry
- **five_wh_one_plus:** `how`
- **answer:** The add flow should keep knowledge semantics in the atom file and editorial metadata in the registry by writing the atom document with `id`, `title`, `five_wh_one_plus`, `tags`, and answer, while mirroring provenance statements and metadata tags into `metadata/atoms/atom-metadata-registry.yaml`. This preserves the atom as a pure knowledge unit without losing the operational metadata needed for governance and retrieval.
- **semantic tags:** `system:knowledge`, `entity:atom`, `entity:metadata_registry`, `topic:knowledge_cli`, `topic:atom_metadata`
- **metadata tags:** `project:kb`, `source:knowledge_cli`, `source:atom_metadata_doc`, `source_kind:code`, `source_kind:spec`, `scope:authoring`, `role:modeling_rule`, `grounding:derived`
- **provenance:** Derived from `knowledge:221-244`, `metadata/atoms/atom-metadata-registry.yaml`, and the separation principle reflected in `source/spec/DESKOPS_FOR_KNOWLEDGE_MANAGEMENT.md` and `source/spec/atom_quality/ATOM_AUTHORING_STANDARD.md`.

### 5) Set metadata should support post-creation enrichment without reopening the atom text
- **five_wh_one_plus:** `why`
- **answer:** `knowledge set-metadata` should support post-creation enrichment without reopening the atom text because provenance wording, scope, role, and grounding often become clearer after the answer itself is drafted. A dedicated metadata command lets authors refine governance metadata incrementally while keeping the atom body focused on the reusable claim.
- **semantic tags:** `system:knowledge`, `entity:metadata_registry`, `entity:atom`, `topic:knowledge_cli`, `topic:authoring_workflow`
- **metadata tags:** `project:kb`, `source:knowledge_cli`, `source:atom_authoring_procedure`, `source_kind:code`, `source_kind:spec`, `scope:authoring`, `role:workflow_rule`, `grounding:derived`
- **provenance:** Derived from `knowledge:278-297`, `source/spec/atom_quality/ATOM_AUTHORING_PROCEDURE.md` steps 6-8, and the registry conventions visible in `metadata/atoms/atom-metadata-registry.yaml`.

### 6) Selector lookup should allow fast human recall but fail loudly on ambiguity
- **five_wh_one_plus:** `how`
- **answer:** Atom lookup in list/show/set-metadata should allow fast human recall by accepting exact ids, filenames, and stems, then falling back to substring matching only when that still resolves to one target. The UX should fail loudly on ambiguity so speed does not silently turn into edits or inspections on the wrong atom.
- **semantic tags:** `system:knowledge`, `entity:atom`, `topic:knowledge_cli`, `topic:navigation`, `domain:knowledge_management`
- **metadata tags:** `project:kb`, `source:knowledge_cli`, `source:deskops_km_spec`, `source_kind:code`, `source_kind:spec`, `scope:authoring`, `role:workflow_rule`, `grounding:derived`
- **provenance:** Derived from `knowledge:108-120`, `knowledge:183-185`, `knowledge:264-266`, `knowledge:279-280`, and `source/spec/source_apps/deskops.md` on direct work-language navigation.

### 7) Semantic and metadata tags should be syntax-checked at write time
- **five_wh_one_plus:** `why`
- **answer:** Semantic and metadata tags should be syntax-checked at write time so authors get immediate feedback when a tag falls outside the namespaced contract. Early rejection keeps retrieval surfaces coherent and prevents malformed tags from entering either the atom documents or the metadata registry.
- **semantic tags:** `system:knowledge`, `entity:atom`, `entity:metadata_registry`, `topic:knowledge_cli`, `topic:tagging`
- **metadata tags:** `project:kb`, `source:knowledge_cli`, `source:atom_authoring_standard`, `source_kind:code`, `source_kind:spec`, `scope:authoring`, `role:governance_rule`, `grounding:derived`
- **provenance:** Derived from `knowledge:156-169`, `desk/atoms/tag-namespaces.yaml`, and `source/spec/atom_quality/ATOM_AUTHORING_STANDARD.md` plus `ATOM_AUTHORING_PROCEDURE.md` on namespaced tagging discipline.

### 8) Validate should be the authoring completion gate, not only a storage health check
- **five_wh_one_plus:** `why`
- **answer:** `knowledge validate` should be the authoring completion gate, not only a storage health check, because a finished atom needs both repository integrity and content-level acceptability. The current flow already proves store and graph consistency, but the intended UX should eventually extend that gate to atom-quality checks such as missing answer blocks, empty tags, absent provenance, and other checklist failures.
- **semantic tags:** `system:knowledge`, `entity:atom`, `topic:knowledge_cli`, `topic:validation`, `domain:knowledge_management`
- **metadata tags:** `project:kb`, `source:knowledge_cli`, `source:atom_quality_checklist`, `source:atom_authoring_procedure`, `source_kind:code`, `source_kind:spec`, `scope:validation`, `role:governance_rule`, `grounding:derived`
- **provenance:** Derived from `knowledge:426-437`, observed `./knowledge validate --root .` output, `source/spec/atom_quality/ATOM_AUTHORING_PROCEDURE.md` step 9, and `source/spec/atom_quality/ATOM_QUALITY_CHECKLIST.md`.

## Implementation-derived notes
- `knowledge list atoms` currently provides exactly the lightweight `id | title` browsing surface that supports duplicate avoidance.
- `knowledge show atom` already exposes the main authoring fields in one terminal view.
- `knowledge add atom` currently writes new atoms flat under `desk/atoms/` rather than asking for a taxonomy path.
- `knowledge set-metadata` replaces the submitted metadata-tag set for the selected atom, which matches a deliberate registry-edit surface but may surprise users expecting additive updates.
- `knowledge validate` currently runs SLDB update/check plus `deskops graph missing`; it does not yet run atom-quality linting.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Produced 8 concrete atom proposals tied to specific implementation and spec file paths, with implementation-derived findings called out by path and line ranges."
    }
  ],
  "changedFiles": [
    "/home/jp/Upla/kb/subagent-outputs/knowledge-authoring-atoms.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "./knowledge --help",
      "result": "passed",
      "summary": "Confirmed exposed CLI surfaces include list/show/add/set-metadata/graph/validate."
    },
    {
      "command": "./knowledge list atoms --root . | head -n 8",
      "result": "passed",
      "summary": "Verified current list UX is a lightweight id-title corpus browser."
    },
    {
      "command": "./knowledge show atom atom-knowledge-cli-should-separate-knowledge-operations-from-operational-workflow --root .",
      "result": "passed",
      "summary": "Verified current show UX surfaces id, title, question, path, tags, provenance, and answer."
    },
    {
      "command": "./knowledge list metadata --root . | head -n 8",
      "result": "passed",
      "summary": "Verified metadata registry is a first-class companion surface with namespace-oriented output."
    },
    {
      "command": "./knowledge add atom --help",
      "result": "passed",
      "summary": "Confirmed required add arguments and metadata-tag support without mutating the repo."
    },
    {
      "command": "./knowledge set-metadata --help",
      "result": "passed",
      "summary": "Confirmed dedicated metadata update surface and its replace-style flags."
    },
    {
      "command": "./knowledge show metadata atom-anchor-bundles-should-combine-structural-textual-and-contextual-locators --root .",
      "result": "passed",
      "summary": "Verified registry record shape for provenance_statement and grouped metadata_tags."
    },
    {
      "command": "./knowledge validate --root .",
      "result": "passed",
      "summary": "Validated current implementation checks store update, store integrity, and missing graph references."
    },
    {
      "command": "nl -ba knowledge | sed -n '1,620p'",
      "result": "passed",
      "summary": "Captured line-referenced implementation evidence for proposals and review findings."
    }
  ],
  "validationOutput": [
    "Updated store at /home/jp/Upla/kb/.sldb",
    "Semantic index: 100 processed, 0 missing",
    "Sections index: 100 processed, 0 missing, 0 empty, 0 unparseable headings",
    "PASS: store integrity",
    "No missing graph references found."
  ],
  "residualRisks": [
    "Did not execute mutating add/set-metadata flows because the task forbade editing existing content; candidate atoms for those commands were inferred from implementation and help output rather than end-to-end writes.",
    "The current validate command proves repository and graph integrity but not full atom-quality acceptance, so intended UX proposals for validation extend beyond what is presently automated."
  ],
  "noStagedFiles": true,
  "diffSummary": "Wrote a new findings document with 8 CLI authoring/validation atom proposals and acceptance evidence.",
  "reviewFindings": [
    "info: knowledge:172-180 - `list atoms` is intentionally minimal text UX (`id | title`), which strongly supports discovery and duplicate avoidance during authoring.",
    "info: knowledge:183-201 - `show atom` already exposes the main authoring payload in one terminal view: id, title, question, path, tags, provenance, and answer.",
    "info: knowledge:204-244 - `add atom` enforces core atom fields, auto-slugifies ids, writes the atom file, and mirrors provenance/metadata tags into the metadata registry.",
    "medium: knowledge:216-219 - new atoms are always written to `desk/atoms/<atom-id>.md`, so taxonomy placement is not yet part of the authoring UX.",
    "info: knowledge:278-295 - `set-metadata` is a dedicated post-creation enrichment surface, but submitted metadata tags replace the grouped set for that atom rather than merging incrementally.",
    "medium: knowledge:426-437 - `validate` currently checks SLDB store health and missing graph references, but it does not yet enforce the atom-quality checklist described in `source/spec/atom_quality/ATOM_QUALITY_CHECKLIST.md`."
  ],
  "manualNotes": "No existing repo files were edited. Findings were written only to the required output path."
}
```