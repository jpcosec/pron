# 04 · Verbos de acción

## El kernel

Los verbos de acción cambian el mundo sin relacionar dos cosas. Son exactamente las escrituras de sldb, y el kernel de pron es una tabla que las nombra:

| verbo | operación de sldb | ejemplo de oración |
|---|---|---|
| crear | `docs create --model M -o ruta payload` | "crea un átomo que diga…" |
| cambiar | `fields update docs/<doc>/<campo>[/<sub>] valor` | "cambia la sinopsis del repl a…" |
| agregar | `fields append docs/<doc>/<lista> valor` | "agrégale el tag system:pron" |
| limpiar | `fields clean docs/<doc>/<lista> --dedupe` | "sácale los tags repetidos" |
| quitar campo | `fields remove docs/<doc>/<campo>` | "bórrale la provenance" |
| olvidar | `docs untrack <doc>` | "olvida ese átomo" |
| refrescar | `stores update` + `semantic-export` + `kgdb ingest` | "refresca" |

Afirmar un verbo transitivo (03) es "crear" con modelo `RelationDoc`. Una transición de máquina de estados es solo "cambiar" el campo de estado, permitida porque ya existe una arista `pasa_a` desde el estado actual y su condición se cumple (03); no crea ninguna arista.

## Qué garantiza sldb

Toda escritura por campo re-renderiza el documento desde el payload nuevo, verifica que vuelve a extraerse igual, escribe el archivo, actualiza `hash_c` y `hash_d`, reconstruye el índice semántico y cascadea `hash_a`. Una escritura que rompería el roundtrip se rechaza. pron no agrega validación propia encima; muestra el rechazo de sldb.

## Refresh

Después de cualquier escritura el mundo está desfasado del grafo. El refresh es una sola función del proyector:

1. `sldb stores update` (índices semánticos y de secciones);
2. `sldb stores semantic-export` (nodos, tags, secciones, DAG);
3. `kgdb ingest` sobre ese export **y** sobre los `RelationDoc` del store (aristas autoradas, integridad referencial);
4. registrar el `hash_mundo` nuevo en el snapshot (07).

Cuándo corre depende de la aplicación: síncrono al final de cada verbo de acción en un REPL, o diferido si el mundo lo expande otro agente. Lo que no depende de la aplicación: pron compara el `hash_mundo` del store con el del snapshot antes de leer kgdb y avisa si el grafo está viejo, en vez de servirlo como verdad. El ledger (07) queda fuera de esa huella, así que registrar un movimiento no desfasa nada.

Después de escribir, pron reevalúa las condiciones de las aristas que salen del sujeto (03) y avisa de las que dejaron de cumplirse. No deshace ni decide: "la mesa 12 es para 6 y ahora son 9" es información, y qué hacer con eso es la próxima oración.

Dos verbos de acción coordinados sobre el mismo sujeto ("cámbiala a 9 y ponle una nota") son un movimiento con dos escrituras y un refresh.

Un verbo de acción con sujeto plural escribe una vez por dirección y hace un solo refresh al final. Si una escritura falla, las anteriores quedan hechas: pron informa cuáles se escribieron y cuáles no, y no deshace, porque cada documento es independiente.

## Lo que no es un verbo de acción

- Leer no es acción. Listar, mostrar, contar, comparar son sustantivos con un verbo de lectura implícito y no pasan por el kernel.
- Editar prosa a mano no existe. Si una oración pide un cambio que ningún campo captura, la respuesta es que ese documento no tiene ese campo, con la lista de campos que sí tiene.

## Invariantes

- Cada verbo de acción es una llamada a la librería de sldb, nunca un subproceso al CLI.
- Ningún verbo de acción escribe fuera del store del mundo activo.
- Todo verbo de acción termina con refresh o con un aviso explícito de que el grafo quedó desfasado.
