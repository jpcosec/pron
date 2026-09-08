# 08 · Prerrequisitos y orden

## Lo que falta fuera de pron

Verificado contra el código el 2026-09-08. Sin esto, pron no puede cumplir el spec.

### kgdb

- **Los modelos de relación no están en el paquete.** `RelationTypeDoc` y `RelationDoc` existen como `sldb/docs/relation_models.py`, un fixture de tests de sldb. Van a `kgdb.models` como `StructuredNLDoc`, y kgdb los exporta.
- **El ensamblado de aristas autoradas no está en el CLI.** `kgdb.ingest.assemble_authored_graph` existe y tiene tests, pero `kgdb ingest-sldb` no lo usa y no hay comando que lo corra. El ingest tiene que producir un solo snapshot con los nodos del `semantic-export` y las aristas de los `RelationDoc`, con integridad referencial. Cómo llegan los `RelationDoc` al ingest, dentro del export de sldb o leídos por librería, se decide en kgdb.
- El `KnowledgeNode` arrastra facetas de wiki de código (`ast`, `git`, `test_map`, `compliance`, `adr`). No bloquean; se ignoran.

### sldb

Resuelto el 2026-09-08 (commit `e7a2c0c` en sldb): el surface de direcciones estaba muerto y ahora funciona, las familias `{Base+}` resuelven sin registrar la base, `model <= Base` funciona en `find`, `models add` graba `family` y `base_models`, y el contrato está escrito en `docs/addressability_model.md`.

Pendiente, no bloqueante: toda lectura por dirección carga el store entero antes de seleccionar. Cuando duela, la optimización es interna a sldb. También no bloqueante: `--where` acepta un solo predicado, y pron cruza direcciones de dos consultas (02); una conjunción en sldb lo borraría.

### kgdb, además

El `kgdb ingest` unificado que pide 10 §2.3, en un solo comando sobre el `semantic-export`:

- nodos `sldb://document/Modelo:nombre` por documento de contenido, como hoy;
- nodos `sldb://relation_type/<name>` por `RelationTypeDoc`;
- una arista por `RelationDoc`, colgada del origen, con `metadata: {relation_doc, condition, origin: relation_doc}`; el `RelationDoc` no es nodo. Los ids `Modelo:nombre` del documento se mapean a `sldb://document/…`. Hoy `assemble_authored_graph` compara ids desnudos de `serve /graph`; hay que alinearlo con los ids del export;
- una arista por link con predicado en prosa, con `origin: link` y la sección de origen; sldb ya los recupera con `docs recover`, falta que el export los lleve;
- exclusión de los documentos con tag `type.pron.move` (el ledger, 07), o una lista de tags a excluir;
- `hash_mundo` en `metadata` del snapshot;
- integridad referencial como error, no como warning.

### pron mismo

- Un modelo `Atom` propio. Los 273 átomos de v1 están tipados con el `AtomDoc` de deskops; se migran al modelo nuevo desde la rama `v1-code-and-kb` con `sldb extract` y `docs create`.
- El store v1 registra trece modelos de deskops sin documentos. El store nuevo se inicializa de cero.

## Orden de construcción

Cada paso termina con un test que corre contra un store real, no con fixtures fabricados.

1. **Mundo y proyección.** Inicializar el store de pron, registrar `Atom`, `CliCommandDoc`, `SurfaceDoc`, `AnchorDoc`, `ProjectionDoc`, `MoveDoc`, y los dos modelos de kgdb. Migrar los átomos. Un `ProjectionDoc` "todo". Test: `sldb stores check` pasa y `st` lista exactamente esos modelos.
2. **Léxico.** Derivar el léxico del store y listarlo. Test: cada palabra listada tiene una fuente en el store y un motivo no vacío.
3. **Sustantivos.** Frase nominal → dirección + predicado → sldb. Las tres salidas. Test: las oraciones del turno de spec2viz producen las direcciones que dicen.
   A partir de aquí los tests corren también contra un segundo mundo, el restaurante de 09, montado desde cero en un directorio temporal: pron tiene que funcionar sobre un mundo que no es el suyo antes de que su propia KB importe.
4. **Ledger.** `MoveDoc` por turno. Test: todo turno de los tests anteriores deja un documento trackeado.
5. **Verbos de acción.** El kernel sobre la librería de sldb, con refresh. Test: cambiar un campo por oración y leerlo por dirección.
6. **Verbos transitivos.** Requiere kgdb. Leer aristas, afirmar un `RelationDoc`, refresh, leer la arista nueva. Test: el turno dos de spec2viz.
7. **Diálogo.** Pendiente y referentes. Test: el diagrama de estados de spec2viz, cada transición.
8. **Superficie natural y REPL.** Recién ahora un REPL, y recién ahora un operador LLM.
9. **`pron docs`.** Regenerar `CliCommandDoc` y `SurfaceDoc` desde el código, como en v1, y el `implements` de cada átomo `impl:here` hacia su modelo o módulo.

Nada del paso 8 se empieza antes de que el 3 y el 5 tengan tests verdes.

## Lints

Corren sobre el store de pron y fallan la build:

- todo átomo `impl:here` tiene una arista `implements` hacia un `sldb://model/…` o un `SurfaceDoc`;
- todo modelo registrado tiene al menos un átomo que lo menciona;
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
