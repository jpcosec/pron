# De dónde sale esto

No es una copia de nada: es el mismo recorte —lo que va entre una s-expression y el store—
escrito desde cero, con la forma de MicroPlanner. La correspondencia, término por término,
es esta; el código de SHRDLU no se leyó para escribir estos archivos, se usó para saber qué
piezas hacían falta.

| MicroPlanner (SHRDLU) | acá | dónde |
|---|---|---|
| base de afirmaciones (`THASSERT`/`THERASE`) | el mundo: documentos y aristas, de solo lectura para la búsqueda | `world.py` (`World`) |
| aserciones de un plan que todavía no se escribió | el overlay, encadenado, uno por rama | `world.py` (`Overlay`) |
| `THGOAL` | `(goal PATRÓN)` | `goals.py`, `primitives.py` |
| `THCONSE` | `(theorem N consequent PATRÓN CUERPO…)` | `theorems.py` |
| `THANTE` | `(theorem N antecedent PATRÓN CUERPO…)` | `assertions.py` (`_fire`) |
| `THAND` `THOR` `THNOT` `THCOND` | `(and …)` `(or …)` `(not …)` | `goals.py` |
| `THPROG` | el cuerpo de un teorema, que es un `and` | `goals.py` (`_apply`) |
| `THUSE` | `(goal PATRÓN (use NOMBRE …))` | `goals.py` (`_use_clause`) |
| `THTBF` | no está: un teorema se elige por cabeza de patrón y por `use`, no por nombre de prueba | — |
| `THFIND` | `(find N VAR G)` | `goals.py` (`_find`) |
| `THV` / `THNV` (variables ligadas y libres) | `?x` como único tipo de variable | `terms.py` |
| el *trail* de la base, y deshacer al retroceder | no hay trail: la rama que falla es un overlay que nadie vuelve a leer | `terms.py` (`Step`), `goals.py` (`_or`, `_apply`, `_find`, `_not`) |
| `TIMID` | `Budget` | `goals.py` |
| el trace de `THGOAL` | `Trace`, un renglón por paso | `goals.py` |
| el diccionario con semántica procedural (`DICTIO`) | no está, a propósito | ver abajo |

## Las tres diferencias

**1. La semántica no es código.** En SHRDLU el sentido de una palabra es un programa Lisp
(`DICTIO`: `PROCEDURE:`, `MARKERS:`, `RESTRICTIONS:`). Acá una regla es *dato*: un
`TheoremDoc` con patrón y cuerpo, legible, listable y borrable. Si el sentido de "book"
fuera una función de este paquete, el conocimiento del mundo volvería al motor, que es
justo lo que este recorte trata de no hacer. Por eso hay un test que falla si `src/plnr`
nombra una palabra de un mundo (`tests/test_rules.py`).

**2. Buscar no es escribir.** La base de MicroPlanner vive en memoria, así que afirmar y
retroceder es barato y simultáneo. Acá el store no tiene transacciones: la búsqueda corre
entera sobre el overlay y **no escribe nada**; lo que devuelve es la lista de escrituras
pendientes (`Plan.as_forms()`), y commitearlas —con la coerción, el roundtrip, el ledger y
el undo del store— queda afuera. Ese es el borde del paquete.

**3. Una respuesta es un par.** Como no hay trail, los bindings no alcanzan para describir
una rama: hace falta también el overlay que esa rama dejó. `Step = (bindings, overlay)`, y
el overlay se pasa de goal en goal en vez de vivir en el motor. Retroceder es tirar del
generador otra vez; la rama anterior no se deshace porque nunca se compartió.

## Qué no está

- Commit de un plan contra un store real (y por lo tanto el roundtrip y el ledger).
- `THTBF` y la elección de teoremas por nombre de prueba: acá se elige por cabeza de patrón
  y por `use` explícito.
- Cacheo de lecturas, concurrencia, y `THFIND` con predicado (el `(find N VAR G)` ya está).
