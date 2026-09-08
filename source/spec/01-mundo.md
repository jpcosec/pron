# 01 · El mundo

## Qué es

Un mundo es un store de sldb. Nada más y nada menos. Lo que un mundo contiene está en su `store_index.yaml`:

- **stores enlazados**: otros stores cuyos documentos entran al mundo con `--global` y cuyas equivalencias de tags entran por `gse.`;
- **modelos registrados**: las clases de objeto del mundo, con `model_ref`, `path` al archivo que las implementa, `family`, `semantics` y `base_models`;
- **predicados**: los nombres de relación con su eje (`HOW`, `WHY`, `WHAT`, `PROVENANCE`, `WHEN_WHERE`) que los links `[pred:: [[x]]]` pueden usar;
- **hash_a**: la huella del mundo entero, que cambia con cualquier escritura.

Un mundo no es de pron. pron opera sobre un mundo que alguien declaró. La KB de pron, la que documenta a pron mismo, es un mundo entre otros, y el REPL de pron corre sobre el mundo que se le indique.

## Modelo = clase, documento = instancia

- `st` lista las clases. `fields show models/X` es el esquema: atributos con tipo y descripción obligatoria.
- `st.{X}.nombre` es una instancia. Su payload es su estado. El markdown es su serialización, reversible.
- `__family__` y `base_models` son la herencia. `{X+}` es la consulta polimórfica y `model <= Base` es `isinstance`.
- `__semantics__` son los tags de clase, heredados por toda instancia; `tags` del documento son de la instancia.
- Los modelos no tienen métodos. El comportamiento por clase no existe en sldb; llega por contrato de kinesis (`ExecutableNode`) cuando corresponda, y no es materia de este spec.

## Los modelos del mundo de pron

El mundo propio de pron declara sus sustantivos:

- `SpecDoc`: cada capítulo de esta especificación, trackeado donde vive; sldb indexa sus secciones, así que "la regla de los determinantes" es una dirección de sección.
- `CliCommandDoc` y `SurfaceDoc`: los comandos y módulos documentados desde el código.
- `AnchorDoc`: alias de léxico (ver 05).
- Y una relación, `implements`, de módulo o comando → capítulo, derivada de las referencias "spec NN" en los docstrings. Es la rama directa del código a lo que debe hacer. No hay un modelo de "átomo": el conocimiento de pron sobre sí mismo ya tiene la forma de su spec y de sus docs, y sldb lo hace direccionable sin aplanarlo a afirmaciones sueltas.

Y registra los modelos de relación de kgdb (`RelationTypeDoc`, `RelationDoc`) para poder autorar verbos. No registra modelos de deskops ni de ningún otro escritorio: deskops es otra instancia sobre el mismo núcleo, y podría ser *un* mundo para pron, nunca la fuente de sus modelos.

## Proyección

Una proyección es la parte de un mundo que una sesión puede nombrar. Se declara como documento del mundo, un `ProjectionDoc`, y se elige al abrir la sesión:

| campo | contenido |
|---|---|
| `stores` | qué stores del mundo entran (el local y cuáles de los enlazados) |
| `models` | qué modelos se pueden nombrar; `{Modelo+}` incluye la familia |
| `relations` | qué tipos de relación, cada uno con modo `read` o `read and assert` |
| `actions` | qué verbos de acción del kernel están permitidos: `create`, `change`, `add`, `clean`, `remove`, `forget`, `refresh`, `undo` |
| `aliases` | qué `AnchorDoc` entran |
| `naming` | cómo se nombra un documento nuevo por modelo, por ejemplo `client-{name}`; sin regla, pron pide el nombre |
| `display` | cómo se muestra un objeto por modelo, por ejemplo `Table: "table {number}"`; sin plantilla, `title` o el nombre del documento |
| `key` | qué campo identifica un objeto por modelo, por ejemplo `Table: number`, para que "table 12" sea `number = 12` |
| `exposed` | si sesiones de **otros mundos** pueden abrir esta proyección: es el léxico de interfaz del mundo (12 §6). Apagado, solo los clientes del mundo propio |

Lo que no está en la proyección no existe para esa sesión: la oración vuelve desde la superficie con "I don't have that word" sin llegar a sldb. Distintos operadores tienen distintas proyecciones: uno que solo lee tiene `actions` vacío y todas sus relaciones en modo `read`. La aplicación puede pedir eso mismo por sesión sin declarar otra proyección: una sesión abierta como **solo lectura** usa la proyección con `actions` vacío y toda relación en modo `read`, y los alias de acción y los compuestos que crean o cambian no entran a su léxico.

## Interfaz entre mundos

Un mundo le habla a otro por su léxico, nunca por su store. El mundo que quiere ser hablado marca una proyección con `exposed: true`: esa es su interfaz, y lo que dice su `pron lexicon` es todo lo que un cliente de otro mundo puede decir. Un cliente de otro mundo abre sesiones solo sobre proyecciones expuestas, y por ellas solo dice oraciones: no lee documentos por dirección, no navega el grafo, no refresca. Dentro de la proyección expuesta rigen las mismas reglas que para cualquier sesión: modelos, relaciones con su modo, acciones. Un mundo sin proyección expuesta es mudo hacia afuera. Montar una interfaz "sobre la marcha" es crear o cambiar un `ProjectionDoc`, una escritura de sldb como cualquier otra (04); no hay que enlazar stores ni copiar documentos.

## Plantilla de un mundo

Un mundo nace sin palabras: sus modelos entran al léxico por su identificador y nada más. Una **plantilla** es un directorio con `anchors/`, `projections/`, `relations/types/` y `relations/`, cada archivo un documento renderizado de `AnchorDoc`, `ProjectionDoc`, `RelationTypeDoc` o `RelationDoc`; `pron init --template DIR` los copia bajo `knowledge/` del mundo nuevo y los trackea (`anchor-<archivo>`, `projection-<archivo>`, `rt-<archivo>`, `<archivo>`), sin tocar los que el mundo ya tenga. Así un runtime que crea muchos mundos de la misma clase les da a todos el mismo vocabulario, la misma interfaz y los mismos verbos desde el primer turno. La plantilla es del runtime; pron solo la aplica.

## Expansión del mundo

Expandir el mundo es registrar un modelo, trackear documentos, declarar un `RelationTypeDoc` o un predicado. Todo eso son escrituras de sldb, y quién las hace y cuándo (síncrono en el turno, o un agente expansor aparte) depende de la aplicación. pron solo exige que después de una expansión corra el refresh (04).

## Invariantes

- El mundo se lee desde `store_index.yaml` y los índices del store, nunca desde un archivo de configuración propio de pron.
- El `hash_mundo` (07) es el token de frescura: una sesión que lo vio cambiar debe recargar léxico y proyección.
- Ningún modelo del mundo de pron vive fuera del repo de pron o de kgdb.
