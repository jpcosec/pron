---
id: atom-knar-llm-nodo
title: Un nodo LLM transforma input y conocimiento proyectado en output tipado
five_wh_one_plus: how
tags:
- system:knar
- topic:llm_node
- domain:system_architecture
- kind:concept
- impl:pending
provenance: Derivado de source/spec.md, secciones 12. Declaración del spec; no prueba
  de implementación.
---

# Un nodo LLM transforma input y conocimiento proyectado en output tipado

## Answer

La ejecución de un nodo LLM combina una entrada con una proyección de conocimiento y entrega una salida tipada. El ejemplo research.interpreter recibe SourceDocument, consulta ontología y notas de fuentes, y produce KnowledgeAtom[] mediante capacidades de extracción y relación de conceptos.
