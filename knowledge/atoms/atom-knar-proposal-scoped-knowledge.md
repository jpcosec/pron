---
id: atom-knar-proposal-scoped-knowledge
title: ScopedKnowledge es una propuesta para hacer cumplir el scope
five_wh_one_plus: how
tags:
- system:knar
- topic:permissions
- domain:governance
- kind:concept
- impl:pending
provenance: Derivado de docs/knowledge-native-runtime/technical/README.md y del modelo
  técnico asociado. Propuesta del asistente; no decisión aprobada del spec.
---

# ScopedKnowledge es una propuesta para hacer cumplir el scope

## Answer

El diseño técnico propone un wrapper ScopedKnowledge que autoriza operaciones antes de delegarlas en KnowledgeBackend. Su scope efectivo intersecta permisos del principal, declaración del nodo y proyección solicitada, como mecanismo propuesto para cumplir los límites del spec.
