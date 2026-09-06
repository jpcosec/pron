# Knowledge Index and Retrieval

## Purpose

Separate two problems that are currently easy to mix:

1. how the atom corpus is organized
2. how relevant atoms are selected for a specific question

These are related, but they are not the same thing.
A good tree does not automatically produce good retrieval.
A good retrieval algorithm still needs an organized index.

## Core distinction

### Indexational aspect

The indexational aspect is the structured description of the corpus.

It includes things like:

- taxonomic location in a knowledge tree
- stable id
- brief title or 1-sentence description
- `five_wh_one_plus`
- semantic tags
- lightweight content metadata
- provenance and grounding surfaces
- possibly explicit relations later

This part answers questions like:

- where does this atom belong?
- what is it about?
- what kind of claim is it?
- which branch or region should contain it?
- what nearby atoms are likely to be structurally related?

This is the organization layer.

### Algorithmic aspect

The algorithmic aspect is the query-time selection strategy.

It answers a different question:

- given a concrete user question in a concrete context, which atoms should be retrieved, and in what order?

This depends on:

- the question itself
- the dominant question type
- the current task or context
- the desired abstraction level
- whether the user wants definition, rationale, mechanism, provenance, contrast, workflow, or graph trace
- whether the system should favor broad recall or narrow precision

This is the retrieval layer.

## Main thesis

The KB should have both:

- a structured knowledge index
- a contextual retrieval policy

The tree, tags, and naming structure are not enough by themselves.
They support retrieval, but they do not determine the best answer set for every question.

In short:

- the index is the organized graph-like surface of the corpus
- retrieval is the contextual composition of the right atoms from that corpus

After that distinction is clear, the system can reuse familiar IR techniques
for ranking, filtering, and query expansion instead of reinventing them.

## Why the distinction matters

Two atoms can be far apart in the tree and still both be relevant to one question.
Two atoms can be near each other in the tree and still not both be useful.

Examples:

- a metadata-policy question may need atoms about metadata, provenance, and atom purity
- a graph-trace question may need atoms about provenance lineage, graph commands, and the source-sample-atom-composition chain
- a CLI authoring question may need atoms about discovery, creation, validation, and metadata enrichment

So retrieval is not just:

- list a folder
- list a tag cluster
- show immediate neighbors

Retrieval is:

- identify the question shape
- identify the likely relevant branches and types
- rank candidate atoms
- select a useful subset

## Index layer

## Goal

Give the corpus a legible, navigable, and queryable structure.

## Minimum indexing surfaces

Each atom should ideally expose at least:

- `id`
- `location`
- `title`
- `five_wh_one_plus`
- semantic `tags`
- `answer`
- `provenance`
- metadata registry entry

This aligns with `source/spec/ATOM_IDENTIFICATION_AND_LAYOUT.md`.

## What the index should support

The index should support:

- taxonomic browsing
- grouping by branch
- grouping by topic
- grouping by question type
- grouping by system, layer, entity, graph dimension, or cross-domain dimension
- local neighborhood inspection
- stable references for retrieval and composition

## Role of the tree

The tree should express conceptual placement.
It should answer:

- where in the knowledge space does this atom live?

Examples:

- `kb/knowledge_cli/authoring`
- `kb/knowledge_cli/graph/provenance`
- `kb/metadata/policy`

The tree is not merely cosmetic.
It is an index surface that makes browsing and preselection easier.

## Role of tags

Tags remain useful, but they are not the whole index.

Tags are good for:

- faceting
- lightweight grouping
- retrieval hints
- secondary filtering

Tags are not enough for:

- strong conceptual placement
- hierarchy
- explicit dependency or contrast
- full semantic neighborhood

This is consistent with `source/spec/ATOM_CONCEPT_GRAPH.md`.

## Possible future index enrichments

The index may later include:

- explicit parent branch membership
- branch summaries
- explicit relations between atoms
- concept nodes and concept links
- question-type distributions per branch
- retrieval summaries or branch descriptors

These are enhancements, not prerequisites for the distinction in this document.

## Retrieval layer

## Goal

Given a question, retrieve the most useful atoms for that question and context.

## Retrieval is contextual

