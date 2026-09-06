---
id: atom-knar-proposal-fallo-tras-escritura
title: Una escritura previa al fallo requiere conservar el estado fallido y su provenance
five_wh_one_plus: how
tags:
- system:knar
- topic:completion_test
- domain:code_craft
- kind:concept
- impl:pending
provenance: Derivado de docs/knowledge-native-runtime/technical/README.md y del modelo
  técnico asociado. Propuesta del asistente; no decisión aprobada del spec.
---

# Una escritura previa al fallo requiere conservar el estado fallido y su provenance

## Answer

La propuesta técnica distingue persistir un artefacto de declarar COMPLETED: un completion test posterior puede fallar. En ese caso plantea registrar FAILED y conservar provenance, sin asumir rollback automático de efectos externos; esa política concreta debe revisarse como decisión de implementación.
