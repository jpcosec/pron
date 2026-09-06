# 4. `SelfDoc`

Cada nodo posee un documento que explica su identidad operacional.

No es una personalidad.

Es una declaración formal de responsabilidad.

```yaml
id: source.scraper.wikipedia

name: Wikipedia Scraper

purpose:
  Extract structured information from Wikipedia pages.

responsibilities:
  - fetch_source
  - normalize_content
  - emit_source_document

does_not:
  - interpret findings
  - modify knowledge atoms
  - publish output

knowledge_scope:
  read:
    - source_configs
  write:
    - raw_sources
```

Esto permite que otro agente u orquestador pueda descubrir qué nodo utilizar sin inspeccionar su código.

---

