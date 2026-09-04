---
id: atom-boolean-algebra-and-bitwise-execution-kernel
title: Boolean Algebra and Bitwise Execution Kernel
five_wh_one_plus: how
tags:
- domain:knowledge_representation
- domain:graph_architecture
provenance: Derived from current project specs during the spec-alignment pass. Exact per-atom source mapping is pending metadata backfill.
---

# Boolean Algebra and Bitwise Execution Kernel

## Answer

Complete propositional logic over s-expressions using boolean semirings ({0,1}, OR, AND). Formulas include RelationAtom (R a b), KernelAtom (kern:name), ConstantFormula, Not, And, Or, If. The bitwise kernel evaluates formulas as integer bit masks via truth tables, enabling parallelized logical inference. Canonicalization and subsumption reduction ensure minimal representations.
