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

Los **valores** también son léxico cuando el campo los acota: los miembros de un `Literal` o `Enum`, y los valores ya usados de campos como `system` y de `tags`. Por eso "de pron" en "los átomos de pron" es un predicado `system = "pron"` y no un nombre propio (02). Los valores libres de texto no entran al léxico.

## Anchors: la forma en español

Un `AnchorDoc` es un alias: `symbol` es la palabra, `ref` es lo que nombra, `motive` es lo que se muestra al preguntar qué significa. Lo que puede nombrar está acotado a cinco formas de `ref`: un modelo, un campo, un predicado sobre un modelo (`grande → predicate:Mesa:capacidad >= 6`), un tipo de relación, y un verbo de acción con campo y valor fijos (`confirmar → action:cambiar Reserva.estado=confirmada`).

Un alias sí aporta significado a una expresión: "grande" significa algo porque alguien decidió que es capacidad mayor o igual a seis. Lo que no hace es agregar capacidades: todo `ref` apunta a algo que el mundo ya puede hacer sin el alias, con la dirección o el comando completo. Por eso no es la fuente del léxico, sino su forma en español, y por eso se puede listar, revisar y borrar sin que nada deje de ser posible.

Un alias puede nombrar también un **verbo de acción con campo y valor fijos**: `confirmar → action:cambiar estado=confirmada`. Es la única forma en que un mundo agrega verbos sin código, y sigue siendo un alias: el verbo real es "cambiar" y pasa por las mismas verificaciones, incluida la transición (03).

Son la única fuente de la forma en español. El identificador `CliCommandDoc` no se convierte en "comando" por ninguna regla: alguien escribe el alias `comando → model:CliCommandDoc`, con su plural. `pron docs` genera un alias inicial por modelo y por campo a partir del identificador partido en palabras (`cli command doc`), que sirve de calce aproximado hasta que se corrige a mano. Un término sin alias se nombra y se reconoce por su identificador tal cual.

## Proyección

La proyección (01) recorta el léxico: solo entran las palabras cuyas fuentes están en la proyección de la sesión. Verificar que una palabra "está en la proyección" es buscarla en ese léxico recortado, no en el mundo entero.

## Calce aproximado

Cuando una palabra no calza exactamente con el léxico, la superficie busca cercanos por similitud entre la palabra y los motivos del léxico: descripciones de campos, docstrings de modelos, descripciones de `RelationTypeDoc`, motivos de anchors. Los embeddings se calculan offline sobre el léxico, no sobre los documentos, y se recalculan cuando cambia `hash_mundo` (07).

El resultado del calce aproximado sobre el mundo nunca se ejecuta solo. Se ofrece: "no tengo *bridge*, ¿querías *bridges* o *puente*?". La única excepción es contestar una pendiente de elección (06): ahí el conjunto de candidatos es cerrado y ya se mostró, y un calce único contra esos candidatos sí rellena el hueco.

## Invariantes

- Todo lo que el léxico sabe de un mundo se puede reconstruir desde su store: ninguna palabra de un mundo vive en código. Las palabras generales (determinantes, interrogativos, los verbos del kernel, las construcciones por tipo de campo) sí son de pron y valen para todo mundo.
- Un cambio de `hash_mundo` invalida el léxico y sus embeddings; escribir en el ledger no.
- El léxico se puede listar: "¿qué puedo decir?" imprime las palabras de la proyección con su motivo.
