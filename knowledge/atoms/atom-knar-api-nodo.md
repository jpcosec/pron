---
id: atom-knar-api-nodo
title: Una API se expone como un nodo con petición y observación tipadas
five_wh_one_plus: how
tags:
- system:knar
- topic:api_node
- domain:system_architecture
- kind:concept
- impl:pending
provenance: Derivado de source/spec.md, secciones 14. Declaración del spec; no prueba
  de implementación.
---

# Una API se expone como un nodo con petición y observación tipadas

## Answer

Una API puede integrarse mediante un nodo que transforma una petición tipada en una respuesta tipada. El ejemplo weather_api recibe WeatherRequest, entrega WeatherObservation y declara current_weather, dejando el detalle HTTP encapsulado en su runtime.
