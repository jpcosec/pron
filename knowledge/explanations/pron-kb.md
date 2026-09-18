# La KB de pron

## Question

¿Qué es la KB de pron?

## Answer

Este repo es también un mundo, y no tiene átomos. Su conocimiento sobre sí mismo ya tiene forma: los capítulos de `source/spec/`, trackeados donde viven como `SpecDoc` con sus secciones indexadas por sldb; los `CliCommandDoc` y `SurfaceDoc` generados del código; y las aristas `implements` de cada módulo hacia los capítulos que su docstring cita. Todo eso lo produce `pron docs` y nada se mantiene a mano.

Solo se versiona lo que se escribe: los capítulos, las explicaciones, las anclas, las proyecciones y el ledger. El store (`.sldb/`), los tipos de relación (`sldb/relation_types/`, `knowledge/relations/`) y los documentos generados (`knowledge/surfaces/`, `knowledge/commands/`) son derivados y no están en git: `make world` los reconstruye desde el repo, y `make docs-check` los reconstruye y falla si el README generado no coincide con el versionado.

```bash
make world                                  # sldb stores init + pron init --knowledge + pron docs
pron docs --world . --pythonpath .          # spec, comandos, módulos, implements
pron check --world . --pythonpath .         # lints, incluido que todo módulo cite un capítulo
pron say "what does the module resolve implement?" --world . --pythonpath .
```

Los átomos de v1 se quedan en la rama `v1-code-and-kb`, como material histórico.

## Sources

- CliCommandDoc:cmd-pron-init
- CliCommandDoc:cmd-pron-docs
- CliCommandDoc:cmd-pron-check
- CliCommandDoc:cmd-pron-say
