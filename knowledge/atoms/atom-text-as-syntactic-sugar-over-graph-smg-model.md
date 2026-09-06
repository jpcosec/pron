---
id: atom-text-as-syntactic-sugar-over-graph-smg-model
title: Text as Syntactic Sugar over Graph (SMG Model)
five_wh_one_plus: how
tags:
- graph:concept
- domain:knowledge_representation
- kind:concept
- impl:pending
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# Text as Syntactic Sugar over Graph (SMG Model)

## Answer

The SMG (Surface-Meaning-Graph) model decomposes text into three layers: Surface (reversible original text), Meaning (s-expression or boolean matrix), and Graph (inverted index of dimensions). Text-to-graph (S->M->G) is stochastic (LLM proposes), while graph-to-text (G->M->S) is deterministic. This ensures logical validation without losing the original surface form.
