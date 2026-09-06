# Knowledge CLI core atom candidates

Scope reviewed:
- `knowledge`
- `source/spec/source_apps/deskops.md`
- `source/spec/DESKOPS_FOR_KNOWLEDGE_MANAGEMENT.md`
- `source/spec/ATOM_METADATA_DOC.md`

The local `knowledge` CLI is a knowledge-scoped surface, not a reproduction of the broader `deskops` operational workflow. Its implemented boundary is atoms, atom metadata, graph inspection, and validation; it deliberately omits board, task, ritual, and next-action commands that `deskops` currently uses as its workflow layer.

## Proposed atoms

### 1. Knowledge CLI should expose knowledge artifacts without inheriting workflow commands
- **title:** Knowledge CLI should expose knowledge artifacts without inheriting workflow commands
- **five_wh_one_plus:** why
- **answer:** The `knowledge` CLI is explicitly scoped to knowledge artifacts because its parser only exposes `list`, `show`, `add`, `set-metadata`, `graph`, and `validate`, all oriented around atoms, metadata, and graph health. This differs from `deskops`, whose observed workflow surface also includes board, task, ritual, and next-action commands, so the new CLI defines a cleaner knowledge boundary rather than a full operational shell.
- **semantic tags:** `system:knowledge`, `system:deskops`, `topic:knowledge_cli`, `topic:workflow_separation`, `domain:knowledge_management`
- **metadata tags:**
  - `project:kb`
  - `source:knowledge_cli_impl`
  - `source:deskops_spec`
  - `scope:core_cli`
  - `role:boundary_definition`
  - `method:implementation_review`
- **provenance statement:** Derived from `knowledge:441-526` and `source/spec/DESKOPS_FOR_KNOWLEDGE_MANAGEMENT.md:160-164,209,319-321,353`.

### 2. Knowledge CLI should keep atom authoring centered on the minimal atom contract
- **title:** Knowledge CLI should keep atom authoring centered on the minimal atom contract
- **five_wh_one_plus:** what
- **answer:** `knowledge add atom` only requires title, question type, and answer, then adds semantic tags and optional provenance around that core. This preserves the deskops atomization discipline while excluding broader workflow fields, so authoring stays focused on producing a small reusable knowledge unit rather than an operational record.
- **semantic tags:** `system:knowledge`, `entity:atom`, `topic:knowledge_cli`, `topic:atom_metadata`, `domain:knowledge_representation`
- **metadata tags:**
  - `project:kb`
  - `source:knowledge_cli_impl`
  - `source:deskops_spec`
  - `scope:atom_authoring`
  - `role:core_contract`
  - `method:implementation_review`
- **provenance statement:** Derived from `knowledge:204-246,474-482` and `source/spec/source_apps/deskops.md:12-18`.

### 3. Knowledge CLI should separate semantic atom tags from metadata-registry tags
- **title:** Knowledge CLI should separate semantic atom tags from metadata-registry tags
- **five_wh_one_plus:** how
- **answer:** The implementation validates semantic tags for the atom frontmatter and groups metadata tags into registry namespaces before saving them separately. That makes the CLI enforce the metadata split described in `ATOM_METADATA_DOC`, unlike the older deskops-shaped practice where governance and provenance information tended to accumulate inside the atom surface.
- **semantic tags:** `system:knowledge`, `entity:metadata_registry`, `entity:atom`, `topic:atom_metadata`, `topic:knowledge_cli`
- **metadata tags:**
  - `project:kb`
  - `source:knowledge_cli_impl`
  - `source:atom_metadata_doc`
  - `scope:metadata_boundary`
  - `role:modeling_rule`
  - `method:implementation_review`
- **provenance statement:** Derived from `knowledge:156-168,207-242,278-295` and `source/spec/ATOM_METADATA_DOC.md:23-29,44-45`.

