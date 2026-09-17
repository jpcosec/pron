# pron — especificación

pron es la capa de lenguaje sobre un mundo que ya existe: los documentos de sldb son los objetos, los modelos de relación de kgdb son los verbos transitivos, y las escrituras de sldb son los verbos de acción. Su lenguaje son las formas (13), s-expressions que se evalúan de forma determinista. Sobre las formas hay superficies, y todas están al mismo nivel: la superficie de lenguaje natural (06), el SHRDLU, convierte oraciones en formas y proyecta respuestas en lenguaje; `graph_ui` convierte gestos en formas y proyecta visualizaciones. Ninguna pasa por la otra. pron no resuelve, no filtra, no declara verbos ni guarda estado del mundo. Convierte formas en direcciones, aristas y escrituras, sostiene el diálogo cuando una forma no alcanza, y deja rastro de cada movimiento.

```
sldb | kgdb            documentos, esquema, grafo tipado
API de pron            Kernel, Verbs, verificación, MoveDoc, undo
formas (13)            el lenguaje: s-expressions evaluadas de forma determinista
superficies            SHRDLU (06): oraciones ↔ lenguaje   ·   graph_ui: gestos ↔ visualizaciones
```

La v1 (código, KB, store, tests) vive entera en la rama `v1-code-and-kb` y el tag `v1-frozen`. Esta especificación se escribió después de leer cómo funcionan sldb y kgdb de verdad, y reemplaza a la v1 en vez de extenderla.

## Documentos

| # | documento | contesta |
|---|---|---|
| 01 | [El mundo](01-mundo.md) | qué es un mundo, qué lo declara, qué es una proyección |
| 02 | [Sustantivos](02-sustantivos.md) | cómo una frase nominal se vuelve una dirección de sldb |
| 03 | [Verbos transitivos](03-verbos-transitivos.md) | qué es un verbo, quién lo declara, cómo se lee y cómo se afirma |
| 04 | [Verbos de acción](04-verbos-de-accion.md) | el kernel: las cuatro escrituras y el refresh |
| 05 | [Léxico y proyección](05-lexico-y-proyeccion.md) | de dónde salen las palabras, qué son los anchors, qué hacen los embeddings |
| 06 | [Superficie y diálogo](06-superficie-y-dialogo.md) | la oración, sus tres salidas, la pendiente y los referentes |
| 07 | [Ledger](07-ledger.md) | qué se registra y cómo se contesta "why?" |
| 08 | [Prerrequisitos y orden](08-prerequisitos-y-orden.md) | qué falta en sldb y kgdb, en qué orden se construye, qué lints lo cuidan |
| 09 | [Una conversación, paso a paso](09-una-conversacion.md) | ocho oraciones sobre un mundo externo (reservas de un restaurante): creación, asignación, transición con condición, ambigüedad, missing, "why?" |
| 09a | [El mundo del restaurante, declarado](09a-el-mundo-del-restaurante.md) | los modelos, tipos de relación, transiciones, proyección y alias que sustentan 09; una declaración posible, no una exigencia |
| 10 | [El SHRDLU sobre el modelo](10-el-shrdlu-sobre-el-modelo.md) | cómo los campos se vuelven propiedades por tipo, cómo una relación llega a kgdb en bytes, cómo conviven las dos superficies |
| 11 | [Decisiones de implementación](11-decisiones-de-implementacion.md) | parser, embeddings, fechas, el ingest de kgdb, cambios durante el turno, identidad, fallo parcial: qué decide pron y qué aporta la aplicación |
| 12 | [pron para un runtime externo](12-pron-para-un-runtime.md) | lo que un runtime (kinesis, una superficie como graph_ui, un servidor) puede usar de pron: sesión en proceso o por socket, la respuesta y sus outcomes, documentos por dirección, el mundo, permisos, el socket, qué es estable |
| 13 | [Formas](13-formas.md) | el lenguaje de pron: s-expressions que nombran las palabras del léxico, que la superficie produce desde una oración y que un runtime escribe directo; evaluarlas resuelve, pregunta, escribe y registra |

Si hay que leer uno solo, es el 09: fija con ejemplos cada decisión que los otros enuncian. El 10 y el 11 se leen antes de implementar; el 12 es el único que un runtime externo necesita.

Las vistas spec2viz en [`docs/spec2viz`](../../docs/spec2viz) son la proyección gráfica de estos documentos. Cuando difieran, manda el spec.

## Vocabulario fijo

- **Mundo**: un store de sldb con sus stores enlazados, sus modelos y sus predicados. Se declara en `store_index.yaml`.
- **Sustantivo**: una dirección `st.{Modelo+}.doc.campo.sub` más un predicado `--where`.
- **Verbo transitivo**: un `RelationTypeDoc` de kgdb. Su instancia, un `RelationDoc`, es una arista.
- **Verbo de acción**: una escritura de sldb: crear documento, cambiar campo, agregar a lista, refrescar.
- **Proyección**: la parte del mundo que una sesión puede nombrar.
- **Movimiento**: un turno completo: oración, direcciones, verbo, resultado.

## Reglas que no se negocian

1. pron no abre markdown. Lee y escribe por dirección; sldb es dueño del archivo.
2. pron no tiene cascada de resolución. Un sustantivo lo responde sldb con una dirección y un `--where`.
3. pron no declara verbos. Los declara kgdb; sldb los guarda; el ingest de kgdb los ensambla.
4. pron no escribe en kgdb. kgdb es derivado y de solo lectura; cambia cuando el proyector lo reconstruye.
5. Todo lo que pron sabe **del mundo** está en documentos del store: qué modelos hay, qué palabras los nombran, qué verbos existen, qué permite una proyección. En código está solo lo general: la gramática, la tabla de oraciones por tipo de campo, el kernel. Si un `if` distingue un modelo o un mundo, está en el lugar equivocado.
