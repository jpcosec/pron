# Knowledge graph atom proposals

## Scope reviewed
- `knowledge`
- `.sldb/runtime/knowledge_graph.kg.json`
- `source/spec/source_apps/kgdb.md`
- `source/spec/source_apps/graph_ui.md`
- `source/spec/GRAPH_ARCHITECTURE.md`

## Concrete review findings
- **high** — `knowledge` and `.sldb/runtime/knowledge_graph.kg.json`: the `knowledge graph list/show` path is implemented and the snapshot loads successfully, but the current snapshot has **137 nodes and 0 total edges**, so graph inspection is presently node-only rather than provenance-relational.
- **high** — `knowledge:375-380`: `knowledge graph trace` only delegates to `deskops graph trace`; runtime output currently says **"graph trace grammar added; implementation deferred."** This leaves a core provenance-retrieval command architecturally present but operationally incomplete.
- **medium** — `knowledge:354-381`: `build`, `missing`, `neighbors`, and `trace` are knowledge-layer entrypoints that delegate outward to `deskops`, while `list` and `show` read the local snapshot directly. That split is useful, but it means graph inspection can appear healthy even when the relational layer is still unmaterialized.
- **low** — `knowledge:321-350, 383-428`: snapshot selection is human-usable because `show` resolves by `node_id`, label, or path, and prints raw node payloads. This aligns with a knowledge-layer inspection role rather than a semantic reinterpretation role.

## Strong atom proposals

### 1) Graph build should be the projection refresh boundary between documents and graph retrieval
- **five_wh_one_plus:** how
- **answer:** The `knowledge graph build` command should be treated as the refresh boundary that materializes a new queryable graph projection from the document corpus, not as a new source of truth. This matches the architecture: documents stay primary, while the graph becomes the refreshed retrieval surface for lineage and support queries.
- **semantic tags:**
  - `system:knowledge`
  - `system:kgdb`
  - `topic:knowledge_graph`
  - `topic:provenance`
  - `graph:provenance`
  - `layer:graph_provenance`
- **metadata tags:**
  - `project:kb`
  - `source:knowledge_cli_and_graph_specs`
  - `source_kind:spec`
  - `grounding:validated_doc_reading`
  - `role:architecture_atom`
  - `method:provenance_analysis`
- **provenance statement:** Derived from `knowledge` (`cmd_graph_build`), `source/spec/source_apps/kgdb.md`, and `source/spec/GRAPH_ARCHITECTURE.md`, which consistently frame the graph as a queryable projection over document-grounded truth.

### 2) Knowledge graph list should provide fast snapshot-native node inventory without semantic reinterpretation
- **five_wh_one_plus:** what
- **answer:** `knowledge graph list` should exist as a fast, local inventory of graph nodes taken directly from the snapshot, with optional type filtering, rather than as a heavy traversal command. Its job in the knowledge layer is discoverability of what the graph currently materializes, not inference about what relations ought to exist.
- **semantic tags:**
  - `system:knowledge`
  - `topic:knowledge_cli`
  - `topic:knowledge_graph`
  - `graph:provenance`
  - `entity:atom`
- **metadata tags:**
  - `project:kb`
  - `source:knowledge_cli`
  - `source_kind:spec`
  - `grounding:validated_doc_reading`
  - `role:query_atom`
  - `method:view_generation`
- **provenance statement:** Derived from `knowledge` (`cmd_graph_list`) and the current `.sldb/runtime/knowledge_graph.kg.json` snapshot shape, which exposes nodes as inspectable projection records.

### 3) Knowledge graph show should expose raw node identity semantics path and edge payloads for auditability
- **five_wh_one_plus:** how
- **answer:** `knowledge graph show` should expose a node's identity, type, semantic label, path, and raw edge payloads without trying to reinterpret the underlying claim. In the knowledge layer, this supports auditability and debugging of graph materialization rather than replacing the original atom or source document.
- **semantic tags:**
  - `system:knowledge`
  - `topic:knowledge_cli`
  - `topic:knowledge_graph`
  - `graph:provenance`
  - `entity:atom`
- **metadata tags:**
  - `project:kb`
  - `source:knowledge_cli`
  - `source_kind:spec`
  - `grounding:validated_doc_reading`
  - `role:inspection_atom`
  - `method:view_generation`
- **provenance statement:** Derived from `knowledge` (`find_snapshot_node`, `cmd_graph_show`) and `source/spec/GRAPH_ARCHITECTURE.md`, which positions the graph as a recoverable relational layer over document-grounded entities.

