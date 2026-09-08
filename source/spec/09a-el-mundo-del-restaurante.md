# 09a · El mundo del restaurante, declarado

Los modelos y documentos que sustentan la conversación de 09. Es *una* declaración posible, escrita para que el lector distinga qué está declarado en ese mundo y qué comportamiento pone pron encima. Nada de esto es una exigencia general: otro restaurante podría declarar otros campos, otros verbos y otros alias. Cuando el orden de construcción (08) pida el segundo mundo de prueba, estos archivos son el fixture, montados de cero en un directorio temporal.

Todo lo que sigue es sintaxis real de sldb v1 y de los modelos de relación de kgdb, salvo dos cosas marcadas como prerrequisito: el campo `condition` en `RelationTypeDoc` y `RelationDoc`, y el modelo `ProjectionDoc`, que es de pron y todavía no existe.

## Los modelos de contenido · `restaurante/models.py`

```python
from typing import Literal
from pydantic import Field
from sldb import StructuredNLDoc


class Cliente(StructuredNLDoc):
    """Una persona que reserva. Se identifica por nombre; el teléfono es obligatorio."""
    __family__ = "restaurante"
    __semantics__ = {"type": ["restaurante", "cliente"]}
    __template__ = """---
nombre: ⸢rev•nombre⸥
telefono: ⸢rev•telefono⸥
---

# ⸢render•nombre⸥

## Notas

⸢rev•notas⸥
""".strip()

    nombre: str = Field(description="Nombre y apellido tal como el cliente lo da.")
    telefono: str = Field(description="Teléfono de contacto, con el formato que el cliente use.")
    notas: str = Field(default="", description="Observaciones libres sobre el cliente: alergias, preferencias, incidentes.")


class Mesa(StructuredNLDoc):
    """Una mesa física del local. Su capacidad es fija; la zona es una de dos."""
    __family__ = "restaurante"
    __semantics__ = {"type": ["restaurante", "mesa"]}
    __template__ = """---
numero: ⸢rev•numero⸥
capacidad: ⸢rev•capacidad⸥
zona: ⸢rev•zona⸥
---

# Mesa ⸢render•numero⸥
""".strip()

    numero: int = Field(description="Número de la mesa tal como está en el salón.")
    capacidad: int = Field(description="Cantidad máxima de personas que se sientan cómodas.")
    zona: Literal["terraza", "salon"] = Field(description="Dónde está la mesa: terraza al aire libre o salón interior.")


class Reserva(StructuredNLDoc):
    """Una reserva para una fecha y hora. A quién es y en qué mesa va son relaciones, no campos."""
    __family__ = "restaurante"
    __semantics__ = {"type": ["restaurante", "reserva"]}
    __template__ = """---
fecha: ⸢rev•fecha⸥
hora: ⸢rev•hora⸥
personas: ⸢rev•personas⸥
estado: ⸢rev•estado⸥
---

# Reserva ⸢render•fecha⸥ ⸢render•hora⸥

## Notas

⸢rev•notas⸥
""".strip()

    fecha: str = Field(description="Fecha de la reserva en ISO, AAAA-MM-DD.")
    hora: str = Field(description="Hora de llegada, HH:MM en 24 horas.")
    personas: int = Field(description="Cantidad de personas que vienen.")
    estado: Literal["pendiente", "confirmada", "sentada", "cancelada"] = Field(
        default="pendiente",
        description="En qué punto está la reserva. Cambia solo por las transiciones declaradas entre estados.",
    )
    notas: str = Field(default="", description="Observaciones libres: ocasión, pedidos especiales.")


class Estado(StructuredNLDoc):
    """Un estado posible de una reserva. Existe como documento para que las transiciones sean aristas entre estados."""
    __family__ = "restaurante"
    __semantics__ = {"type": ["restaurante", "estado"]}
    __template__ = """---
machine: ⸢rev•machine⸥
nombre: ⸢rev•nombre⸥
---

# ⸢render•machine⸥ · ⸢render•nombre⸥

⸢rev•descripcion⸥
""".strip()

    machine: str = Field(description="Qué campo de qué modelo gobierna esta máquina, como Modelo.campo; por ejemplo Reserva.estado.")
    nombre: str = Field(description="El valor del campo al que corresponde este documento.")
    descripcion: str = Field(description="Qué significa estar en este estado.")
```

