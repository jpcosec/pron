# pron

Un SHRDLU sobre un mundo que ya existe. Los documentos de sldb son los objetos, los modelos de relación de kgdb son los verbos transitivos, las escrituras de sldb son los verbos de acción. pron convierte oraciones en direcciones, aristas y escrituras, sostiene el diálogo cuando una oración no alcanza, y registra cada movimiento.

El nombre es Mapudungun: el cordel anudado con que se llevaba el registro.

## Estado

`master` es la reescritura. Contiene la especificación y las vistas, y todavía no contiene código.

La v1 completa (evaluador de s-expressions, la KB de 273 átomos, el store, los tests, el desk) está en la rama `v1-code-and-kb` y en el tag `v1-frozen`. Se conserva como referencia y como fuente para migrar los átomos; no se extiende.

## Leer

- [`source/spec/`](source/spec/README.md): la especificación, ocho documentos cortos. Empezar por el índice.
- [`views/spec2viz/`](views/spec2viz/README.md): las vistas de la arquitectura objetivo, generadas desde `specs/*.yml` con `python build.py`.

## Depende de

- [sldb](https://github.com/jpcosec/hum-ecosystem) v1, con el surface de direcciones activo (commit `e7a2c0c` o posterior).
- [kgdb](https://github.com/jpcosec/hum-ecosystem), que todavía debe absorber los modelos de relación y ensamblar `RelationDoc` en su ingest. Ver `source/spec/08-prerequisitos-y-orden.md`.

## Quién lo usa

`kinesis` declara `pron` como dependencia. Hasta que la reimplementación llegue al paso 5 del orden de construcción, kinesis debe apuntar a la rama `v1-code-and-kb`.
