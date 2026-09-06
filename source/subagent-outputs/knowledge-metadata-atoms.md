# Knowledge/metadata atom candidate review

## Scope reviewed
- `knowledge`
- `source/spec/ATOM_METADATA_DOC.md`
- `source/spec/atom_quality/ATOM_AUTHORING_STANDARD.md`
- `source/spec/atom_quality/ATOM_TAGGING_AND_PROVENANCE_CONVENTIONS.md`
- `desk/atoms/tag-namespaces.yaml`
- `metadata/atoms/atom-metadata-registry.yaml`
- supporting context: `source/spec/source_apps/deskops.md`, `source/spec/DESKOPS_FOR_KNOWLEDGE_MANAGEMENT.md`

## Review findings
- info: `knowledge:77-82`, `knowledge:300-308`, `knowledge:440-489` - the CLI has distinct surfaces for atom metadata (`metadata/atoms/atom-metadata-registry.yaml`) and atom-side semantic namespaces (`desk/atoms/tag-namespaces.yaml`), which strongly supports proposing split-policy atoms rather than mixed governance/semantic atoms.
- info: `knowledge:204-244` - `knowledge add atom` writes semantic tags into atom frontmatter and grouped metadata tags into the registry in the same workflow, so the implementation already models “one claim, two classification layers.”
- info: `source/spec/ATOM_METADATA_DOC.md:21-29`, `84-96` - the spec is explicit that atoms keep claim, question type, and semantic retrieval tags, while governance, grounding, and broader provenance state belong in metadata, with frontmatter `provenance` retained only for compatibility.
- info: `desk/atoms/tag-namespaces.yaml:1-69` and `knowledge list namespaces --root .` - the atom-side namespace policy is now a narrow allowlist of seven semantic namespaces: `cross`, `domain`, `entity`, `graph`, `layer`, `system`, `topic`.
- info: `metadata/atoms/atom-metadata-registry.yaml:2140-2188` - the registry already carries metadata facets such as `project`, `source`, `source_kind`, `grounding`, `scope`, and `role` for the new knowledge/metadata atoms, so new candidate atoms should sharpen policy boundaries rather than restate the base split.
- low: `source/spec/atom_quality/ATOM_TAGGING_AND_PROVENANCE_CONVENTIONS.md:45-52` still describes tags as helping answer project and grounding questions, but `79-80`, `100-124` move those namespaces to metadata. This makes fine-grained “what lives in atoms vs metadata” atoms especially valuable.
- low: existing atoms already cover some top-level ground, especially `desk/atoms/atom-atom-metadata-should-live-outside-atoms-in-a-dedicated-registry.md` and `desk/atoms/atom-knowledge-cli-should-separate-knowledge-operations-from-operational-workflow.md`; the strongest additions are narrower policy atoms that clarify edge cases and namespace boundaries.

## Proposed atom candidates

### 1) Frontmatter provenance should remain trace text, not the full governance envelope
- **five_wh_one_plus:** what
- **answer:** Frontmatter `provenance` should remain a compact trace statement that tells readers where the claim came from, but it should not absorb the atom’s full governance profile. Project context, grounding state, editorial role, phase, and similar management facets belong in the metadata registry so the atom body stays focused on the claim.
- **semantic tags:**
  - `system:knowledge`
  - `entity:atom`
  - `topic:provenance`
  - `topic:atom_metadata`
- **metadata tags:**
  - `project:kb`
  - `source:atom_metadata_registry`
  - `source_kind:generated_spec`
  - `grounding:derived`
  - `scope:meta`
  - `role:definition`
- **provenance:** Derived from `source/spec/ATOM_METADATA_DOC.md`, `source/spec/atom_quality/ATOM_AUTHORING_STANDARD.md`, and `source/spec/atom_quality/ATOM_TAGGING_AND_PROVENANCE_CONVENTIONS.md`.

### 2) Atom semantic tags should be limited to the namespace allowlist defined in tag-namespaces.yaml
- **five_wh_one_plus:** what
- **answer:** Atom-side semantic tags should come only from the namespace families that are explicitly curated in `desk/atoms/tag-namespaces.yaml`. That keeps retrieval semantics stable and prevents governance namespaces from creeping back into atom frontmatter just because they match the generic `namespace:value` syntax.
- **semantic tags:**
  - `system:knowledge`
  - `entity:atom`
  - `entity:tag_facet`
  - `topic:atom_metadata`
- **metadata tags:**
  - `project:kb`
  - `source:tag_namespaces_yaml`
  - `source_kind:source_file`
  - `grounding:derived`
  - `scope:meta`
  - `role:governance_rule`
- **provenance:** Derived from `desk/atoms/tag-namespaces.yaml` and the local `knowledge` CLI implementation.