La convención que une `Reserva.estado` con `Estado` es el par `(machine, nombre)`: el valor `confirmada` es el documento de `Estado` con `machine = "Reserva.estado"` y `nombre = "confirmada"`, acá `estado-reserva-confirmada` (10 §2.5).

## Los tipos de relación · documentos de `RelationTypeDoc` (modelo de kgdb)

`relations/types/de.md`

```markdown
---
name: de
direction: directed
cardinality: many_to_one
source_types:
- Reserva
target_types:
- Cliente
condition: ""
---

# de

## Description

A quién pertenece una reserva. Toda reserva es de exactamente un cliente.
```

`relations/types/asignada_a.md`

```markdown
---
name: asignada_a
direction: directed
cardinality: many_to_one
source_types:
- Reserva
target_types:
- Mesa
condition: "capacidad >= {personas}"
---

# asignada_a

## Description

En qué mesa va una reserva. La condición se evalúa sobre la mesa con las personas de la reserva: la mesa tiene que tener capacidad para todos. Es la condición de todas las aristas de este tipo salvo que una instancia la reemplace.
```

`relations/types/pasa_a.md`

```markdown
---
name: pasa_a
direction: directed
cardinality: many_to_many
source_types:
- Estado
target_types:
- Estado
condition: ""
---

# pasa_a

## Description

Transición permitida entre dos estados de una reserva. La condición de cada arista se evalúa sobre la reserva que quiere transicionar.
```

Los tres nombres se registran además como predicados del store, para que los links en prosa compartan vocabulario:

```
sldb predicates add de --axis WHAT
sldb predicates add asignada_a --axis WHERE
sldb predicates add pasa_a --axis WHEN
```

## Las transiciones · documentos de `RelationDoc`

`relations/pasa_a--pendiente--confirmada.md`

```markdown
---
source_id: Estado:estado-reserva-pendiente
target_id: Estado:estado-reserva-confirmada
relation_type: pasa_a
condition: "personas <= 8"
---

# pendiente pasa_a confirmada

## Notes

Grupos de más de 8 los confirma el encargado a mano.
```

Y sin condición, con el mismo formato: `pasa_a--pendiente--cancelada`, `pasa_a--confirmada--sentada`, `pasa_a--confirmada--cancelada`.

## Los documentos iniciales

Cuatro `Estado` con `machine: Reserva.estado`: `estado-reserva-pendiente`, `estado-reserva-confirmada`, `estado-reserva-sentada`, `estado-reserva-cancelada`. Cinco `Mesa`:

| documento | numero | capacidad | zona |
|---|---|---|---|
| `mesa-3` | 3 | 4 | salon |
| `mesa-5` | 5 | 4 | salon |
| `mesa-12` | 12 | 6 | terraza |
| `mesa-14` | 14 | 8 | terraza |
| `mesa-20` | 20 | 2 | terraza |

Dos `Cliente`: `cliente-ana-perez`, `cliente-luis-soto`. Una `Reserva` previa de Luis Soto para el 2026-09-11, `reserva-2026-09-11-luis-soto`, con sus dos `RelationDoc` `de` y `asignada_a` hacia `mesa-3`.

## El store

```
sldb stores init --path ~/mundos/restaurante
sldb models add restaurante.models:Cliente  --store .sldb --pythonpath .
sldb models add restaurante.models:Mesa     --store .sldb --pythonpath .
sldb models add restaurante.models:Reserva  --store .sldb --pythonpath .
sldb models add restaurante.models:Estado   --store .sldb --pythonpath .
sldb models add kgdb.models:RelationTypeDoc --store .sldb
sldb models add kgdb.models:RelationDoc     --store .sldb
sldb models add pron.models:AnchorDoc       --store .sldb
sldb models add pron.models:ProjectionDoc   --store .sldb
sldb models add pron.models:MoveDoc         --store .sldb
```

