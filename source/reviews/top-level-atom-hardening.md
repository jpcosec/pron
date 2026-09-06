# Top-level atom hardening pass

Reviewed all 74 top-level atoms in `desk/atoms/*.md` and edited 53 of them. The pass stayed out of `desk/atoms/kb/` entirely.

## What changed

- Normalized 46 `role:*` tags into the approved working set (`definition`, `constraint`, `governance_rule`, `relation`, `workflow_rule`, `migration_rule`, `retrieval_rule`, `modeling_rule`).
- Tightened 8 `topic:*` tags where the prior topic was either overly generic or inconsistent with nearby atoms.
- Rewrote 6 answers that were still the thinnest after tag cleanup, keeping the original thesis and `five_wh_one_plus` intact.

## Atoms with answer rewrites

1. `desk/atoms/atom-anchored-in-should-connect-a-sample-to-the-locator-bundle-used-to-recover-it.md`
2. `desk/atoms/atom-drawn-from-section-should-connect-a-support-object-to-an-explicit-source-section.md`
3. `desk/atoms/atom-sampled-from-should-link-a-sample-to-the-exact-source-artifact-it-comes-from.md`
4. `desk/atoms/atom-supported-by-structure-should-link-atoms-to-source-structure-beyond-textual-excerpts.md`
5. `desk/atoms/atom-supports-should-connect-evidence-to-the-atoms-or-compositions-it-justifies.md`
6. `desk/atoms/atom-the-bootstrap-kb-should-welcome-partial-provenance-without-confusing-it-with-validation.md`

## Atoms with tag-only normalization

1. `desk/atoms/atom-api-snapshots-should-be-treated-as-versioned-structured-sources.md`
2. `desk/atoms/atom-atom-answers-should-remain-stable-enough-to-be-recomposed-across-future-kb-layers.md`
3. `desk/atoms/atom-bridge-atoms-should-state-reusable-relations-rather-than-narrating-long-comparisons.md`
4. `desk/atoms/atom-code-sources-should-expose-symbol-aware-support-paths-in-addition-to-raw-text.md`
5. `desk/atoms/atom-composition-should-provide-depth-without-inflating-atomic-answers.md`
6. `desk/atoms/atom-coverage-views-should-reveal-which-source-regions-have-not-yet-produced-atoms.md`
7. `desk/atoms/atom-cross-project-synthesis-atoms-should-be-reviewable-independently-from-local-source-atoms.md`
8. `desk/atoms/atom-deskops-should-remain-the-operational-authoring-surface-for-the-bootstrap-corpus.md`
9. `desk/atoms/atom-exact-quote-anchors-should-be-paired-with-structural-locators-when-possible.md`
10. `desk/atoms/atom-git-sources-should-support-repository-blob-commit-and-file-level-provenance.md`
11. `desk/atoms/atom-graph-ui-should-visualize-lineage-concept-and-structure-perspectives-separately.md`
12. `desk/atoms/atom-hum-scrapper-should-be-treated-as-a-source-acquisition-layer-not-as-knowledge-truth.md`
13. `desk/atoms/atom-json-and-yaml-sources-should-expose-object-path-projections-for-anchoring.md`
14. `desk/atoms/atom-kgdb-should-materialize-queryable-graph-projections-rather-than-documentary-truth.md`
15. `desk/atoms/atom-legacy-extraction-should-preserve-useful-architecture-intuitions-without-inheriting-obsolete-containers.md`
16. `desk/atoms/atom-marcado-should-own-the-annotation-layer-over-samples.md`
17. `desk/atoms/atom-materialized-diagrams-should-be-derived-views-over-atomized-architecture-knowledge.md`
18. `desk/atoms/atom-one-atom-may-be-supported-by-multiple-samples-from-multiple-sources.md`
19. `desk/atoms/atom-ontomap-should-curate-explicit-concept-mappings-across-knowledge-regions.md`
20. `desk/atoms/atom-pdf-sources-need-text-structure-and-layout-projections-at-the-same-time.md`
21. `desk/atoms/atom-provenance-retrieval-and-concept-retrieval-should-remain-interoperable-but-distinct.md`
22. `desk/atoms/atom-queries-should-be-able-to-isolate-atoms-by-graph-stratum.md`
23. `desk/atoms/atom-queries-should-be-able-to-isolate-atoms-by-grounding-maturity.md`
24. `desk/atoms/atom-queries-should-be-able-to-isolate-atoms-that-still-need-samples.md`
25. `desk/atoms/atom-relation-mapping-should-drive-the-discovery-of-missing-entities-in-the-ontology.md`
26. `desk/atoms/atom-repopackage-can-help-model-repository-structure-as-a-source-projection.md`
27. `desk/atoms/atom-reports-should-be-treated-as-compositions-rather-than-as-primary-knowledge-atoms.md`
28. `desk/atoms/atom-samples-should-be-annotable-without-losing-their-deterministic-binding.md`
29. `desk/atoms/atom-section-paths-symbol-paths-and-ast-paths-are-complementary-anchor-families.md`
30. `desk/atoms/atom-sldb-should-own-tracked-document-structure-for-future-kb-documents.md`
31. `desk/atoms/atom-sldb-ui-can-become-a-document-and-sample-inspection-surface-for-the-kb.md`
32. `desk/atoms/atom-source-adapters-should-emit-enough-metadata-to-reconstruct-retrieval-context.md`
33. `desk/atoms/atom-source-adapters-should-expose-enough-structure-to-support-future-graph-derivation.md`
34. `desk/atoms/atom-source-oriented-atoms-and-synthesis-atoms-should-coexist-in-the-same-kb.md`
35. `desk/atoms/atom-spec2viz-should-generate-maintained-diagrams-from-structured-sources.md`
36. `desk/atoms/atom-structural-graph-nodes-should-remain-projected-from-sources-rather-than-authored-as-primary-truths.md`
37. `desk/atoms/atom-support-queries-should-traverse-sources-samples-atoms-and-compositions-as-one-lineage-chain.md`
38. `desk/atoms/atom-the-bootstrap-corpus-should-accumulate-explicit-bridge-atoms-for-every-major-tool-relationship.md`
39. `desk/atoms/atom-the-concept-graph-should-be-atom-centered-rather-than-concept-only.md`
40. `desk/atoms/atom-the-first-bootstrap-corpus-should-prioritize-architecture-governance-and-provenance-atoms.md`
41. `desk/atoms/atom-the-kb-should-distinguish-source-evidence-from-atom-level-synthesis.md`
42. `desk/atoms/atom-the-kb-should-treat-notebooks-as-multi-projection-sources.md`
43. `desk/atoms/atom-the-ontology-loop-should-iterate-by-mapping-relations-before-freezing-entity-taxonomies.md`
44. `desk/atoms/atom-the-source-sample-atom-composition-chain-should-remain-legible-to-humans.md`
45. `desk/atoms/atom-tractatusir-suggests-value-in-addressable-textual-units-for-retrieval.md`
46. `desk/atoms/atom-view-generation-should-be-reversible-back-to-atoms-and-evidence-links.md`
47. `desk/atoms/atom-webpage-sources-should-be-snapshot-bound-before-they-are-sampled.md`

