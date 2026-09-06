---
id: atom-knar-orquestador-pequeno
title: El orquestador coordina sin contener conocimiento específico de aplicaciones
five_wh_one_plus: how_not
tags:
- system:knar
- topic:orchestration
- domain:system_architecture
- kind:concept
- impl:pending
provenance: Derivado de source/spec.md, secciones 18. Declaración del spec; no prueba
  de implementación.
---

# El orquestador coordina sin contener conocimiento específico de aplicaciones

## Answer

El orquestador debe mantenerse pequeño y delegar las transformaciones concretas en nodos descritos semánticamente. Su lógica coordina resolución, compatibilidad, ejecución y verificación, sin incorporar el conocimiento particular de cada aplicación.
