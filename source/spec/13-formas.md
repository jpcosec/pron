# 13 · Formas

## Qué es

Una **forma** es un movimiento de pron escrito como s-expression. Es el lenguaje estructurado de pron: lo que se evalúa. El lenguaje natural es una envoltura sobre las formas: la superficie (06) resuelve una oración, con léxico, diálogo y referentes, hasta que cada frase nominal es un conjunto de direcciones, y entonces la escribe como formas y las evalúa. Un runtime que ya sabe qué documentos quiere, un editor que tiene los dos extremos de un arrastre, escribe las formas directamente y no habla.

Las dos entradas terminan en la misma evaluación: permisos de la proyección (01), verificación de verbos (03), verbos de acción del kernel (04), prevalidación del movimiento entero y segunda lectura de `hash_mundo` (11 §5, §7), refresh, `MoveDoc` (07) y `undo`.

```
oración ──superficie (06): léxico, diálogo, referentes──▶ formas ──evaluación──▶ escrituras · MoveDoc
                                                  formas ──evaluación──▶ escrituras · MoveDoc
```

## Sustantivos

| forma | qué nombra |
|---|---|
| `(doc "Modelo:nombre" …)` | documentos por id de exportación (02, 10 §2.2); con store enlazado, `"A:Modelo:nombre"` |
| `(the Modelo cláusula …)` | exactamente un documento; más de uno es `ambiguo` y la respuesta nombra cada candidato como `(doc …)` |
| `(find Modelo cláusula …)` | todos los que calzan, incluso ninguno |

Cláusulas: `(where "<predicado de sldb>")`, un predicado por cláusula y la intersección entre ellas (02); `(named "nombre propio")`, resuelto por `key`, nombre o `doc ~` como un nombre propio (02).

Un modelo fuera de la proyección es `missing` sin consultar sldb, igual que una palabra (01). Un `(doc …)` que no existe es `missing`.

## Movimientos

| forma | equivale a |
|---|---|
| `(show SUST)` | una frase nominal leída |
| `(targets relación SUST [(of Modelo)] [(where "…")])` | "what does X relation?": `edges_from`, filtrado por los predicados |
| `(sources relación SUST [(of Modelo)] [(where "…")])` | "who relation X?": `edges_to` |
| `(assert relación SUJETO OBJETO)` | afirmar un verbo (03) |
| `(create Modelo (campo valor) …)` | `create` (04); los campos obligatorios que falten son `missing` |
| `(change SUST campo valor)`, `(add SUST campo valor)`, `(remove SUST campo [valor])`, `(clean SUST campo)`, `(forget SUST)` | los verbos de acción del kernel (04) |
| `(say alias SUST)` | un alias de acción (05): `(say confirm (doc "Reservation:r"))` |
| `(say alias SUJETO OBJETO)` | un alias de relación |
| `(say alias (slot "$referent:M" SUST) (slot "$object:M" SUST [(alternatives "id" …)]) (campo valor) …)` | un alias `compose` con sus ranuras llenas por dirección y sus literales por campo |
| `(undo)`, `(refresh)`, `(why [SUST])` | los verbos sin objeto del kernel y "why?" (07) |
| `(move FORMA …)` | varias partes, un movimiento y un refresh (06 §Coordinación) |

Valores: cadenas, números, `true`, `false`, `nil`, y listas como `(list v …)`.

Las formas no agregan capacidades: cada una es algo que una oración ya podía decir, con los mismos nombres del mundo (modelos, campos, `RelationTypeDoc`, símbolos de alias). Un alias sigue siendo lo único que da nombres nuevos (05); `say` lo invoca por su `symbol`.

## Qué registra

El `MoveDoc` de una forma evaluada lleva la forma tal como entró en `sentence`. El de una oración lleva la oración en `sentence` y, en `record["forms"]`, las formas a las que se resolvió. Evaluar esas formas sobre el mismo mundo en el mismo estado deja las mismas escrituras y la misma respuesta: la traza de un turno es reproducible también como formas (06 §Invariantes). La pendiente y los referentes son de la superficie: una forma nunca contesta una pendiente, y un `ambiguo` de `(the …)` no abre una.

## Cómo se usa

- En proceso, `session.eval(formas) -> Response` (12 §2).
- Por socket, la operación `eval` con `forms`, y `RemoteSession.eval(formas)`. Un cliente de otro mundo no la tiene: hablarle a otro mundo es por oraciones (12 §6).
- Por CLI, `pron eval '(…)'`.

## Invariantes

- Toda oración que escribe o lee algo se evalúa como formas; no hay una segunda ruta de ejecución.
- Una forma pasa por las mismas verificaciones y permisos que la oración equivalente.
- Toda forma evaluada deja un `MoveDoc`, también las que terminan en `missing`, `ambiguo` o `error`.
