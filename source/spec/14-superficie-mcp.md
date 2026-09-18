# 14 · La superficie MCP

## Qué es

Una cuarta superficie sobre las formas (13), al lado del SHRDLU (06), `graph_ui` (10 §3) y el runtime por socket (12): un servidor MCP por stdio que un agente monta como herramienta. Es la superficie de los agentes. No parsea oraciones: recibe argumentos tipados, los traduce a formas o a lecturas por dirección, y devuelve JSON.

```
agente ──MCP (JSON)──▶ pron.mcp ──formas──▶ evaluación (13) ──▶ respuesta · escrituras · MoveDoc
                              └──lecturas por dirección (12 §4, §5)──▶ JSON
```

Tres reglas la definen:

1. **Cero texto libre en el camino de la escritura.** Ningún tool recibe una oración. Si un agente pudiera mandar `say("…")`, el problema del parseo (06) se mudaría de cuarto. La única entrada de texto libre es la búsqueda rankeada (§3.3), que ordena documentos y nunca escribe.
2. **Toda escritura es una forma.** Un tool de escritura compila sus argumentos a una forma y la evalúa con `session.eval` (12 §2): verificación de verbos (03), prevalidación (11 §7), refresh, `MoveDoc` y `undo`, igual que un gesto de `graph_ui`. No hay una puerta lateral al store; la única excepción declarada es el nivel 3 (§5), que es edición de esquema y no tiene forma (12 §4).
3. **El agente nunca escribe markdown.** Crear un documento es mandar sus campos en JSON; lo renderiza el `__template__` del modelo, por la misma forma `create` que usa cualquier otra superficie.

## 1. Arranque y mundos

```
pron mcp --world NAME=PATH [--world NAME=PATH …] --pythonpath DIR
         [--projection NAME] [--speaker ID] [--audit MODULE:FUNC]
```

Un servidor, varios mundos, y **el mundo es argumento de cada tool**. A diferencia de `pron serve` (12, 11 §8), que abre un store y enlaza los demás en su `store_index`, el servidor MCP abre un `World` independiente por mundo y no escribe nada en ninguno para montarlo. Un mundo sin nombre (`--world PATH`) toma el nombre de su directorio.

`--projection` es la proyección de las sesiones (01; por defecto `all`), `--speaker` el hablante por defecto de los `MoveDoc` (por defecto `mcp`). Cada tool acepta `speaker` para sobrescribirlo: el agente lleva su ejecución en el hablante, como pide 12 §2.

Las sesiones viven en el servidor, una por `(mundo, speaker)`. Una sesión es un diálogo (06): una forma que queda `ambiguo` o pide un dato deja su pendiente ahí, y la respuesta dice cuál es; el agente la resuelve con otra forma más precisa (un `(doc …)` en vez de un `(the …)`), nunca contestando con texto.

El SDK es el oficial de MCP para Python, versión 2.x (`MCPServer`, que en la 1.x se llamaba `FastMCP`). Es una dependencia opcional (`pip install pron[mcp]`, `mcp>=2.2`), importada solo en `pron.mcp`: `import pron` no la carga.

## 2. Direcciones

Toda lectura se nombra con una URI `kb://`. Una URI **literal** resuelve a un solo destino; una **semántica** resuelve a un conjunto. Toda respuesta que trae documentos trae, por cada uno, su dirección literal, para que el agente baje de un conjunto a un documento y siga navegando.

Un conjunto llega **paginado**: a lo sumo 50 documentos (los 10 mejores si es una búsqueda rankeada), con `total` y, si quedaron documentos después de la página, `truncated: true`. La URI no lleva el límite; lo llevan los argumentos `limit` y `offset` de `kb_get` y `kb_find`, y un resource devuelve la primera página.

### 2.1 Plano literal

| URI | resuelve a |
|---|---|
| `kb://{mundo}/{Modelo}` | los documentos del modelo: dirección, id, título |
| `kb://{mundo}/{Modelo}/{doc}` | el payload completo del documento (12 §4) |
| `kb://{mundo}/{Modelo}/{doc}/{campo}` | el valor de un campo |
| `kb://{mundo}/{Modelo}/{doc}/{campo}/{i}` | el ítem `i` de un campo lista |

Un documento de un store enlazado se nombra con su id completo (`kb://{mundo}/A:Modelo/{doc}`, 10 §2.2). Un modelo que no está en la proyección no resuelve (01).

### 2.2 Plano semántico

Un selector empieza con `@` y es siempre **un predicado que el mundo ya declara**: el servidor no inventa semántica, la lee. Un selector que el mundo no declara resuelve a un conjunto vacío, con una línea que lo dice.