### 3) Regex-valid metadata namespaces should still be excluded from atom tags
- **five_wh_one_plus:** why
- **answer:** A tag being syntactically valid is not enough to make it atom-semantic. Namespaces like `project:*`, `source:*`, `source_kind:*`, `grounding:*`, `scope:*`, `role:*`, `phase:*`, `bootstrap:*`, `method:*`, `status:*`, and `legacy:*` describe the atom’s curation state or origin, so they should live in metadata even though the CLI can parse them as namespaced tags.
- **semantic tags:**
  - `system:knowledge`
  - `entity:atom`
  - `topic:tag_policy`
  - `topic:atom_metadata`
- **metadata tags:**
  - `project:kb`
  - `source:knowledge_cli_impl`
  - `source_kind:source_file`
  - `grounding:derived`
  - `scope:meta`
  - `role:governance_rule`
- **provenance:** Derived from `knowledge`, `source/spec/ATOM_METADATA_DOC.md`, and `desk/atoms/tag-namespaces.yaml`.

### 4) System tags should identify the subject system, not the curation container
- **five_wh_one_plus:** how
- **answer:** `system:*` should say what system or tool the claim is about, not where the atom is stored or which repo currently curates it. Repository context belongs in metadata as `project:*`, which preserves the difference between subject identity and curation location.
- **semantic tags:**
  - `system:knowledge`
  - `entity:tag_facet`
  - `topic:tag_policy`
- **metadata tags:**
  - `project:kb`
  - `source:atom_tagging_conventions`
  - `source_kind:spec`
  - `grounding:derived`
  - `scope:meta`
  - `role:definition`
- **provenance:** Derived from `source/spec/atom_quality/ATOM_TAGGING_AND_PROVENANCE_CONVENTIONS.md`, `desk/atoms/tag-namespaces.yaml`, and `desk/atoms/atom-project-tags-should-distinguish-repository-context-from-system-identity.md`.

### 5) Cross tags belong on atoms only when the bridge is part of the claim itself
- **five_wh_one_plus:** when
- **answer:** `cross:*` belongs in atom tags only when the atom’s thesis is inherently about a bridge across systems, projects, or graph strata. If the atom merely happens to be curated from multiple sources or projects, that crossing should be expressed in provenance and metadata instead of being treated as atom semantics.
- **semantic tags:**
  - `system:knowledge`
  - `entity:tag_facet`
  - `topic:multi_source`
  - `cross:deskops_kb`
- **metadata tags:**
  - `project:kb`
  - `source:tag_namespaces_yaml`
  - `source_kind:source_file`
  - `grounding:derived`
  - `scope:meta`
  - `role:governance_rule`
- **provenance:** Derived from `desk/atoms/tag-namespaces.yaml`, `source/spec/ATOM_METADATA_DOC.md`, and `desk/atoms/kb/bootstrap/query/atom-cross-tags-should-mark-bridge-knowledge-between-systems-and-projects.md`.

### 6) Metadata registry records should be the canonical query surface for governance facets
- **five_wh_one_plus:** why
- **answer:** Governance queries such as “which atoms are bootstrap,” “which are source-file-derived,” or “which still need stronger grounding” should resolve against metadata registry records rather than atom tags alone. That keeps evidentiary and editorial filtering explicit without polluting claim-level retrieval semantics.
- **semantic tags:**
  - `system:knowledge`
  - `entity:metadata_registry`
  - `topic:query`
  - `topic:atom_metadata`
- **metadata tags:**
  - `project:kb`
  - `source:atom_metadata_registry`
  - `source_kind:generated_spec`
  - `grounding:derived`
  - `scope:meta`
  - `role:retrieval_rule`
- **provenance:** Derived from `metadata/atoms/atom-metadata-registry.yaml`, `source/spec/ATOM_METADATA_DOC.md`, and the local `knowledge` CLI metadata commands.

### 7) Metadata source tags should name the immediate authoring source, while provenance carries multi-source detail
- **five_wh_one_plus:** what
- **answer:** The registry’s `source:*` tag should identify the immediate source surface from which the atom was authored, using one principal source when possible. When an atom synthesizes multiple documents, the fine-grained combination should be spelled out in the provenance statement rather than expanded into many `source:*` tags.
- **semantic tags:**
  - `system:knowledge`
  - `entity:metadata_registry`
  - `topic:provenance`
  - `topic:multi_source`
- **metadata tags:**
  - `project:kb`
  - `source:atom_tagging_conventions`
  - `source_kind:spec`
  - `grounding:derived`
  - `scope:meta`
  - `role:definition`
- **provenance:** Derived from `source/spec/atom_quality/ATOM_TAGGING_AND_PROVENANCE_CONVENTIONS.md` and `metadata/atoms/atom-metadata-registry.yaml`.