### 4. Knowledge CLI should preserve id-first browsing of atoms as a knowledge retrieval surface
- **title:** Knowledge CLI should preserve id-first browsing of atoms as a knowledge retrieval surface
- **five_wh_one_plus:** why
- **answer:** The CLI keeps list/show flows centered on atom ids, titles, paths, and fuzzy selectors, which supports direct knowledge lookup without opening files manually. This carries forward one of deskops' useful browsing affordances, but it narrows the surface to knowledge retrieval instead of mixing retrieval with task navigation.
- **semantic tags:** `system:knowledge`, `entity:atom`, `topic:knowledge_cli`, `topic:knowledge_retrieval`, `domain:knowledge_management`
- **metadata tags:**
  - `project:kb`
  - `source:knowledge_cli_impl`
  - `source:deskops_spec`
  - `scope:browsing`
  - `role:user_surface`
  - `method:implementation_review`
- **provenance statement:** Derived from `knowledge:81-105,172-202,459-470` and `source/spec/DESKOPS_FOR_KNOWLEDGE_MANAGEMENT.md:117-139,189-196`.

### 5. Knowledge CLI should keep graph inspection available as knowledge infrastructure, not workflow UI
- **title:** Knowledge CLI should keep graph inspection available as knowledge infrastructure, not workflow UI
- **five_wh_one_plus:** what
- **answer:** The `graph` subcommands remain part of the CLI even though workflow commands are absent, so graph build, missing-link checks, neighbors, trace, list, and show are treated as first-class KB operations. The implementation still delegates some of these actions to `deskops graph`, which shows the knowledge boundary has been separated at the command surface before being fully separated in infrastructure.
- **semantic tags:** `system:knowledge`, `system:deskops`, `graph:lineage`, `topic:knowledge_graph`, `topic:knowledge_cli`
- **metadata tags:**
  - `project:kb`
  - `source:knowledge_cli_impl`
  - `source:deskops_spec`
  - `scope:graph_surface`
  - `role:boundary_definition`
  - `method:implementation_review`
- **provenance statement:** Derived from `knowledge:354-423,492-522` and `source/spec/source_apps/deskops.md:41-50`.

### 6. Knowledge CLI validation should measure knowledge-store integrity rather than workflow completeness
- **title:** Knowledge CLI validation should measure knowledge-store integrity rather than workflow completeness
- **five_wh_one_plus:** what
- **answer:** The `validate` command runs store update, store check, and graph missing checks, all of which test the health of the knowledge corpus and its graph references. Unlike deskops workflow validation, this boundary ignores task state, board progress, and rituals, framing validation as KB consistency rather than operational readiness.
- **semantic tags:** `system:knowledge`, `system:sldb`, `topic:knowledge_cli`, `topic:knowledge_graph`, `domain:knowledge_management`
- **metadata tags:**
  - `project:kb`
  - `source:knowledge_cli_impl`
  - `scope:validation`
  - `role:integrity_rule`
  - `method:implementation_review`
- **provenance statement:** Derived from `knowledge:426-434,524-526` and `source/spec/DESKOPS_FOR_KNOWLEDGE_MANAGEMENT.md:150-164`.

### 7. Knowledge CLI separates the command surface from deskops faster than it separates the storage substrate
- **title:** Knowledge CLI separates the command surface from deskops faster than it separates the storage substrate
- **five_wh_one_plus:** how
- **answer:** The CLI has its own `knowledge` entrypoint and knowledge-only verbs, but it still reads from `desk/atoms/`, `metadata/atoms/atom-metadata-registry.yaml`, and `.sldb/runtime/knowledge_graph.kg.json`, and it shells out to `deskops graph` for several graph actions. This means the boundary shift is already real at the UX layer, while the underlying corpus location and some graph infrastructure remain inherited from the deskops-era workspace.
- **semantic tags:** `system:knowledge`, `system:deskops`, `layer:structure`, `topic:knowledge_cli`, `cross:deskops_kb`
- **metadata tags:**
  - `project:kb`
  - `source:knowledge_cli_impl`
  - `source:deskops_spec`
  - `scope:architecture_boundary`
  - `role:migration_observation`
  - `legacy:deskops_migration`
