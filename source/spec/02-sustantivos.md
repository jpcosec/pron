# 02 · Sustantivos

## La regla

Una frase nominal es una dirección de sldb más un predicado. pron la arma; sldb la responde. pron nunca carga los documentos para filtrarlos en Python.

## De la frase a la dirección

| pieza de la frase | pieza de la dirección | ejemplo |
|---|---|---|
| el nombre común | el modelo o la familia | "atom" → `st.{Atom+}` |
| el adjetivo, la relativa | un predicado `--where` | "with provenance" → `has(provenance)`; "of pron" → `system = "pron"` |
| el nombre propio | `doc ~ "…"` o el nombre exacto | "the bridges one" → `doc ~ "bridges"` |
| el genitivo | un subfield | "the synopsis of the repl" → `st.{CliCommandDoc}.cmd-pron-repl.synopsis` |
| el ordinal, el índice | un ítem de lista | "the first argument" → `.arguments.0` |
| el hiperónimo | la familia | "the primitives" → `st.{PrimitiveDoc+}` |

Las direcciones y la gramática de predicados son las de sldb y se documentan allá, en `docs/addressability_model.md`. pron no agrega ninguna.

## El determinante decide la cardinalidad

- "the" con sustantivo singular ("the table"): se espera exactamente una dirección. Cero es *missing* (ver 06). Dos o más es *ambiguo*: pron guarda los candidatos y pregunta "¿cuál?".
- "the" con plural, "all", "every" ("the tables"): el conjunto. Cero no es error, es un conjunto vacío, y la salida sigue siendo *único*: la cardinalidad que el determinante permite se cumplió.
- "a", "any": cualquiera; pron toma la primera y lo dice.
- "that", "it", "the previous one", "the same": un referente del diálogo (06), que ya es una dirección.

## Lo que sldb devuelve y pron muestra

sldb devuelve direcciones `st.{Modelo}.doc` o valores; con stores enlazados, `store:st.{Modelo}.doc`, y pron conserva el store como parte de la identidad del objeto (10 §2.2). pron los muestra con su nombre natural: el campo `title` o `summary` del documento si existe, si no el nombre del doc. Nunca inventa un nombre.

## Término, nombre propio, literal

Qué es cada palabra lo decide su posición en la frase, no su forma:

- **término**: una palabra del léxico de la proyección (05): modelo, campo, tag, valor enumerado, verbo, alias. Si una palabra en posición de término no está en el léxico, es *missing*.
- **nombre propio**: lo que ocupa la posición de nombre después de un término: "the atom of X", "the command X", "the surface named X". No tiene que estar en el léxico. Se busca en el mundo con `doc ~ "X"` y, si el modelo tiene `title`, también `title ~ "X"`. Cero resultados es *missing* con cercanos por título.
- **literal**: lo que va entre comillas, después de "to:" o "saying", o después de un verbo de acción que fija un valor. Nunca se busca; se escribe.
- **valor de campo**: "of pron" tras "the atoms" es `system = "pron"` si `pron` es un valor conocido del campo `system` (los valores de campos enumerados y de tags entran al léxico). Si no, es nombre propio.

La forma en español de un término sale de su alias (05). Un modelo sin alias se nombra por su identificador tal cual, `CliCommandDoc`, y pron lo dice así hasta que alguien le dé alias.

## Dos predicados, dos consultas, una intersección

`--where` acepta un predicado. Una frase con dos restricciones produce dos consultas sobre el mismo alcance y pron se queda con las direcciones que aparecen en ambas. Cruza listas de direcciones; no lee payloads. La traza muestra las dos consultas, los dos conteos y el conteo final:

```
find 'st.{Atom+}' --where 'system = "pron"'   → 41
find 'st.{Atom+}' --where 'has(provenance)'   → 260
∩                                              → 38
```

La misma intersección sirve cuando una lista viene de kgdb y otra de sldb: "Ana's reservations for Friday" cruza `edges_to(Ana, booked_by)` con `find st.{Reservation} --where date = …`.

Si sldb incorpora conjunción en `--where`, pron la usa y borra la intersección.

## Invariantes

- Toda frase nominal produce una dirección o un conjunto de direcciones antes de que se aplique cualquier verbo.
- La traza de un sustantivo es la dirección y el predicado exactos que se pidieron a sldb, copiables a la shell.
- Un sustantivo que no está en la proyección no llega a sldb.
