---
id: atom-knar-especializaciones-como-datos
title: Los tipos de nodo pueden ser especializaciones configuradas
five_wh_one_plus: how
tags:
- system:knar
- topic:node_spec
- domain:system_architecture
- kind:concept
- impl:pending
provenance: Derivado de source/spec.md, secciones 11, 22. Declaración del spec; no
  prueba de implementación.
---

# Los tipos de nodo pueden ser especializaciones configuradas

## Answer

AgentNode, ToolNode, ProjectorNode, AdapterNode, WorkflowNode y CompositeNode no necesitan constituir clases distintas. El spec permite representar sus diferencias mediante configuración de ExecutableNode, como el kind del nodo y el runtime seleccionado.
