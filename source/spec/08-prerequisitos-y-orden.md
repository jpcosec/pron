# 08 · Prerrequisitos y orden

## Lo que falta fuera de pron

Verificado contra el código el 2026-09-08. Sin esto, pron no puede cumplir el spec.

### kgdb

- ~~Los modelos de relación no están en el paquete.~~ Resuelto 2026-09-09, ver el upgrade abajo. Antes: `RelationTypeDoc` y `RelationDoc` existen como `sldb/docs/relation_models.py`, un fixture de tests de sldb. Van a `kgdb.models` como `StructuredNLDoc`, y kgdb los exporta. Los dos necesitan un campo `condition: str` (predicado `--where`, vacío por defecto): en el tipo vale para todas sus aristas, en la instancia reemplaza al del tipo (03).
- ~~El ensamblado de aristas autoradas no está en el CLI.~~ Resuelto 2026-09-09 con `kgdb ingest --store`. Antes: `kgdb.ingest.assemble_authored_graph` existe y tiene tests, pero `kgdb ingest-sldb` no lo usa y no hay comando que lo corra. El ingest tiene que producir un solo snapshot con los nodos del `semantic-export` y las aristas de los `RelationDoc`, con integridad referencial. Cómo llegan los `RelationDoc` al ingest, dentro del export de sldb o leídos por librería, se decide en kgdb.
- El `KnowledgeNode` arrastra facetas de wiki de código (`ast`, `git`, `test_map`, `compliance`, `adr`). No bloquean; se ignoran.
- ~~kgdb no tipa las relaciones y no admite dos aristas entre el mismo par.~~ Resuelto 2026-09-09: `MultiDiGraph` y tipos por documento. Lo verificado entonces: Verificado el 2026-09-09: una arista es `target_id` más `relation_type`, y `relation_type` es un token de forma libre (`^[A-Za-z][A-Za-z0-9_.:-]*$`) sin registro, sin extremos válidos, sin cardinalidad. El grafo persistido es un `networkx.DiGraph`: dos aristas de distinto tipo entre los mismos dos nodos colapsan en una, gana la última (`schema.edges` del nodo conserva las dos, pero `kgdb edges`, `filter_graph_by_relation` y todo lo que lee la estructura ven una sola). Para pron esto bloquea: `booked_by` y otra relación entre la misma reserva y el mismo cliente, `applies_to_source` y `applies_to_target` de `transitions_to` hacia `State`, y cualquier par de verbos entre dos objetos. El ingest unificado tiene que persistir un `MultiDiGraph` con la arista identificada por `(source, target, relation_type)`, y `edges_from`/`edges_to` tienen que devolver todas. El tipado de la relación sigue viviendo en el `RelationTypeDoc`, que es donde corresponde; kgdb solo garantiza la forma del token.

### sldb

Resuelto el 2026-09-08 (commit `e7a2c0c` en sldb): el surface de direcciones estaba muerto y ahora funciona, las familias `{Base+}` resuelven sin registrar la base, `model <= Base` funciona en `find`, `models add` graba `family` y `base_models`, y el contrato está escrito en `docs/addressability_model.md`.

Pendiente, no bloqueante: toda lectura por dirección carga el store entero antes de seleccionar. Cuando duela, la optimización es interna a sldb. También no bloqueante: `--where` acepta un solo predicado, y pron cruza direcciones de dos consultas (02); una conjunción en sldb lo borraría.

### kgdb: el upgrade · relaciones tipadas por sldb

Decidido el 2026-09-09. kgdb pasa de grafo de tokens a grafo tipado, y el tipo es un documento de sldb:

- `kgdb.models` exporta `RelationTypeDoc` y `RelationDoc` (con `condition`) como `StructuredNLDoc`; un mundo los registra en su store.
- **Ninguna arista sin tipo.** El ingest rechaza toda arista cuyo `relation_type` no tenga un `RelationTypeDoc` trackeado. Las relaciones estructurales que kgdb mismo produce (`has_model`, `has_document`, `has_section`, `tagged_as`, `semantic_parent`, `semantic_equivalent`, `has_field`, `extends`, `applies_to_source`, `applies_to_target`, `names`) se declaran como `RelationTypeDoc` embarcados en el paquete y se registran al inicializar. El grafo queda descrito entero por documentos.
- **Validación en el ensamblado**, por `RelationDoc`: los extremos existen; la clase del origen está en `source_types` y la del destino en `target_types`, con herencia por `base_models`; la cardinalidad se respeta contando; `direction` decide si se materializa la inversa. Es la segunda puerta de RELATION_MODEL_LAYER_SPEC §5: pron previene al autorar, kgdb detecta al ensamblar, y lo que entró por el editor sin pasar por pron se valida igual.
- Cada arista referencia su nodo `sldb://relation_type/<name>` (eje, cardinalidad, condición); `kgdb query` filtra por eje.
- `MultiDiGraph`, arista identificada por `(source, target, relation_type)`.
- kgdb sigue sin autorar: valida y ensambla, y sabe qué es válido leyendo sldb.

**Hecho el 2026-09-09** (kgdb, commit "typed relations"): `kgdb.models` con los dos modelos y `condition`, once tipos estructurales embarcados, `kgdb init --store`, `kgdb ingest --store` con nodos de campo, `extends`, `applies_to_*`, `names`, aristas por `RelationDoc` con `origin`/`condition`/`axis`, exclusión por tag, validación como error, `MultiDiGraph`. Pendiente: los links con predicado en prosa, porque el export de sldb no los lleva. Los ids con prefijo de store enlazado se aceptan como texto pero el export es local; queda para cuando un mundo enlace stores.

