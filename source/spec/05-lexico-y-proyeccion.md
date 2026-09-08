# 05 · Léxico y proyección

## De dónde salen las palabras

El léxico no es una tabla de pron. Se deriva del mundo, en este orden:

| palabra | fuente | ejemplo |
|---|---|---|
| nombre común | nombre del modelo y su docstring | `CliCommandDoc` → "comando" |
| hiperónimo | `base_models` y `family` | `PrimitiveDoc` → "primitivo" |
| atributo | nombre y `description` de cada campo | `synopsis` → "sinopsis" |
| categoría | tags y el DAG semántico | `type.knowledge.anchor` → "anchor" |
| verbo transitivo | `RelationTypeDoc.name` y su descripción | `implements` → "implementa" |
| verbo de acción | la tabla del kernel (04) | "cambia", "crea", "olvida" |
| alias | `AnchorDoc` | "repl" → `st.{CliCommandDoc}.cmd-pron-repl` |

Las descripciones obligatorias de los campos son el motivo de cada palabra: lo que se le muestra al humano cuando pregunta "¿qué es sinopsis?" y lo que se embebe para el calce aproximado.

## Anchors

Un `AnchorDoc` es un alias: una palabra que nombra algo que ya existe y que no coincide con ningún nombre de modelo, campo, tag o verbo. Tiene `symbol`, `ref` a la dirección o al verbo que nombra, y `motive`. No declara operaciones, no contiene semántica, no es la fuente del léxico. Si un mundo no necesita alias, no tiene anchors.

## Proyección

La proyección (01) recorta el léxico: solo entran las palabras cuyas fuentes están en la proyección de la sesión. Verificar que una palabra "está en la proyección" es buscarla en ese léxico recortado, no en el mundo entero.

## Calce aproximado

Cuando una palabra no calza exactamente con el léxico, la superficie busca cercanos por similitud entre la palabra y los motivos del léxico: descripciones de campos, docstrings de modelos, descripciones de `RelationTypeDoc`, motivos de anchors. Los embeddings se calculan offline sobre el léxico, no sobre los documentos, y se recalculan cuando cambia `hash_a`.

El resultado del calce aproximado nunca se ejecuta solo. Se ofrece: "no tengo *bridge*, ¿querías *bridges* o *puente*?".

## Invariantes

- Todo lo que el léxico sabe se puede reconstruir desde el store: no hay palabras en código.
- Un cambio de `hash_a` invalida el léxico y sus embeddings.
- El léxico se puede listar: "¿qué puedo decir?" imprime las palabras de la proyección con su motivo.
