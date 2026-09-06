---
id: atom-knar-sin-parsing-en-agentes
title: El agente debe delegar el parsing de Markdown a la capa de knowledge
five_wh_one_plus: how_not
tags:
- system:knar
- topic:knowledge_api
- domain:retrieval
- kind:concept
- impl:pending
provenance: Derivado de source/spec.md, secciones 6. Declaración del spec; no prueba
  de implementación.
---

# El agente debe delegar el parsing de Markdown a la capa de knowledge

## Answer

El agente no debería interpretar arbitrariamente el Markdown de la base para obtener su contexto. La capa de acceso debe resolver y proyectar el conocimiento de forma estructurada, manteniendo el parsing fuera de la lógica particular del agente.
