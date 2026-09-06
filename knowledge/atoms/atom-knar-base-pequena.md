---
id: atom-knar-base-pequena
title: La abstracción base del nodo debe mantenerse pequeña
five_wh_one_plus: how_not
tags:
- system:knar
- topic:node
- domain:system_architecture
- kind:concept
- impl:pending
provenance: Derivado de source/spec.md, secciones 3, 11. Declaración del spec; no
  prueba de implementación.
---

# La abstracción base del nodo debe mantenerse pequeña

## Answer

La clase o protocolo base debe conservar un contrato deliberadamente pequeño. El spec prefiere especializaciones configuradas y evita introducir una jerarquía de clases cuando la diferencia puede expresarse como datos del nodo y selección de runtime.