Los modelos de kgdb y de pron son de esos paquetes; el restaurante solo los registra.

## La proyección · `ProjectionDoc` (modelo de pron)

`proyecciones/todo.md`

```yaml
name: todo
stores: [local]
models: [Cliente, Mesa, Reserva, Estado]
relations:
  - {name: de, mode: leer y afirmar}
  - {name: asignada_a, mode: leer y afirmar}
  - {name: pasa_a, mode: leer}
actions: [crear, cambiar, agregar, limpiar, quitar, olvidar, refrescar, deshacer]
matching: {cercanos: 3, umbral: 0.55}
aliases: [todos]
naming:
  Cliente: "cliente-{nombre}"
  Reserva: "reserva-{fecha}-{de.nombre}"
  RelationDoc: "{relation_type}--{source_id}--{target_id}"
display:
  Cliente: "{nombre}"
  Mesa: "mesa {numero}"
  Reserva: "{fecha} {hora}, {personas} personas, mesa {asignada_a.numero}, {estado}"
key:
  Mesa: numero
```

`pasa_a` está en modo `leer`: nadie declara transiciones nuevas por oración en esta sesión. `{de.nombre}` y `{asignada_a.numero}` en las plantillas siguen una arista y leen un campo del destino; sin arista, la plantilla deja el hueco vacío.

## Los alias · documentos de `AnchorDoc`

| symbol | ref | motive |
|---|---|---|
| cliente, clientes | `model:Cliente` | una persona que reserva |
| mesa, mesas | `model:Mesa` | una mesa del local |
| reserva, reservas | `model:Reserva` | una reserva para una fecha y hora |
| se llama, que se llame | `field:Cliente.nombre` | el nombre del cliente |
| teléfono | `field:Cliente.telefono` | el teléfono de contacto |
| para N, para N personas | `field:Reserva.personas` y `predicate:Mesa:capacidad >= N` | cuántas personas; como adjetivo de mesa, que quepan |
| en la Z, de la Z | `predicate:Mesa:zona = Z` | dónde está la mesa |
| el viernes, a las H | `field:Reserva.fecha`, `field:Reserva.hora` | cuándo; la superficie normaliza fechas relativas |
| reservale, reserva para | `compose` · crear Reserva con `$literales` · afirmar `de` `$creado` → `$referente:Cliente` · afirmar `asignada_a` `$creado` → `$objeto:Mesa` (05) | crear una reserva de alguien y ponerla en una mesa |
| asignale, en la mesa | `relation:asignada_a` | poner una reserva en una mesa |
| tiene, de | `relation:de` leído desde el cliente | las reservas de alguien |
| confirmar, confirmala | `action:cambiar Reserva.estado=confirmada` | pasar la reserva a confirmada |
| cancelar | `action:cambiar Reserva.estado=cancelada` | cancelar la reserva |
| sentar | `action:cambiar Reserva.estado=sentada` | marcar que llegaron |
| cabe | `predicate:Mesa:capacidad >= {personas}` | si la mesa tiene lugar para la reserva |
| grande | `predicate:Mesa:capacidad >= 6` | mesas para seis o más |
| nota, ponle una nota | `field:Reserva.notas` | observaciones de la reserva |

Las formas `ref:` de alias (`model:`, `field:`, `predicate:`, `relation:`, `action:`, `doc:`, `compose`) son las que 05 y 10 describen; cada fila lista además sus `forms`, omitidas acá por espacio; el `AnchorDoc` de v1 solo tenía `model`, `doc`, `edge`, `op`, `fields`, `view`, `expr`, y se reemplaza.

## Lo que este mundo no declara

- Ningún verbo en código. "Confirmar" es un alias sobre "cambiar"; "cabe" es un alias sobre un predicado.
- Ningún campo de referencia entre objetos: la reserva no tiene `cliente` ni `mesa` como campos; son aristas.
- Ninguna regla de negocio fuera de las condiciones de las aristas: la capacidad y el límite de 8 son texto en un `RelationTypeDoc` y en un `RelationDoc`.
