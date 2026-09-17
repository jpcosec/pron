# Next

## Question

¿Qué sigue?

## Answer

- **Colapsar las fases del movimiento.** Las clases de `sexpr/` todavía leen la `Session`
  entera y llaman a sus privados; cada una debe recibir solo lo que usa, y `trace`/`record`
  viajar en un contexto del movimiento. La red de caracterización (`tests/golden/`) clava
  el comportamiento mientras tanto. La superficie pública (el constructor y `turn()`) está
  clavada por spec 12 y `tests/session/test_12_runtime_surface.py`; no tocarla.
- **Tamaño.** `make audit` reporta lo que todavía supera 100 líneas por archivo o 10
  sentencias por función; cuando quede limpio, esas reglas pasan a `make lint`.

## Sources

- SpecDoc:spec-12