- **provenance statement:** Derived from `knowledge:69-79,356-377` and `source/spec/DESKOPS_FOR_KNOWLEDGE_MANAGEMENT.md:271-353`.

### 8. Knowledge CLI treats provenance as compatibility data while pushing broader governance into metadata records
- **title:** Knowledge CLI treats provenance as compatibility data while pushing broader governance into metadata records
- **five_wh_one_plus:** why
- **answer:** New atoms still carry a frontmatter `provenance` field, but the CLI also writes `provenance_statement` and grouped metadata tags into the registry, matching the compatibility note in the metadata spec. This defines a practical boundary: provenance text can remain visible on the atom for traceability, while broader classification and governance live outside the atom itself.
- **semantic tags:** `system:knowledge`, `entity:atom`, `entity:metadata_registry`, `topic:atom_metadata`, `topic:provenance`
- **metadata tags:**
  - `project:kb`
  - `source:knowledge_cli_impl`
  - `source:atom_metadata_doc`
  - `scope:provenance_boundary`
  - `role:compatibility_rule`
  - `method:implementation_review`
- **provenance statement:** Derived from `knowledge:49-63,226-242,288-294` and `source/spec/ATOM_METADATA_DOC.md:44-45,96`.

## Notes on proposal quality
- These proposals stay within the implemented core of the local CLI: atoms, metadata, graph operations, and validation.
- They avoid deskops workflow atoms about boards, tasks, rituals, or next actions except where those commands clarify the new CLI boundary by contrast.
- Proposal 7 is especially important because it captures the main architectural nuance: the knowledge CLI is already separate in purpose even when some storage and graph machinery are still inherited.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Returned 8 concrete atom proposals grounded in `knowledge`, `source/spec/source_apps/deskops.md`, `source/spec/DESKOPS_FOR_KNOWLEDGE_MANAGEMENT.md`, and `source/spec/ATOM_METADATA_DOC.md`, each with file-path provenance statements and boundary-focused findings."
    }
  ],
  "changedFiles": [
    "/home/jp/Upla/kb/subagent-outputs/knowledge-core-atoms.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "python3 ./knowledge --help",
      "result": "passed",
      "summary": "Confirmed the CLI surface is limited to list/show/add/set-metadata/graph/validate."
    },
    {
      "command": "python3 ./knowledge list atoms --root . --format json",
      "result": "passed",
      "summary": "Confirmed atom listing works and returned 103 atoms."
    },
    {
      "command": "python3 ./knowledge list metadata --root . --format json",
      "result": "passed",
      "summary": "Confirmed metadata listing works and returned 103 registry records."
    }
  ],
  "validationOutput": [
    "`knowledge --help` describes the tool as a 'Knowledge-only CLI for atoms and atom metadata.'",
    "Atom listing returned 103 items.",
    "Metadata listing returned 103 records."
  ],
  "residualRisks": [
    "Some graph commands remain implemented as passthroughs to `deskops graph`, so the CLI boundary is cleaner than the underlying infrastructure boundary.",
    "The corpus still lives under `desk/atoms/`, so future atom proposals may need review once storage is moved into a fully separate knowledge-root layout."
  ],
  "noStagedFiles": true,
  "diffSummary": "Wrote one findings document with 8 atom proposals and an attested acceptance report.",
  "reviewFindings": [
    "info: knowledge:441-526 - the parser exposes only knowledge-oriented commands and no task/board/ritual workflow surface.",
    "info: knowledge:204-242 - atom creation enforces the minimal atom contract while splitting metadata tags into the registry.",
    "info: knowledge:354-377 - several graph commands still delegate to `deskops`, showing an incomplete infrastructure separation.",
    "info: source/spec/DESKOPS_FOR_KNOWLEDGE_MANAGEMENT.md:160-164 - deskops retains workflow commands that the local knowledge CLI intentionally omits.",
    "no blockers"
  ],
  "manualNotes": "No project files were edited beyond the required output artifact."
}
```