### 8) The knowledge CLI already models a two-surface policy: atoms/namespaces versus metadata/registry
- **five_wh_one_plus:** why
- **answer:** The local `knowledge` CLI treats atom content, semantic namespaces, and metadata records as separate surfaces, which is a strong implementation signal about intended policy. Because the interface already separates `list/show atoms`, `list namespaces`, and `list/show/set metadata`, atom authoring rules should align with that split instead of re-mixing governance into frontmatter tags.
- **semantic tags:**
  - `system:knowledge`
  - `topic:knowledge_cli`
  - `topic:atom_metadata`
  - `entity:metadata_registry`
- **metadata tags:**
  - `project:kb`
  - `source:knowledge_cli_impl`
  - `source_kind:source_file`
  - `grounding:derived`
  - `scope:meta`
  - `role:architecture_decision`
- **provenance:** Derived from the local `knowledge` CLI implementation, `source/spec/ATOM_METADATA_DOC.md`, and `desk/atoms/tag-namespaces.yaml`.

## Residual risks
- Some policy space is already partially covered by existing atoms, so the parent should deduplicate against `desk/atoms/atom-atom-metadata-should-live-outside-atoms-in-a-dedicated-registry.md`, `desk/atoms/atom-project-tags-should-distinguish-repository-context-from-system-identity.md`, and `desk/atoms/kb/bootstrap/query/atom-cross-tags-should-mark-bridge-knowledge-between-systems-and-projects.md` before authoring.
- `source/spec/atom_quality/ATOM_TAGGING_AND_PROVENANCE_CONVENTIONS.md` still contains older wording that can blur whether grounding/project belong in tags or metadata; if that spec is later tightened, some proposal wording may want slight normalization.
- The current CLI validates tag syntax but does not appear to enforce the semantic namespace allowlist at write time, so policy atoms may precede enforcement code.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Produced 8 concrete atom proposals plus review findings with file paths and severities, grounded in `knowledge`, `source/spec/ATOM_METADATA_DOC.md`, `source/spec/atom_quality/ATOM_TAGGING_AND_PROVENANCE_CONVENTIONS.md`, `desk/atoms/tag-namespaces.yaml`, and `metadata/atoms/atom-metadata-registry.yaml`."
    }
  ],
  "changedFiles": [
    "/home/jp/Upla/kb/subagent-outputs/knowledge-metadata-atoms.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "./knowledge list namespaces --root .",
      "result": "passed",
      "summary": "Returned the seven atom-side semantic namespaces: cross, domain, entity, graph, layer, system, topic."
    },
    {
      "command": "./knowledge list metadata --root . | tail -n 15",
      "result": "passed",
      "summary": "Confirmed recent records use metadata namespaces such as project, source, source_kind, grounding, scope, role, phase, bootstrap, and method."
    },
    {
      "command": "./knowledge show metadata atom-knowledge-cli-should-separate-knowledge-operations-from-operational-workflow --root .",
      "result": "passed",
      "summary": "Verified a concrete metadata record for the knowledge CLI atom with separated metadata tags."
    },
    {
      "command": "nl -ba knowledge | sed -n '70,120p'; nl -ba knowledge | sed -n '150,320p'; nl -ba knowledge | sed -n '440,490p'",
      "result": "passed",
      "summary": "Captured implementation evidence for separated atom, namespace, and metadata surfaces."
    }
  ],
  "validationOutput": [
    "`knowledge` defines separate paths for atoms (`desk/atoms`), metadata registry (`metadata/atoms/atom-metadata-registry.yaml`), and semantic namespaces (`desk/atoms/tag-namespaces.yaml`).",
    "The CLI parser exposes separate commands for `list atoms`, `list metadata`, `list namespaces`, `show atom`, `show metadata`, and `set-metadata`."
  ],
  "residualRisks": [
    "Existing atoms already cover some top-level separation themes, so deduplication is needed before authoring.",
    "Tag syntax is validated by the CLI, but semantic namespace enforcement is not clearly enforced at write time.",
    "One conventions spec still contains wording that can blur tags versus metadata, so future doc cleanup may refine these proposals."
  ],
  "noStagedFiles": true,
  "diffSummary": "Wrote the requested findings report with review findings, 8 atom proposals, and an acceptance report.",
  "reviewFindings": [
    "info: knowledge:77-82,300-308,440-489 - implementation cleanly separates metadata registry access from semantic namespace access.",
    "info: source/spec/ATOM_METADATA_DOC.md:21-29,84-96 - docs explicitly place governance and provenance-status facets in metadata, not atoms.",
    "low: source/spec/atom_quality/ATOM_TAGGING_AND_PROVENANCE_CONVENTIONS.md:45-52 vs 79-80,100-124 - some wording still blurs whether project/grounding are tag concerns or metadata concerns."
  ],
  "manualNotes": "No repository source files were edited; only the required output report was written."
}
```