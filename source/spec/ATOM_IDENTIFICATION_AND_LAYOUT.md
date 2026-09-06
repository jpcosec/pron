# Atom Identification and Layout

## Purpose

Separate the concerns that are currently collapsed into long sentence-style atom ids.

An atom should not use the full claim sentence as its primary identity surface.
Instead, the atom should be organized as:

1. location in the knowledge tree
2. brief 1-sentence description
3. typing
4. content
5. provenance / grounding
6. metadata

This makes atoms easier to name, browse, group, move, and query.

## Problem

The current pattern often makes one long sentence do too much at once:

- identify the atom
- state the claim
- hint at taxonomy
- support retrieval
- enforce uniqueness

That produces ids and filenames that are:

- too long
- awkward to scan
- hard to cluster taxonomically
- fragile when wording changes

In practice, many current atom names are better understood as descriptions than as identifiers.

## Principle

Atom identity should not be the same thing as atom wording.

The system should distinguish:

- where the atom belongs conceptually
- how the atom is briefly described
- how the atom is typed semantically
- what the atom actually says
- how the atom is grounded
- what governance metadata applies to it

## Proposed ordering

### 1. Location

The atom should declare a conceptual location in the knowledge tree.

This answers:

- where does this atom live conceptually?
- which branch of the KB does it belong to?

Examples:

- `kb/knowledge_cli/authoring`
- `kb/knowledge_cli/graph/provenance`
- `kb/metadata/policy`

Location is taxonomic placement, not the full claim.

### 2. Brief 1-sentence description

The atom should have a short human-readable description.

This is the claim label or caption.
It should be concise, stable, and easy to scan.
It should not carry the full burden of taxonomy or uniqueness.

Example:

- `Metadata can be enriched after atom creation`

### 3. Typing

Typing should classify the atom semantically.

Minimum typing surfaces:

- `five_wh_one_plus`
- semantic tags

This answers:

- what kind of question does the atom answer?
- what semantic dimensions does the claim belong to?

Typing is retrieval-oriented and should remain separate from governance metadata.

### 4. Content

The content is the durable knowledge payload.

In the current atom form, this is the answer body.
It should carry the actual claim, explanation, or rule.

### 5. Provenance / grounding

This layer explains where the atom came from and how directly it is supported.

Examples:

- frontmatter `provenance` as a compact trace statement
- grounding state in metadata
- source references in metadata

Provenance and grounding should support auditability without being mistaken for claim semantics.

### 6. Metadata

Metadata contains editorial, governance, migration, and curation information about the atom.

Examples:

- project context
- source surface
- source kind
- grounding state
- editorial role
- scope
- phase
- bootstrap or legacy status

This information belongs in the metadata registry, not in the semantic core of the atom.

## Recommended document shape

The practical shape should be:

- `id`: stable symbolic id
- `location`: taxonomic path
- `title`: brief 1-sentence description
- `five_wh_one_plus`
- `tags`
- `answer`
- `provenance`
- metadata registry entry

## Important distinction: id vs location

`id` and `location` should not be treated as the same thing.

### Stable id

The id should remain stable enough to survive wording changes and moderate taxonomic refactoring.

### Location

The location expresses the atom's current placement in the knowledge tree.
That placement may evolve as the taxonomy improves.

If identity is collapsed into location, every taxonomy refactor becomes an identity migration.
If identity is collapsed into title wording, every wording improvement becomes an identity migration.

For that reason:

- `id` should be stable
- `location` should be movable
- `title` should be editable

## Naming implication

A long filename like:

- `atom-knowledge-set-metadata-should-support-post-creation-enrichment-without-reopening-the-atom-text`

is functioning more as a prose description than as a good identifier.

A cleaner model is:

- location: `knowledge_cli/authoring`
- title: `Metadata can be enriched after atom creation`
- type: `why` + semantic tags
- id: a stable symbolic identifier derived from a controlled naming scheme, not from the full thesis sentence

Possible id styles:

- `knowledge_cli.authoring.post_creation_metadata_enrichment`
- `atom.knowledge_cli.authoring.post_creation_metadata_enrichment`

The exact id syntax can vary, but the important point is that the id should not depend on full prose wording.

## Rule for current atoms

When reviewing or migrating current atoms:

- treat the current long sentence name as the description layer
- do not assume it is the best long-term identifier
- add or infer a taxonomic location
- preserve semantic typing
- keep content intact
- keep provenance traceable
- keep governance metadata outside the atom body

## Migration direction

This document does not require an immediate rewrite of all existing atom ids.

It defines the target model:

- taxonomy first
- short description second
- semantic typing third
- body fourth
- provenance / grounding after that
- metadata last

In implementation terms, the preferred end state is:

- shorter and more stable ids
- explicit `location`
- concise titles
- pure semantic tags in atoms
- governance metadata in the metadata registry

## Relation to existing specs

This proposal is consistent with:

- `source/spec/ATOM_METADATA_DOC.md`
- `source/spec/NAMESPACE_TREE.md`
- `source/spec/atom_quality/ATOM_AUTHORING_STANDARD.md`
- `source/spec/atom_quality/ATOM_TAGGING_AND_PROVENANCE_CONVENTIONS.md`

`ATOM_METADATA_DOC.md` separates claim semantics from governance metadata.
This document adds another separation: atom identity should be separated from full claim wording.
