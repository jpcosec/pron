# 02 · Sustantivos

## La regla

Una frase nominal es una dirección de sldb más un predicado. pron la arma; sldb la responde. pron nunca carga los documentos para filtrarlos en Python.

## De la frase a la dirección

| pieza de la frase | pieza de la dirección | ejemplo |
|---|---|---|
| el nombre común | el modelo o la familia | "átomo" → `st.{Atom+}` |
| el adjetivo, la relativa | un predicado `--where` | "con provenance" → `has(provenance)`; "de pron" → `system = "pron"` |
| el nombre propio | `doc ~ "…"` o el nombre exacto | "el de bridges" → `doc ~ "bridges"` |
| el genitivo | un subfield | "la sinopsis del repl" → `st.{CliCommandDoc}.cmd-pron-repl.synopsis` |
| el ordinal, el índice | un ítem de lista | "el primer argumento" → `.arguments.0` |
| el hiperónimo | la familia | "los primitivos" → `st.{PrimitiveDoc+}` |

Las direcciones y la gramática de predicados son las de sldb y se documentan allá, en `docs/addressability_model.md`. pron no agrega ninguna.

## El determinante decide la cardinalidad

- "el / la": se espera exactamente una dirección. Cero es *missing* (ver 06). Dos o más es *ambiguo*: pron guarda los candidatos y pregunta "¿cuál?".
- "los / las / todos": el conjunto. Cero no es error, es un conjunto vacío.
- "un / alguno": cualquiera; pron toma la primera y lo dice.
- "ese / la anterior / el mismo": un referente del diálogo (06), que ya es una dirección.

## Lo que sldb devuelve y pron muestra

sldb devuelve direcciones `st.{Modelo}.doc` o valores. pron los muestra con su nombre natural: el campo `title` o `summary` del documento si existe, si no el nombre del doc. Nunca inventa un nombre.

## Un predicado por frase

`--where` acepta un predicado. Una frase con dos adjetivos se traduce a dos consultas encadenadas sobre el mismo alcance, y pron lo dice en la traza. Si sldb incorpora conjunción, pron la usa y borra el encadenado.

## Invariantes

- Toda frase nominal produce una dirección o un conjunto de direcciones antes de que se aplique cualquier verbo.
- La traza de un sustantivo es la dirección y el predicado exactos que se pidieron a sldb, copiables a la shell.
- Un sustantivo que no está en la proyección no llega a sldb.