| URI | resuelve a |
|---|---|
| `kb://{mundo}/@{valor}` | ver abajo |
| `kb://{mundo}/{Modelo}/@{valor}` | lo mismo, restringido a un modelo (y su familia, `{Modelo+}`) |
| `kb://{mundo}/@family/{familia}` | los documentos de los modelos cuya familia (`__family__`) o semántica de clase (`__semantics__`) la nombra |
| `kb://{mundo}/@{doc}/{relación}` | los vecinos de `doc` por esa relación: `edges_from` |
| `kb://{mundo}/@{doc}/~{relación}` | lo mismo al revés: `edges_to` |
| `kb://{mundo}/@{doc}/{r1}/{r2}/…` | recorrido encadenado, un salto por relación |
| `kb://{mundo}/?{texto}` | búsqueda rankeada (§3.3) |

`@{valor}` se resuelve, en este orden, contra las dos cosas que un mundo declara como valor:

1. un **tag**: los documentos con ese tag semántico (su arista `tagged_as`, 10 §2.3) o con ese valor en su campo `tags`;
2. un **valor de enumeración**: los documentos que tienen ese valor en un campo cuyo tipo lo enumera (`Literal`, `Enum`; 05). Así `@why` o `@how-not` funcionan sobre un campo de las cinco preguntas sin que el servidor sepa qué es una pregunta: es un valor declarado en un modelo.

Si el mismo valor es tag y enumeración, la respuesta trae la unión y dice de dónde salió cada documento.

Los selectores se componen con `&`, que es intersección de direcciones (02): `kb://antonia-cobranza/DomainAtom/@system:laboratorio-chile&@why`.

### 2.3 Estado del mundo

| URI | qué es |
|---|---|
| `kb://{mundo}/_schema` | modelos de la proyección con sus campos (tipo, obligatorio, enum, descripción; `schema()`), y los `RelationTypeDoc` con tipos de origen y destino, cardinalidad, eje y condición |
| `kb://{mundo}/_ledger/recent` | los últimos `MoveDoc`: quién, qué forma, qué leyó, qué escribió, `hash_mundo` antes y después (07) |
| `kb://{mundo}/_store/integrity` | lo que `pron check` diría del store, y los problemas del índice de aristas (`check_edges`, `stale`) |
| `kb://{mundo}/_transitions/{Modelo}/{estado}` | las transiciones legales desde un estado (10 §2.5): destinos, y la condición de cada una |

## 3. Tools de lectura (nivel 0)

Las lecturas no pasan por formas y no dejan `MoveDoc`: son lecturas por dirección (12 §4, §5), acotadas por la proyección.

| tool | hace |
|---|---|
| `worlds_list()` | los mundos del servidor: nombre, raíz, modelos |
| `kb_get(uri, limit?, offset?)` | resuelve cualquier URI de §2; es la misma lectura que el resource de esa URI, para clientes que solo usan tools |
| `kb_find(world, model, where?, text?, limit?, offset?)` | documentos de un modelo por predicados de sldb (`where`, lista, intersección; 02) y, con `text`, ordenados por §3.3 |
| `kb_read(world, id)` | el documento completo por id (`Modelo:doc`) |
| `kb_neighbors(world, id, relation?, direction?)` | las aristas de un documento, con `origin` y condición (10 §2.4) |

### 3.3 Búsqueda rankeada

`?{texto}` y `kb_find(text=…)` ordenan documentos por similitud con el índice del corpus (`pron.corpus`: embeddings si hay puerto, `difflib` si no, y la respuesta dice cuál). Es la única entrada de texto libre: devuelve direcciones con puntaje, no interpreta nada y no escribe en el mundo. Trae los 10 mejores salvo que `limit` diga otra cosa: un corpus entero con puntaje no es algo que un agente pueda leer. El índice vive en `.pron/`, derivado y fuera de git.

## 4. Tools de escritura

Cada tool compila una forma, la evalúa en la sesión de `(mundo, speaker)` y devuelve la `Response` (12 §3) como JSON: `text`, `outcome`, `move_id`, y de `record` las escrituras con `done`. Todas aceptan `dry_run: true`: prevalidan el movimiento entero (11 §7) y no escriben.

### Nivel 1 · contenido

| tool | forma |
|---|---|
| `kb_doc_create(world, model, fields, name?)` | `(create Modelo (as "name") (campo valor) …)` |
| `kb_doc_edit(world, id, ops)` | `(move (change (doc "id") campo valor) (add …) (remove …) (clean …))`, un movimiento con todas las operaciones |
| `kb_doc_forget(world, id)` | `(forget (doc "id"))` |
| `kb_edge_assert(world, source, relation, target)` | `(assert relación (doc "source") (doc "target"))` |
| `kb_edge_expire(world, source, relation, target)` | `(forget (doc "RelationDoc:<relación>--<source>--<target>"))`: negar una arista es dejar de trackear su `RelationDoc` (03); lo que fue queda en el ledger |
| `kb_undo(world)` | `(undo)` |

`ops` es una lista de `{op: set|add|remove|clean, field, value?}`. Los campos de un documento son también sus secciones: un modelo `StructuredNLDoc` pone cada sección en un campo de su plantilla, y se escribe como cualquier otro.

