# Atom Metadata Doc

## Purpose

Keep atoms as pure knowledge units.

Move knowledge-about-knowledge into a separate metadata space.

That includes things like:

- project context
- immediate source surface
- source kind
- grounding state
- editorial role
- scope
- migration or legacy lineage

This metadata space is not a second semantic tag layer for the atom itself.
It is an operational surface for facts about the atom: where it came from,
how it was curated, and how grounded it currently is.

## Rule

An atom should contain:

- its knowledge claim
- its question type
- semantic retrieval tags that describe the claim itself

An atom should not carry governance or provenance-status tags as if they were part of the claim.

The atom frontmatter still remains the place for the atom's own identity and
semantic retrieval surface.
The metadata registry is for atom-adjacent operational facts.

## Proposed document kind

`AtomMetadataDoc`

Minimum shape:

```yaml
id: atom-metadata-registry
title: Atom metadata registry
document_kind: atom_metadata_registry
records:
  - atom_id: atom-...
    path: .knowledge/atoms/atom-....md
    provenance_statement: Derived from `...`.
    metadata_tags:
      project:
        - project:...
      source:
        - source:...
      source_kind:
        - source_kind:...
      grounding:
        - grounding:...
      scope:
        - scope:...
      role:
        - role:...
      method:
        - method:...
      legacy:
        - legacy:...
```

`metadata_tags` is the current storage shape, not a claim that atom metadata
must conceptually be modeled as semantic tags forever. What matters is the
separation of concerns.

## Current implementation

Current registry:

- `metadata/atoms/atom-metadata-registry.yaml`

Current atom-side semantic tags remain focused on claim content, such as:

- `system:*`
- `topic:*`
- `layer:*`
- `entity:*`
- `domain:*`
- `graph:*`
- `cross:*`

## Migration rule

When a field mainly answers any of these questions, it belongs in metadata rather than in the atom:

- where did this atom come from?
- in which project was it curated?
- how grounded is it?
- what editorial/governance role does it currently play?

The metadata registry may group some of these facts under namespaced values for
query convenience, but those values still describe the atom as an artifact of
curation rather than the atom's semantic claim.

## Compatibility note

The current `AtomDoc` model still carries frontmatter `provenance`.
That field remains for compatibility and traceability, but the broader governance metadata now lives in the metadata registry.