### kgdb, además

El `kgdb ingest` unificado que pide 10 §2.3, en un solo comando sobre el `semantic-export`:

- nodos `sldb://document/Modelo:nombre` por documento de contenido, como hoy;
- nodos `sldb://relation_type/<name>` por `RelationTypeDoc`, con aristas `applies_to_source` y `applies_to_target` hacia los nodos modelo que nombran;
- nodos `sldb://field/<M>.<f>` con tipo y descripción y aristas `has_field`; aristas `extends` por `base_models`; nodos `sldb://anchor/<symbol>` con aristas `names` hacia lo que el `ref` nombra (10 §2.3);
- una arista por `RelationDoc`, colgada del origen, con `metadata: {relation_doc, condition, origin: relation_doc}`; el `RelationDoc` no es nodo. Los ids `Modelo:nombre` del documento se mapean a `sldb://document/…`. Hoy `assemble_authored_graph` compara ids desnudos de `serve /graph`; hay que alinearlo con los ids del export;
- una arista por link con predicado en prosa, con `origin: link` y la sección de origen; sldb ya los recupera con `docs recover`, falta que el export los lleve;
- exclusión de los documentos con tag `type.pron.move` (el ledger, 07), o una lista de tags a excluir;
- `hash_mundo` en `metadata` del snapshot;
- integridad referencial como error, no como warning.

### pron mismo

- Ningún modelo de "átomo". Decidido el 2026-09-09: los átomos de v1 se quedan en la rama, como material histórico. El conocimiento de pron sobre sí mismo son los capítulos del spec (`SpecDoc`, trackeados donde viven, con sus secciones indexadas por sldb), los docs de comandos y módulos generados del código, y las aristas `implements` derivadas de los docstrings. sldb es más expresivo que una lista de afirmaciones sueltas, y no hay que aplanarlo.
- El store v1 registra trece modelos de deskops sin documentos. El store nuevo se inicializa de cero.

## Orden de construcción

Cada paso termina con un test que corre contra un store real, no con fixtures fabricados.

**Hecho el 2026-09-09**, los nueve pasos, en `src/pron/` con `tests/test_01…05`: el mundo y la proyección (`world`, `store`, `graph`), el léxico (`lexicon`, `embedder`), los sustantivos (`surface/tokens`, `surface/nouns`, `resolve`), el ledger (`ledger`, `MoveDoc`), los verbos de acción (`kernel`), los transitivos (`verbs`), el diálogo (`dialogue`), la superficie y el REPL (`surface/interpret`, `session`, `cli/repl`), y `pron docs` con los lints (`docs`, `lints`). La conversación de 09 corre entera en `tests/test_04_conversation.py`. La KB de pron son sus capítulos de spec, sus docs generados y las aristas `implements` derivadas de los docstrings.

1. **Mundo y proyección.** Inicializar el store de pron, registrar `SpecDoc`, `CliCommandDoc`, `SurfaceDoc`, `AnchorDoc`, `ProjectionDoc`, `MoveDoc`, y los dos modelos de kgdb. Un `ProjectionDoc` "todo". Test: `sldb stores check` pasa y `st` lista exactamente esos modelos.
2. **Léxico.** Derivar el léxico del store y listarlo. Test: cada palabra listada tiene una fuente en el store y un motivo no vacío.
3. **Sustantivos.** Frase nominal → dirección + predicado → sldb. Las tres salidas. Test: las oraciones del turno de spec2viz producen las direcciones que dicen.
   A partir de aquí los tests corren también contra un segundo mundo, el restaurante de 09, montado desde cero en un directorio temporal: pron tiene que funcionar sobre un mundo que no es el suyo antes de que su propia KB importe.
4. **Ledger.** `MoveDoc` por turno. Test: todo turno de los tests anteriores deja un documento trackeado.
5. **Verbos de acción.** El kernel sobre la librería de sldb, con refresh. Test: cambiar un campo por oración y leerlo por dirección.
6. **Verbos transitivos.** Requiere el `kgdb ingest` unificado (11 §4); hasta entonces, los transitivos leídos responden que el grafo no está disponible y los afirmados escriben el `RelationDoc` igual. Leer aristas, afirmar un `RelationDoc`, refresh, leer la arista nueva. Test: el turno dos de spec2viz.
7. **Diálogo.** Pendiente y referentes. Test: el diagrama de estados de spec2viz, cada transición.
8. **Superficie natural y REPL.** Recién ahora un REPL, y recién ahora un operador LLM.
9. **`pron docs`.** Regenerar `CliCommandDoc` y `SurfaceDoc` desde el código, trackear cada capítulo del spec como `SpecDoc`, y derivar el `implements` de cada módulo hacia los capítulos que su docstring cita.

Nada del paso 8 se empieza antes de que el 3 y el 5 tengan tests verdes.

## Lints

Corren sobre el store de pron y fallan la build:

- todo módulo de pron cita al menos un capítulo del spec en su docstring, y esa cita es una arista `implements`;
- todo comando del CLI tiene su `CliCommandDoc` regenerado sin drift;
- ningún `RelationDoc` huérfano (el ingest de kgdb lo reporta; el lint lo convierte en error);
- ninguna palabra del léxico sin motivo;
- ningún movimiento del ledger sin `hash_mundo` antes y después;
- ninguna referencia a `deskops` en el store de pron.

## Lo que no se construye

- Una cascada de resolución de sustantivos.
- Un filtro de documentos en Python.
- Un formato propio de aristas o un escritor de kgdb.
- Operaciones fijas en un `dispatch`.
- Un léxico en código.
- Un bridge que cargue todos los documentos del store.
