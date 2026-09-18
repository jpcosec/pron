# 13 · Formas

## Qué es

Una **forma** es una s-expression, y es el lenguaje de pron: todo lo que pron entiende y hace está escrito en formas. Las palabras del léxico nombran formas (05): `(model Table)`, `(relation assigned_to)`, `(where Table "capacity >= 6")`, `(change (it "it" Reservation) status "confirmed")`. La superficie (06) convierte una oración en formas y no hace nada más. Evaluar formas es todo lo demás: resolver sustantivos, contestar, preguntar, verificar, escribir, refrescar y registrar.

```
oración ──superficie (06): solo sintaxis──▶ formas ──evaluación──▶ respuesta · escrituras · MoveDoc
             gesto de graph_ui, runtime ──▶ formas ──evaluación──▶ respuesta · escrituras · MoveDoc
```

Las superficies están al mismo nivel sobre las formas: el SHRDLU (06) proyecta lenguaje; `graph_ui`, que ya sabe qué documentos quiere (tiene los dos extremos de un arrastre), escribe las formas directamente y proyecta visualizaciones; un runtime como kinesis hace lo mismo sin dibujar. Ninguna habla a través de otra. Las dos entradas terminan en la misma evaluación: permisos de la proyección (01), verificación de verbos (03), verbos de acción del kernel (04), prevalidación del movimiento entero y segunda lectura de `hash_mundo` (11 §5, §7), refresh, `MoveDoc` (07) y `undo`.

## Sustantivos

Un sustantivo sin resolver es lo que dijo la oración; evaluarlo lo resuelve contra sldb, kgdb y el diálogo, exactamente como 02 y 06 describen.

| forma | qué nombra |
|---|---|
| `(doc "Modelo:nombre" …)` | documentos por id de exportación (02, 10 §2.2); con store enlazado, `"A:Modelo:nombre"`; no hay nada que resolver; dentro de un movimiento, resuelve también contra los creates pendientes de ese movimiento |
| `(the Modelo cláusula …)` | uno: más de uno es `ambiguo` y abre una pendiente de elección (06) |
| `(a Modelo cláusula …)` | cualquiera: pron toma el primero y lo dice |
| `(all Modelo cláusula …)` | el conjunto, incluso vacío; `find` es lo mismo |
| `(it "palabra" [Modelo])`, `(them "palabra" [Modelo])` | el referente singular o plural del diálogo, de esa clase si se da (06) |
| `(me "palabra")` | la identidad de la sesión (11 §6) |

Cláusulas de `the`, `a` y `all`: `(where "<predicado de sldb>")`, un predicado por cláusula y la intersección entre ellas (02); un predicado que no parsea es error, no una lista vacía, y `""` es un literal válido (02); `(named "nombre propio")`, por `key`, nombre o `doc ~`; `(of SUST)`, un complemento que es otra frase ("the reservations of the client Ana"); `(of-name "palabra" …)`, un complemento que es un nombre ("of Luis Soto"), decidido al resolver como valor de un campo, documento relacionado o nombre propio (02); `(plural)` para "the" con plural; `(asked)` para la frase interrogada ("what reservations"); `(set campo valor)`, un literal que la frase trae para el documento que se va a crear; `(not-a-value Modelo campo "texto")`, un valor que la superficie no encontró entre los del campo, para que la respuesta ofrezca los que hay.

Un modelo, un tipo de relación o un alias fuera de la proyección es `missing` sin consultar sldb (01).

## Movimientos

| forma | equivale a |
|---|---|
| `(show SUST)` | una frase nominal leída |
| `(targets relación [SUST] [(of Modelo)] [(where "…")])` | "what does X relation?": `edges_from`, filtrado por los predicados; sin sustantivo, "I need to know whose." |
| `(sources relación [SUST] [(of Modelo)] [(where "…")])` | "who relation X?": `edges_to` |
| `(assert relación SUJETO OBJETO)` | afirmar un verbo (03) |
| `(create Modelo [(as "nombre")] (campo valor) …)` | `create` (04); un campo obligatorio que falte abre una pendiente de dato (06); `(as …)` da el nombre del documento cuando la proyección no tiene regla de `naming` (01) |
| `(change SUST campo valor)`, `(add SUST campo valor)`, `(remove SUST campo [valor])`, `(clean SUST campo)`, `(forget SUST)` | los verbos de acción del kernel (04) |
| `(say alias SUST)` | un alias de acción (05) |
| `(say alias SUJETO OBJETO)` | un alias de relación |
| `(say alias (slot "$referent:M" SUST) (slot "$object:M" SUST [(alternatives "id" …)]) [(as "nombre")] (campo valor) …)` | un alias compuesto con sus huecos llenos y sus literales por campo |
| `(goal PATRÓN …)` | una meta que el mundo prueba con sus reglas documentadas (03 §Reglas): `(goal (free ?t))`, `(goal (book Ana table-12 reservation-1 2026-09-20 21:00 6))` |
| `(undo)`, `(refresh)`, `(why [SUST])` | los verbos sin objeto del kernel y "why?" (07) |
| `(move FORMA …)` | varias partes, un movimiento y un refresh (06 §Coordinación) |