The relevant set of atoms is not fixed globally.
It varies by question.

The same atom corpus may produce different relevant subsets for:

- a `what` question
- a `why` question
- a `how` question
- a provenance question
- a graph question
- an authoring question
- a migration or governance question

## Query-time retrieval steps

A retrieval flow should generally do some version of the following:

1. parse the incoming question
2. infer dominant question type or intent
3. detect likely topic and system dimensions
4. estimate scope and abstraction level
5. preselect relevant branches of the tree
6. gather candidate atoms from those branches, relations, and related facets
7. rank or filter candidates
8. compose and return a useful subset in a useful order

## Important retrieval dimensions

A retrieval policy may weigh:

- location / branch
- `five_wh_one_plus`
- semantic tags
- provenance or graph relevance
- direct lexical overlap with the question
- branch-specific importance
- diversity across complementary subtopics
- closeness through explicit relations, when available

## Example: metadata question

Question:

- Why should atom metadata live outside atoms?

Likely retrieval priorities:

- metadata-policy atoms
- atom purity atoms
- tagging and provenance convention atoms
- metadata registry atoms

Likely lower priority:

- graph trace atoms
- structural projection atoms

## Example: graph question

Question:

- How do I inspect provenance lineage in the knowledge CLI?

Likely retrieval priorities:

- graph trace atoms
- graph commands atoms
- provenance chain atoms
- graph architecture atoms

Likely lower priority:

- metadata governance atoms

## Example: authoring question

Question:

- How do I create and review a new atom?

Likely retrieval priorities:

- add-atom atoms
- show-atom atoms
- validate atoms
- set-metadata atoms
- authoring standard docs or related atoms

## Consequence

A static tree alone cannot answer these questions well.
The retrieval layer has to make choices based on context.

## Index and retrieval are complementary

The tree and tags are not competitors of retrieval.
They are inputs to retrieval.

A good retrieval algorithm depends on a legible index.
A good index becomes much more useful when retrieval can interpret context.

So the relationship is:

- indexation organizes the corpus
- retrieval selects and composes the right slice of the corpus

## Implications for the `knowledge` CLI

The current CLI already supports a basic retrieval surface:

- `knowledge list atoms`
- `knowledge show atom`
- `knowledge show metadata`
- `knowledge list namespaces`
- `knowledge graph ...`

But this is still mostly a direct inspection surface, not a contextual retrieval surface.

## Current strengths

The current CLI can already support:

- corpus discovery
- direct lookup by id
- metadata inspection
- graph inspection
- validation

## Current limitations

The current CLI is weak at:

- branch-aware browsing
- native filtering by question type or semantic facets
- contextual ranking
- query-driven selection
- multi-atom answer assembly

## Suggested next capabilities

Useful future additions may include:

- `knowledge list atoms --branch ...`
- `knowledge list atoms --tag ...`
- `knowledge list atoms --question ...`
- `knowledge retrieve "<question>"`
- `knowledge retrieve --why ...`
- `knowledge retrieve --context ...`
- branch summaries and branch indexes
- query-time ranking over tree location + tags + question type

The exact commands can vary.
The important point is that retrieval should become an explicit feature, not an accidental side effect of listing files.

## Architectural principle

The system should not assume that folder proximity equals relevance.
It should not assume that tag overlap alone equals relevance either.

Relevance should be computed from a combination of:

- organized index structure
- semantic typing
- question context
- retrieval rules
- eventually graph relations

## Relation to other specs

This document complements:

- `source/spec/ATOM_IDENTIFICATION_AND_LAYOUT.md`
- `source/spec/ATOM_METADATA_DOC.md`
- `source/spec/NAMESPACE_TREE.md`
- `source/spec/ATOM_CONCEPT_GRAPH.md`

`ATOM_IDENTIFICATION_AND_LAYOUT.md` focuses on how a single atom should be structured.
This document focuses on how the corpus should be organized and how relevant subsets should be selected.

## Summary

The KB needs two distinct but connected layers:

1. an index layer that organizes atoms into a meaningful structure
2. a retrieval layer that chooses the right atoms for a given question

The first is taxonomic and descriptive.
The second is contextual and algorithmic.

Both are necessary.
Neither replaces the other.
