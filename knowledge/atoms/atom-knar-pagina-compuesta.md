---
id: atom-knar-pagina-compuesta
title: Una página compleja se compone de proyectores especializados
five_wh_one_plus: how
tags:
- system:knar
- topic:page_composition
- domain:system_architecture
- kind:concept
- impl:pending
provenance: Derivado de source/spec.md, secciones 16. Declaración del spec; no prueba
  de implementación.
---

# Una página compleja se compone de proyectores especializados

## Answer

Una página grande se descompone en proyectores de encabezado, artículo, relaciones, fuentes y navegación. PageComposer reúne sus resultados y AstroRenderer genera HTML, permitiendo comprobar cada pieza por separado.