### 4) Graph neighbors should remain explicit adjacency inspection rather than inferred conceptual similarity
- **five_wh_one_plus:** what
- **answer:** `knowledge graph neighbors` should mean inspection of explicit incoming and outgoing graph adjacencies, not fuzzy topical similarity or embedding-style relatedness. That preserves the graph as a fact-bearing provenance surface where each neighboring relation is inspectable and attributable.
- **semantic tags:**
  - `system:knowledge`
  - `topic:knowledge_graph`
  - `topic:query_retrieval`
  - `graph:provenance`
  - `graph:lineage`
- **metadata tags:**
  - `project:kb`
  - `source:knowledge_cli_and_graph_architecture`
  - `source_kind:spec`
  - `grounding:validated_doc_reading`
  - `role:relation_atom`
  - `method:provenance_analysis`
- **provenance statement:** Derived from `knowledge` (`cmd_graph_neighbors`) and `source/spec/GRAPH_ARCHITECTURE.md`, which emphasizes explicit support, derivation, and composition edges as the graph's core value.

### 5) Graph trace should answer provenance lineage across the source sample atom composition chain
- **five_wh_one_plus:** how
- **answer:** `knowledge graph trace` should operationalize provenance lineage by walking the chain from `Source` to `Sample` to `Atom` to `Composition` and back as needed. In this KB, trace is the command that should make source-grounded support recoverable to a human, not just prove that a node exists.
- **semantic tags:**
  - `system:knowledge`
  - `topic:provenance_retrieval`
  - `topic:knowledge_graph`
  - `graph:lineage`
  - `graph:provenance`
  - `layer:graph_provenance`
- **metadata tags:**
  - `project:kb`
  - `source:graph_architecture_and_kgdb`
  - `source_kind:spec`
  - `grounding:validated_doc_reading`
  - `role:core_capability`
  - `method:provenance_analysis`
- **provenance statement:** Derived from `knowledge` (`cmd_graph_trace`), `source/spec/source_apps/kgdb.md`, and `source/spec/GRAPH_ARCHITECTURE.md`, all of which identify traceable lineage as a central graph function.

### 6) Graph missing should serve as a knowledge-layer diagnostics surface for unresolved relational targets
- **five_wh_one_plus:** why
- **answer:** `knowledge graph missing` should exist to surface unresolved graph targets and broken relation intents as diagnostics within the knowledge layer itself. Missing-reference visibility matters because provenance gaps and unmaterialized links are governance problems, not merely implementation details.
- **semantic tags:**
  - `system:knowledge`
  - `topic:knowledge_graph`
  - `topic:provenance`
  - `graph:provenance`
  - `layer:graph_provenance`
- **metadata tags:**
  - `project:kb`
  - `source:knowledge_cli_and_graph_architecture`
  - `source_kind:spec`
  - `grounding:validated_doc_reading`
  - `role:diagnostics_atom`
  - `method:provenance_analysis`
- **provenance statement:** Derived from `knowledge` (`cmd_graph_missing`, `cmd_validate`) and `source/spec/GRAPH_ARCHITECTURE.md`, which explicitly treats coverage and diagnostics as graph responsibilities.

### 7) Snapshot-native list and show can live in the knowledge layer even when traversal delegates to deskops
- **five_wh_one_plus:** where
- **answer:** The right place for `graph list` and `graph show` is the local knowledge layer because they read and expose the current graph snapshot directly, while traversal-heavy operations may still delegate to the lower graph runtime. This split keeps everyday inspection close to the KB authoring surface without pretending the knowledge CLI owns graph execution internals.
- **semantic tags:**
  - `system:knowledge`
  - `system:kgdb`
  - `topic:knowledge_cli`
  - `topic:knowledge_graph`
  - `layer:graph_provenance`
- **metadata tags:**
  - `project:kb`
  - `source:knowledge_cli`
  - `source_kind:spec`
  - `grounding:validated_doc_reading`
  - `role:layering_atom`
  - `method:view_generation`
- **provenance statement:** Derived from `knowledge:354-428`, where `build/missing/neighbors/trace` delegate to `deskops` but `list/show` operate directly over `.sldb/runtime/knowledge_graph.kg.json`.

### 8) A zero-edge graph snapshot should be treated as an incomplete provenance build rather than a healthy graph
- **five_wh_one_plus:** what
- **answer:** A graph snapshot with nodes but no edges should be treated as an incomplete provenance build, because the KB architecture expects recoverable support, derivation, and composition relations, not just labeled entities. Node-only materialization is still useful for inventory, but it does not yet satisfy the graph's intended knowledge-layer role.
- **semantic tags:**
  - `system:knowledge`
  - `system:kgdb`
  - `topic:knowledge_graph`
  - `topic:provenance_retrieval`
  - `graph:provenance`
  - `graph:lineage`
