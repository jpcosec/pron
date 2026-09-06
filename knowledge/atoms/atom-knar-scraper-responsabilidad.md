---
id: atom-knar-scraper-responsabilidad
title: El scraper de ejemplo adquiere fuentes sin interpretar ni publicar
five_wh_one_plus: what
tags:
- system:knar
- topic:source_acquisition
- domain:source_modeling
- kind:software
- impl:pending
provenance: Derivado de source/spec.md, secciones 4. Declaración del spec; no prueba
  de implementación.
---

# El scraper de ejemplo adquiere fuentes sin interpretar ni publicar

## Answer

Wikipedia Scraper se responsabiliza de obtener la fuente, normalizar su contenido y emitir un documento de fuente. Su SelfDoc excluye interpretar hallazgos, modificar átomos y publicar output, con lectura de source_configs y escritura de raw_sources.
