# Next

## Question

¿Qué sigue?

## Answer

- **Tests bajo las reglas de tamaño.** `make lint` exige al código ≤100 líneas por archivo
  y ≤10 sentencias por función; los tests están exentos y todavía no las cumplen (los
  mundos de prueba y los guiones golden son los más largos).
- **Referentes de una lectura sin ambigüedad.** "what reservations does Ana Pérez have?"
  no deja a Ana Pérez como referente singular; una respuesta elegida en una pendiente sí.
- **kgdb por la CLI de sldb.** pron ya usa `sldb.api`; kgdb todavía llama las clases de la
  CLI de sldb, y por eso `pron init` sigue imprimiendo sus "Registered".
- La superficie pública (el constructor de `Session` y `turn()`) está clavada por spec 12
  y `tests/session/test_12_runtime_surface.py`; no tocarla.

## Sources

- SpecDoc:spec-12