## Topic refinements made

- `topic:knowledge_retrieval` → `topic:coverage` for the coverage-view atom.
- `topic:knowledge_retrieval` → `topic:query_retrieval` for the three atom-isolation query atoms.
- `topic:multi_source` → `topic:source_adapters` for the two source-adapter atoms.
- `topic:structural_graph` → `topic:anchoring` for `supported_by_structure`, which is about evidence binding rather than graph projection.
- `topic:document-structure` → `topic:document_structure` for consistency with the broader underscore-based topic style.

## Atoms considered too ambiguous to refine further safely

- `desk/atoms/atom-graph-ui-should-visualize-lineage-concept-and-structure-perspectives-separately.md` — role normalization was clear, but a more specific topic split between graph inspection and concept navigation would have been speculative.
- `desk/atoms/atom-sldb-ui-can-become-a-document-and-sample-inspection-surface-for-the-kb.md` — role normalization was clear, but a narrower topic than general retrieval/inspection would have required introducing a more opinionated tag family.
- `desk/atoms/atom-tractatusir-suggests-value-in-addressable-textual-units-for-retrieval.md` — the retrieval-oriented role was safe, but further topical tightening would have depended on a stronger decision about whether to emphasize query behavior, addressability, or legacy bridge lineage.

## Validation notes

- All 74 top-level atom files still parse with exactly one `topic:*` tag and one approved `role:*` tag.
- No legacy role tags (`principle`, `architecture_decision`, `bridge`, `query_surface`, `mapping`) remain in `desk/atoms/*.md`.
- A `find` check on `desk/atoms/kb/` showed no files modified during this pass.
