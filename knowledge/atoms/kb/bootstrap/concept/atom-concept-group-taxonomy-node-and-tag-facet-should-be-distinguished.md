---
id: atom-concept-group-taxonomy-node-and-tag-facet-should-be-distinguished
title: ConceptGroup, TaxonomyNode, and TagFacet should be distinguished
five_wh_one_plus: why
tags:
  - system:kb
  - layer:graph_concept
  - entity:concept_group
  - entity:taxonomy_node
  - entity:tag_facet
  - topic:concept_graph
  - topic:taxonomy
  - topic:tag_facets
  - domain:knowledge_representation
  - graph:concept
provenance: Derived from `kb/spec/ATOM_CONCEPT_GRAPH.md` and `kb/spec/ATOM_CONCEPT_GRAPH_SCHEMA.md`.

---

# ConceptGroup, TaxonomyNode, and TagFacet should be distinguished

## Answer

ConceptGroup, TaxonomyNode, and TagFacet should be modeled as distinct roles because they organize knowledge in different ways: concept groups collect semantically related regions, taxonomy nodes express placement in a hierarchy, and tag facets support lightweight retrieval and filtering. Collapsing them into one flat tagging scheme hides useful structure and makes future graph evolution harder.