Un sustantivo solo no es un movimiento: pron responde error y sugiere `(show SUST)`; una cabeza desconocida cercana a una conocida también se sugiere.

**Metas.** Una forma con cabeza `goal` no la resuelve pron: la prueba el mundo, con reglas
que el mundo declara como documentos (03 §Reglas). Dentro de una meta hay combinadores
—`(and G …)`, `(or G …)`, `(not G)`, `(find N VAR G)`, `(bind VAR FORMA)`, `(succeed)`,
`(fail)`— y hojas que son lecturas del mundo: `(is DOC MODELO)`, `(where DOC "predicado")`,
`(field DOC CAMPO VALOR)`, `(edge RELACIÓN SRC TGT)`, `(compare OP A B)`. `(use NOMBRE …)`
dentro de una meta dice con qué reglas probarla, y nada más que con esas.

La búsqueda corre entera sobre un overlay: lee sldb y kgdb y no escribe. Lo que afirma
—`(assert-doc MODELO DOC)`, `(assert-field DOC CAMPO VALOR)`, `(assert-edge RELACIÓN SRC
TGT)`— queda pendiente, y es el mismo kernel (04) el que lo escribe cuando el plan entero
cerró, con el mismo refresh, el mismo `MoveDoc` y el mismo `undo`. Una meta que el mundo no
puede probar es `missing`; una meta mal formada, o una búsqueda que agota su presupuesto, es
`error`. Ni una ni otra escriben nada.

Valores: cadenas, números, `true`, `false`, `nil`, y listas como `(list v …)`.

Las formas no agregan capacidades: cada una usa los nombres del mundo (modelos, campos, `RelationTypeDoc`, símbolos de alias). Un alias sigue siendo lo único que da nombres nuevos, y lo que nombra es a su vez una forma (05).

## Qué registra

Todo movimiento deja en su `MoveDoc`:

- `sentence`: lo que entró, la oración o la forma tal como se escribió;
- `record["forms"]`: la forma que se evaluó, con los sustantivos sin resolver: lo que se dijo;
- `record["resolved"]`: la misma forma con cada sustantivo como las direcciones que resolvió. Evaluarla sobre el mismo mundo en el mismo estado deja las mismas escrituras y la misma respuesta, sin necesitar el diálogo: la traza de un turno es reproducible como formas (06 §Invariantes).

## El diálogo

La pendiente es de la evaluación, no de la superficie: un `(the …)` ambiguo o un `(create …)` al que le falta un campo abren la pendiente de elección o de dato de 06, sea que la forma venga de una oración o de un runtime. La respuesta llena el hueco y la forma se vuelve a evaluar. Evaluar una forma nueva mientras hay una pendiente es una orden nueva: la pendiente se descarta y se registra. Los referentes (`(it …)`, `(them …)`) son los mismos para oraciones y formas de una misma sesión.

## Cómo se usa

- En proceso, `session.eval(formas) -> Response` (12 §2).
- Por socket, la operación `eval` con `forms`, y `RemoteSession.eval(formas)`. Un cliente de otro mundo no la tiene: hablarle a otro mundo es por oraciones (12 §6).
- Por CLI, `pron eval '(…)'`.

## Invariantes

- Toda oración se evalúa como formas; no hay una segunda ruta de ejecución.
- Toda palabra del léxico nombra una forma.
- Una forma pasa por las mismas verificaciones y permisos que la oración equivalente.
- Toda forma evaluada deja un `MoveDoc`, también las que terminan en `missing`, `ambiguo` o `error`.
