# plnr

La capa que va entre una s-expression y un store de documentos, tomada como lo que
MicroPlanner era: **una búsqueda de metas**, no una tabla de casos.

## La idea

- El store dice qué documentos hay, de qué clase, con qué campos y qué aristas. Nada más.
- Las **reglas del mundo** son documentos suyos: `(theorem nombre consequent PATRÓN CUERPO…)`
  o `(theorem nombre antecedent PATRÓN CUERPO…)`. No viven en este paquete, y los nombres de
  ningún mundo aparecen en `src/plnr`.
- Un **goal** se *prueba*: devuelve los bindings que lo satisfacen, uno por cada manera, y
  quien quiera otra respuesta vuelve a tirar del generador. De ahí sale el retroceso.
- Las reglas que en un motor de casos serían código — qué es una transición de estado, qué
  significa "book" — son **teoremas del mundo**, con `use` para decir cuáles probar, como
  THUSE.
- Se busca entero **sobre un overlay**: las lecturas ven lo que el plan dejaría, el store no
  se mueve. Lo que se escribe son escrituras *pendientes*, y commitearlas es de otro.
- Una respuesta del motor es un par: los bindings y el overlay de esa rama (`Step`). Así el
  retroceso es correcto sin *trail* ni rollback: la rama que falla es un overlay que nadie
  vuelve a leer.

## El lenguaje

Metas de control:

| forma | qué hace |
|---|---|
| `(and G …)` | todas, encadenando bindings; falla con la primera que falla |
| `(or G …)` | la primera que sirve, y las demás al retroceder |
| `(not G)` | una solución si G no tiene ninguna; no liga variables |
| `(goal PATRÓN [(use NOMBRE …)])` | prueba PATRÓN: primitivas primero, después los teoremas |
| `(find N VAR G)` | N soluciones de G como lista; N es número, `all`, o `(at-least N)` |
| `(bind VAR FORMA)` | liga VAR a la forma ya evaluada |
| `(succeed)` `(fail)` | las dos constantes |

Primitivas (lo único que lee el mundo):

| forma | qué pregunta |
|---|---|
| `(is DOC MODELO)` | DOC es un documento de MODELO |
| `(where DOC "PREDICADO")` | el predicado es del store, se lo evalúa el store |
| `(field DOC CAMPO VALOR)` | el campo vale eso; corre en las dos direcciones |
| `(edge REL SRC TGT)` | una arista, en cualquier dirección |
| `(compare OP A B)` | `= != > < >= <=`; lo único que no lee nada, porque comparar dos números no es conocimiento de un mundo |

Aserciones (nunca tocan el store, van al overlay):

| forma | qué deja pendiente |
|---|---|
| `(assert-edge REL SRC TGT)` | una arista |
| `(assert-field DOC CAMPO VALOR)` | un campo |
| `(assert-doc MODELO DOC)` | un documento |

## Qué no hace, a propósito

- **No escribe**: devuelve las escrituras pendientes como formas (`Plan.as_forms()`). El
  commit — con la coerción y el roundtrip del store, su ledger y su undo — es de afuera.
- **No interpreta predicados**: `(where …)` se lo pregunta al store. `payload_matches` existe
  solo para poder probar el motor sin store, y es deliberadamente tonto.
- **No tiene gramática, diálogo ni léxico**: entra una forma, sale un plan.

## Uso

```python
from plnr import MemoryWorld, Theorems, read_one, run

world = MemoryWorld({"t12": ("Table", {"capacity": 6, "zone": "terrace"})})
theorems = Theorems().load('(theorem free consequent (free ?t) (goal (is ?t Table)))')

plan = run(read_one("(goal (free ?t))"), world, theorems)
plan.value("?t")        # 't12'
plan.as_forms()         # lo que escribiría, sin escribir nada
```

El mundo de los tests vive en `worlds/restaurant.theorems` (las reglas, con una transición
de estado y un "book" compuestos como teoremas) y `worlds/restaurant.py` (los documentos).

```bash
python -m pytest -q tests     # 107 tests
make check                    # ruff + formato + mypy + tests + largo de archivo
python examples/demo.py       # busca y muestra lo que escribiría, sin escribir
```

El porqué de cada pieza y su equivalencia con MicroPlanner (THCONSE, THANTE, THUSE, THFIND,
el trail que acá no hace falta) están en [`DESIGN.md`](DESIGN.md).

## Estado

Primera versión. Concurrencia, cacheo de lecturas y un committedor contra un store real no
están: el paquete termina en `Plan`.