### Nivel 2 · reglas del mundo

Las reglas son documentos: un `RelationTypeDoc` declara un verbo, su `condition` la legalidad de sus aristas, y las transiciones son aristas `transitions_to` entre documentos de estado (10 §2.5). Declararlas y editarlas es escribir esos documentos con las mismas formas, así que dejan `MoveDoc` y se deshacen con `undo`.

| tool | forma |
|---|---|
| `kb_rule_declare(world, name, source_types, target_types, cardinality, direction?, axis?, condition?, description)` | `(create RelationTypeDoc (as "rt-<name>") …)` |
| `kb_rule_edit(world, name, changes, confirm?)` | `(move (change (doc "RelationTypeDoc:rt-<name>") campo valor) …)` |

Antes de evaluar, `kb_rule_edit` **simula el efecto** sobre las aristas existentes de ese tipo: cuáles quedarían con un origen o destino fuera de los tipos nuevos, cuáles violarían la cardinalidad nueva, cuáles dejarían de cumplir la condición nueva. Si alguna se rompe, no escribe y devuelve la lista; con `confirm: true`, escribe igual y la respuesta la trae. Esa simulación es la guarda del nivel 2: editar las reglas está permitido, a ciegas no.

Los tipos de relación son modelos internos (05): no son palabras del léxico ni se nombran desde una oración. Una sesión con nivel 2 los admite como modelos escribibles en sus formas; una sin él los rechaza como `missing`, como a cualquier modelo fuera de la proyección.

### Nivel 3 · modelos

| tool | hace |
|---|---|
| `kb_model_create(world, name, fields, template?, base?, confirm?)` | genera el módulo Python del modelo desde JSON y lo registra en el mundo |
| `kb_model_extend(world, name, add_fields?, remove_fields?, template?, confirm?)` | edita el modelo por su draft: `model_fields_add`, `model_fields_remove`, `model_template_edit`, `model_validate_draft`, `model_promote` (12 §4) |

Es la única escritura por debajo de las formas, porque la edición de esquema no tiene forma (12 §4): no deja `MoveDoc` ni se deshace con `undo`. Por eso tiene un gate explícito: sin `confirm: true`, devuelve lo que haría (el módulo generado, o el draft y su validación) y no toca nada.

`fields` es una lista de `{name, type, description, required?, default?, enum?}`, con los tipos que el esquema de sldb ya describe (`str`, `int`, `float`, `bool`, `list[str]`, `Literal[…]`). El módulo generado es un `StructuredNLDoc` con `__template__` (el dado, o uno con una sección por campo) y vive en un paquete importable desde el `--pythonpath` del servidor; su `model_ref` apunta ahí. El módulo es un derivado de lo que se declaró: se regenera desde la misma declaración.

### Auditoría

`kb_audit(world)` corre lo que `pron check` corre sobre el mundo, más `check_edges`. Si el servidor arrancó con `--audit MODULE:FUNC`, llama además a esa función con la raíz del mundo y devuelve su reporte: así un mundo trae sus propias pruebas (las consultas congeladas de su especificación) sin que pron sepa cuáles son. Una auditoría que evalúa turnos deja sus `MoveDoc`, como cualquier turno.

## 5. La escalera de mutabilidad

| nivel | qué permite | guarda |
|---|---|---|
| 0 | lecturas (§2, §3) | la proyección |
| 1 | contenido: documentos y aristas (§4) | verificación y prevalidación del kernel |
| 2 | reglas: tipos de relación, condiciones, transiciones | lo anterior, más la simulación de efecto |
| 3 | modelos: generación y edición de esquema | lo anterior, más `confirm` explícito |

El nivel se declara **por proyección**, en el campo `mutability` del `ProjectionDoc` (01), porque la proyección ya es lo que una sesión puede nombrar y hacer. Sin el campo, el nivel es 1, que es lo que una proyección permite hoy. Una sesión `read_only` (12 §2) es nivel 0 cualquiera sea su proyección. Un tool de un nivel más alto que el de la sesión responde `error` sin evaluar nada, y dice qué nivel haría falta.

Los niveles se acumulan: la proyección sigue mandando dentro de cada uno. Un nivel 1 no puede crear un documento de un modelo que la proyección no nombra, ni un nivel 2 afirmar una relación que la proyección tiene en modo `read`.

## Invariantes

- Ningún tool recibe una oración; la búsqueda rankeada ordena y nunca escribe.
- Toda escritura de nivel 1 y 2 es una forma evaluada, y deja su `MoveDoc`.
- Montar un mundo no escribe en él.
- Un selector semántico es un predicado declarado en el mundo; lo que el mundo no declara no resuelve.
- Toda respuesta con documentos trae la dirección literal de cada uno.
- Todo conjunto trae su `total` y llega cortado a una página; lo que se cortó lo dice `truncated`.
- El nivel de una sesión sale de su proyección, nunca de un argumento del tool.
