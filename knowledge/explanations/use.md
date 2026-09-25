# Usar

## Question

¿Cómo lo uso sobre un mundo?

## Answer

Un mundo es un store de sldb. Sobre cualquier store:

```bash
pron init --world . --pythonpath .          # registra los tipos de relación + los modelos de pron
pron refresh --world .                      # índices de sldb, incluido el de aristas
# Derivados, fuera de git: .pron/ (vectores) y .sldb/runtime/ (payloads extraídos, aristas, secciones)
pron lexicon --world . [Model]              # qué se puede decir · los verbos de una clase
pron say "the large tables on the terrace" --world . --trace
pron repl --world . --speaker me
pron serve --world . [--world otro=../otro]  # un store abierto, el de ., con ../otro enlazado como mundo 'otro'; say, repl y los runtimes hablan por .pron/serve.sock
pron serve --world . --mount tercero=../tercero   # agrega un mundo a un daemon corriendo
pron serve --world . --listen 0.0.0.0:8200   # además por TCP, para un cliente en otro contenedor (red privada: no autentica)
pron serve --world . --stop
pron init --world . --template DIR          # un mundo nuevo con las palabras, proyecciones y relaciones de la plantilla
pron check --world .                        # los lints
```

Un turno frío cuesta medio segundo, casi todo imports y la primera carga del store; con `pron serve` corriendo, `pron say` lee en 0,12 s y escribe en medio segundo, y el proceso que pregunta no importa ni sldb: el cliente es `pron.client`, solo biblioteca estándar.

## Sources

- CliCommandDoc:cmd-pron-init
- CliCommandDoc:cmd-pron-refresh
- CliCommandDoc:cmd-pron-lexicon
- CliCommandDoc:cmd-pron-say
- CliCommandDoc:cmd-pron-repl
- CliCommandDoc:cmd-pron-serve
- CliCommandDoc:cmd-pron-docs
- CliCommandDoc:cmd-pron-check
