# Next

## Question

¿Qué sigue?

## Answer

- **Colapsar el camino dry-run.** `_dry_parts`/`_plan_compose` duplica a `_execute`/`_compose`
  en `session.py`, y esa duplicación ya produjo un bug. Orden seguro: test de caracterización
  que afirme que ambos caminos coinciden sobre un corpus de oraciones, y recién después
  colapsar el par. La superficie pública (el constructor y `turn()`) ya está clavada por
  spec 12 y `tests/test_12_runtime_surface.py`; no tocarla.

## Sources

- SpecDoc:spec-12
