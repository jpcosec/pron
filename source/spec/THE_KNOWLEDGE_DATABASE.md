# The Knowledge Database

## Core Principle

**Entities are indexed. Relations are registered.**

This is the fundamental distinction that defines this knowledge system.

---

## What Gets Registered: Relations (ARB)

The primary unit of registration is the **relation**:

```
(A --R→ B)
```

Where:
- **A** and **B** are entity references (indexed by other relations)
- **R** is the relation type with algebraic properties (transitivity, symmetry, etc.)

Example relations:
- `módulo_login --depende_de→ base_de_datos`
- `servicio_api --desplegado_en→ servidor_producción`
- `usuario_juan --es_jefe_de→ equipo_alpha`

## What Gets Indexed: Entities

Entities (objects) are not registered as standalone records. Instead, they are **indexed** by their participation in relations.

An entity exists in the knowledge base when it appears as A or B in at least one relation. Its identity is derived from its position in the relation graph.

```
Entity "servidor_producción" exists because:
  - módulo_login --depende_de→ servidor_producción
  - servicio_api --desplegado_en→ servidor_producción
  - metricas --recopiladas_en→ servidor_producción
```

## The Algebra of Relations

Relations (R) carry algebraic properties that allow inference:

| Property | Meaning | Example |
|----------|---------|---------|
| **Transitivity** | If A→B and B→C, then A→C | depends_on is transitive |
| **Symmetry** | If A→B, then B→A | communicates_with is symmetric |
| **Reflexivity** | A→A always holds | entity_exists |
| **Inverses** | A→B implies B←A | owns / owned_by |

This algebra enables the knowledge base to compile relations into boolean adjacency matrices.

## Validity: Two Gates

Before a relation is registered, it must pass two gates:

### Gate 1: Sense (S_i)

Does the relation make sense in the given context (facet)?

```
S_facet(Tipo(A), Relation, Tipo(B)) → {0, 1}
```

Computed via the facet's adjacency matrix. If 0, the relation is **Unsinnig** (senseless) — rejected before any evidence is checked.

### Gate 2: Truth (V_i)

Does the relation actually hold empirically?

```
V(relation) → {0, 1, unknown}
```

Verified via:
- Executable tests (for code relations)
- Grounded samples (for document relations)
- Source anchors (for provenance relations)

## Facets as Contextual Projections

A **facet** is a contextual lens that projects a subgraph from the full knowledge graph.

Mechanically, a facet is:
1. A set of allowed relation types
2. A set of type constraints per relation
3. A boolean matrix that computes S_i

When you query or insert, you activate one or more facets. The system computes the **intersection** of those facet projections.

```
Query under Facet_A ∩ Facet_B
= All relations valid in both Facet_A AND Facet_B
```

A facet is itself a relation — one that is always true for nodes that belong to it.

## Text as Syntactic Sugar

Text is the human-readable and LLM-readable surface over the relation graph.

- **Text → Relations**: Stochastic extraction (LLM task). Loses information.
- **Relations → Text**: Deterministic generation. Complete.

This asymmetry justifies why we use LLMs only for ingestion (text → graph), never for retrieval (graph operations are purely algebraic).

## Propositions Must Ground Down

High-level propositions must trace a path to low-level propositions (tests, axioms, assumed facts).

```
"Este servicio es confiable"
    ↓ derived_from
"Este servicio tiene 99.9% uptime medido en los últimos 6 meses"
    ↓ grounded_in
SELECT uptime FROM metrics WHERE service = X AND date > ...
```

If a proposition cannot trace to something verifiable, it cannot be registered. No orphan atoms.

## Contradictions Are Stored, Not Resolved Prematurely

When two relations contradict each other:
1. Both are stored
2. Both are marked as colliding
3. Resolution is manual (human decision)

The system detects contradictions. It does not auto-resolve them.

---

## Summary

| Concept | Role |
|---------|------|
| **Entity** | Indexed by participation in relations |
| **Relation (A--R→B)** | The registered unit |
| **Relation Algebra** | Enables inference and matrix compilation |
| **Facet** | Context that projects and constrains |
| **Sense (S_i)** | Gate 1: Is it logically applicable? |
| **Truth (V_i)** | Gate 2: Is it empirically verified? |
| **Text** | Human/LLM interface, syntactic sugar |
| **Contradiction** | Detected and stored, not auto-resolved |
