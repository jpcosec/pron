---
id: atom-knar-knowledge-api
title: El acceso a knowledge debe tener una interfaz estable
five_wh_one_plus: how
tags:
- system:knar
- topic:knowledge_api
- domain:retrieval
- kind:concept
- impl:pending
provenance: Derivado de source/spec.md, secciones 6. Declaración del spec; no prueba
  de implementación.
---

# El acceso a knowledge debe tener una interfaz estable

## Answer

El spec propone las operaciones knowledge.query, knowledge.resolve, knowledge.project, knowledge.write y knowledge.validate como API de acceso. El CLI existente puede implementar inicialmente esta capa y servir de puente hacia esa interfaz estable.
