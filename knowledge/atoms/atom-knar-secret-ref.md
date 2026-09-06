---
id: atom-knar-secret-ref
title: La autenticación de una API puede declararse mediante secret_ref
five_wh_one_plus: how
tags:
- system:knar
- topic:authentication
- domain:system_architecture
- kind:concept
- impl:pending
provenance: Derivado de source/spec.md, secciones 14. Declaración del spec; no prueba
  de implementación.
---

# La autenticación de una API puede declararse mediante secret_ref

## Answer

El ejemplo de nodo HTTP declara una estrategia secret_ref y referencia WEATHER_API_KEY. La definición del nodo identifica el secreto requerido mediante una referencia, en lugar de incluir su valor en el spec.
