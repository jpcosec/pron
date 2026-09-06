---
id: atom-knar-completion-persistencia
title: Un completion test puede exigir que el resultado esté almacenado
five_wh_one_plus: how
tags:
- system:knar
- topic:completion_test
- domain:code_craft
- kind:concept
- impl:pending
provenance: Derivado de source/spec.md, secciones 10. Declaración del spec; no prueba
  de implementación.
---

# Un completion test puede exigir que el resultado esté almacenado

## Answer

Las condiciones de término pueden incluir knowledge.exists(output.document.id), además de existencia del output, schema correcto y campos requeridos. Si el contrato exige almacenamiento, producir un documento válido en memoria no satisface por sí solo esa condición.