- **metadata tags:**
  - `project:kb`
  - `source:knowledge_snapshot_and_graph_architecture`
  - `source_kind:spec`
  - `grounding:validated_doc_reading`
  - `role:diagnostics_atom`
  - `method:provenance_analysis`
- **provenance statement:** Derived from `.sldb/runtime/knowledge_graph.kg.json` as observed locally during review and from `source/spec/GRAPH_ARCHITECTURE.md`, which requires support, derivation, and lineage relations to be materially recoverable.

## Residual risks
- These proposals are intentionally scoped to graph functionality in the `knowledge` CLI and do not cover non-graph commands.
- `trace`, `neighbors`, and `missing` ultimately depend on delegated `deskops` behavior, so some intended semantics are inferred from architecture docs plus current runtime output rather than from a fully implemented local traversal engine.
- The current snapshot is relation-poor, so proposals about lineage and support are architecture-faithful but only partially runtime-confirmed in this repository state.

```acceptance-report
{
  "criteriaSatisfied": [
    {
      "id": "criterion-1",
      "status": "satisfied",
      "evidence": "Included concrete graph-function findings with file paths and severity, plus 8 atom proposals grounded in `knowledge`, `.sldb/runtime/knowledge_graph.kg.json`, `source/spec/source_apps/kgdb.md`, `source/spec/source_apps/graph_ui.md`, and `source/spec/GRAPH_ARCHITECTURE.md`."
    }
  ],
  "changedFiles": [
    "/home/jp/Upla/kb/subagent-outputs/knowledge-graph-atoms.md"
  ],
  "testsAddedOrUpdated": [],
  "commandsRun": [
    {
      "command": "python3 - <<'PY' ... read .sldb/runtime/knowledge_graph.kg.json ... PY",
      "result": "passed",
      "summary": "Confirmed snapshot has 137 nodes, 0 total edges, types atom/config_file/pill/spec, and does not include every desk atom."
    },
    {
      "command": "python3 ./knowledge graph list --root . --format text | head -n 5",
      "result": "passed",
      "summary": "Verified local list command reads snapshot and emits node inventory."
    },
    {
      "command": "python3 ./knowledge graph missing --root .",
      "result": "passed",
      "summary": "Runtime reported no missing graph references found."
    },
    {
      "command": "python3 ./knowledge graph trace atom:atom-distilled-from-should-link-atoms-to-the-samples-they-abstract --root .",
      "result": "passed",
      "summary": "Runtime reported 'graph trace grammar added; implementation deferred.'"
    },
    {
      "command": "python3 ./knowledge graph neighbors atom:atom-distilled-from-should-link-atoms-to-the-samples-they-abstract --root .",
      "result": "passed",
      "summary": "Verified neighbors command currently reports no incoming or outgoing edges for the inspected node."
    },
    {
      "command": "python3 ./knowledge graph show atom:atom-distilled-from-should-link-atoms-to-the-samples-they-abstract --root .",
      "result": "passed",
      "summary": "Verified show command prints node identity, type, path, and raw JSON payload."
    }
  ],
  "validationOutput": [
    "Snapshot inspection: 137 nodes, 0 total edges.",
    "`knowledge graph missing`: No missing graph references found.",
    "`knowledge graph trace`: graph trace grammar added; implementation deferred.",
    "`knowledge graph neighbors` on inspected node: Outgoing none, Incoming none."
  ],
  "residualRisks": [
    "Current graph snapshot is node-only, so lineage-oriented proposals are architecture-grounded more than runtime-proven.",
    "Delegated deskops behavior may evolve independently of the local `knowledge` wrapper."
  ],
  "noStagedFiles": true,
  "diffSummary": "Created a graph-focused atom proposal report at the required output path; no repository source files were modified.",
  "reviewFindings": [
    "high: knowledge + .sldb/runtime/knowledge_graph.kg.json - graph inspection works but current snapshot has 137 nodes and 0 edges, so graph functionality is materially incomplete for provenance traversal.",
    "high: knowledge:375-380 - `knowledge graph trace` delegates to deskops, and runtime currently reports 'graph trace grammar added; implementation deferred.'",
    "medium: knowledge:354-381 - graph execution is split between local snapshot inspection and delegated deskops traversal, which can mask relational incompleteness if users only run list/show."
  ],
  "manualNotes": "No repo source files were edited. Output written only to the mandated subagent output path."
}
```