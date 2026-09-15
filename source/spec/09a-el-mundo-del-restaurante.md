# 09a · El mundo del restaurante, declarado

Los modelos y documentos que sustentan la conversación de 09. Es *una* declaración posible, escrita para que el lector distinga qué está declarado en ese mundo y qué comportamiento pone pron encima. Nada de esto es una exigencia general: otro restaurante podría declarar otros campos, otros verbos y otros alias. Cuando el orden de construcción (08) pida el segundo mundo de prueba, estos archivos son el fixture, montados de cero en un directorio temporal.

Todo lo declarado está en inglés, identificadores, descripciones, motivos y formas de alias, por decisión del 2026-09-08 (11 §0): permite modelos de embeddings chicos y una sola tabla de palabras funcionales. El español es una capa de alias que se agrega después, sin tocar los modelos.

Todo lo que sigue es sintaxis real de sldb v1 y de los modelos de relación de kgdb, salvo dos cosas marcadas como prerrequisito: el campo `condition` en `RelationTypeDoc` y `RelationDoc`, y el modelo `ProjectionDoc`, que es de pron y todavía no existe.

## Los modelos de contenido · `restaurant/models.py`

```python
from typing import Literal
from pydantic import Field
from sldb import StructuredNLDoc


class Client(StructuredNLDoc):
    """A person who books. Identified by name; the phone number is mandatory."""
    __family__ = "restaurant"
    __semantics__ = {"type": ["restaurant", "client"]}
    __template__ = """---
name: ⸢rev•name⸥
phone: ⸢rev•phone⸥
---

# ⸢render•name⸥

## Notes

⸢rev•notes⸥
""".strip()

    name: str = Field(description="Full name as the client gives it.")
    phone: str = Field(description="Contact phone number, in whatever format the client uses.")
    notes: str = Field(default="", description="Free-form remarks about the client: allergies, preferences, incidents.")


class Table(StructuredNLDoc):
    """A physical table in the venue. Capacity is fixed; the zone is one of two."""
    __family__ = "restaurant"
    __semantics__ = {"type": ["restaurant", "table"]}
    __template__ = """---
number: ⸢rev•number⸥
capacity: ⸢rev•capacity⸥
zone: ⸢rev•zone⸥
---

# Table ⸢render•number⸥
""".strip()

    number: int = Field(description="Table number as marked on the floor.")
    capacity: int = Field(description="Maximum number of people seated comfortably.")
    zone: Literal["terrace", "indoor"] = Field(description="Where the table is: the open-air terrace or the indoor room.")


class Reservation(StructuredNLDoc):
    """A booking for a date and time. Who it is for and which table it gets are relations, not fields."""
    __family__ = "restaurant"
    __semantics__ = {"type": ["restaurant", "reservation"]}
    __template__ = """---
date: ⸢rev•date⸥
time: ⸢rev•time⸥
party_size: ⸢rev•party_size⸥
status: ⸢rev•status⸥
---

# Reservation ⸢render•date⸥ ⸢render•time⸥

## Notes

⸢rev•notes⸥
""".strip()

    date: str = Field(description="Reservation date in ISO form, YYYY-MM-DD.")
    time: str = Field(description="Arrival time, HH:MM in 24-hour form.")
    party_size: int = Field(description="Number of people coming.")
    status: Literal["pending", "confirmed", "seated", "cancelled"] = Field(
        default="pending",
        description="Where the reservation stands. Changes only through the transitions declared between states.",
    )
    notes: str = Field(default="", description="Free-form remarks: occasion, special requests.")


class State(StructuredNLDoc):
    """One possible state of a status field. Exists as a document so that transitions are edges between states."""
    __family__ = "restaurant"
    __semantics__ = {"type": ["restaurant", "state"]}
    __template__ = """---
machine: ⸢rev•machine⸥
name: ⸢rev•name⸥
---

# ⸢render•machine⸥ · ⸢render•name⸥

⸢rev•description⸥
""".strip()

    machine: str = Field(description="Which field of which model this machine governs, as Model.field; for example Reservation.status.")
    name: str = Field(description="The field value this document stands for.")
    description: str = Field(description="What being in this state means.")
```

La convención que une `Reservation.status` con `State` es el par `(machine, name)`: el valor `confirmed` es el documento de `State` con `machine = "Reservation.status"` y `name = "confirmed"`, acá `state-reservation-confirmed` (10 §2.5).

## Los tipos de relación · documentos de `RelationTypeDoc` (modelo de kgdb)

`relations/types/booked_by.md`

```markdown
---
name: booked_by
direction: directed
cardinality: many_to_one
source_types:
- Reservation
target_types:
- Client
condition: ""
---

# booked_by

## Description

Who a reservation belongs to. Every reservation is booked by exactly one client.
```

`relations/types/assigned_to.md`

```markdown
---
name: assigned_to
direction: directed
cardinality: many_to_one
source_types:
- Reservation
target_types:
- Table
condition: "capacity >= {party_size}"
---

# assigned_to

## Description

Which table a reservation gets. The condition is evaluated on the table with the reservation's party size: the table must seat everyone. It applies to every edge of this type unless an instance overrides it.
```

`relations/types/transitions_to.md`

```markdown
---
name: transitions_to
direction: directed
cardinality: many_to_many
source_types:
- State
target_types:
- State
condition: ""
---

# transitions_to

## Description

An allowed move between two states of a status field. Each edge's condition is evaluated on the object that wants to move.
```

Los tres nombres se registran además como predicados del store, para que los links en prosa compartan vocabulario:

```
sldb predicates add booked_by --axis WHAT
sldb predicates add assigned_to --axis WHERE
sldb predicates add transitions_to --axis WHEN
```

## Las transiciones · documentos de `RelationDoc`

`relations/transitions_to--state-reservation-pending--state-reservation-confirmed.md`

```markdown
---
source_id: State:state-reservation-pending
target_id: State:state-reservation-confirmed
relation_type: transitions_to
condition: "party_size <= 8"
---

# pending transitions_to confirmed

## Notes

Parties larger than 8 are confirmed by the manager by hand.
```

Y sin condición, con el mismo formato: `pending → cancelled`, `confirmed → seated`, `confirmed → cancelled`.

## Los documentos iniciales

Cuatro `State` con `machine: Reservation.status`: `state-reservation-pending`, `state-reservation-confirmed`, `state-reservation-seated`, `state-reservation-cancelled`. Cinco `Table`:

| documento | number | capacity | zone |
|---|---|---|---|
| `table-3` | 3 | 4 | indoor |
| `table-5` | 5 | 4 | indoor |
| `table-12` | 12 | 6 | terrace |
| `table-14` | 14 | 8 | terrace |
| `table-20` | 20 | 2 | terrace |

Dos `Client`: `client-ana-perez`, `client-luis-soto`. Una `Reservation` previa de Luis Soto para el 2026-09-11, `reservation-2026-09-11-luis-soto`, con sus dos `RelationDoc` `booked_by` y `assigned_to` hacia `table-3`.

## El store

```
sldb stores init --path ~/worlds/restaurant
sldb models add restaurant.models:Client      --store .sldb --pythonpath .
sldb models add restaurant.models:Table       --store .sldb --pythonpath .
sldb models add restaurant.models:Reservation --store .sldb --pythonpath .
sldb models add restaurant.models:State       --store .sldb --pythonpath .
sldb models add kgdb.models:RelationTypeDoc   --store .sldb
sldb models add kgdb.models:RelationDoc       --store .sldb
sldb models add pron.models:AnchorDoc         --store .sldb
sldb models add pron.models:ProjectionDoc     --store .sldb
sldb models add pron.models:MoveDoc           --store .sldb
```

Los modelos de kgdb y de pron son de esos paquetes; el restaurante solo los registra.

## La proyección · `ProjectionDoc` (modelo de pron)

`projections/all.md`

```yaml
name: all
stores: [local]
models: [Client, Table, Reservation, State]
relations:
  - {name: booked_by, mode: read and assert}
  - {name: assigned_to, mode: read and assert}
  - {name: transitions_to, mode: read}
actions: [create, change, add, clean, remove, forget, refresh, undo]
aliases: [all]
naming:
  Client: "client-{name}"
  Reservation: "reservation-{date}-{booked_by.name}"
  RelationDoc: "{relation_type}--{source_id}--{target_id}"
display:
  Client: "{name}"
  Table: "table {number}"
  Reservation: "{date} {time}, {party_size} people, table {assigned_to.number}, {status}"
key:
  Table: number
matching: {neighbors: 3, threshold: 0.55}
```

`transitions_to` está en modo `read`: nadie declara transiciones nuevas por oración en esta sesión. `{booked_by.name}` y `{assigned_to.number}` en las plantillas siguen una arista y leen un campo del destino; sin arista, la plantilla deja el hueco vacío.

## Los alias · documentos de `AnchorDoc`

| symbol | forms | ref | motive |
|---|---|---|---|
| client | client, clients | `(model Client)` | a person who books |
| table | table, tables | `(model Table)` | a table in the venue |
| reservation | reservation, reservations, booking, bookings | `(model Reservation)` | a booking for a date and time |
| named | named, called, whose name is | `(field Client name)` | the client's name |
| phone | phone, phone number, number | `(field Client phone)` | the contact phone number |
| for N | for N, for N people, party of N | `(field Reservation party_size)` y `(where Table "capacity >= N")` | how many people; as a table adjective, that they fit |
| on the Z | on the Z, in the Z | `(where Table "zone = Z")` | where the table is |
| on DAY, at TIME | on DAY, this DAY, next DAY, at TIME | `(field Reservation date)`, `(field Reservation time)` | when; the surface normalizes relative dates (11 §3) |
| book | book her, book him, book them, make a reservation for | `(move …)` (abajo) | create a reservation for someone and put it at a table |
| assign | assign, put it at table, seat at | `(relation assigned_to)` | put a reservation at a table |
| has | has, have, of | `(relation booked_by)` leída desde el cliente | someone's reservations |
| confirm | confirm, confirm it | `(change (it "it" Reservation) status "confirmed")` | move the reservation to confirmed |
| cancel | cancel, cancel it | `(change (it "it" Reservation) status "cancelled")` | cancel the reservation |
| seat | seat, seat them, they arrived | `(change (it "it" Reservation) status "seated")` | mark that they arrived |
| fits | fits, fit, fits at | `(where Table "capacity >= {party_size}")` | whether the table has room for the reservation |
| large | large, big | `(where Table "capacity >= 6")` | tables for six or more |
| note | note, add a note, note saying | `(field Reservation notes)` | remarks on the reservation |

El alias compuesto `book`, completo:

```yaml
symbol: book
forms: [book her, book him, book them, make a reservation for]
ref: (move (create Reservation) (assert booked_by (created) (it "her" Client)) (assert assigned_to (created) (a Table)))
motive: create a reservation for someone and put it at a table
```

Los casos de `ref` son los de 05, todos formas (13). El `AnchorDoc` de v1 solo tenía `model`, `doc`, `edge`, `op`, `fields`, `view`, `expr`, y se reemplaza; la sintaxis de texto que usó la primera versión de este documento (`model:Client`, `compose` con `steps`) se sigue leyendo.

## Lo que este mundo no declara

- Ningún verbo en código. "confirm" es un alias sobre "change"; "fits" es un alias sobre un predicado; "book" es una secuencia de tres pasos.
- Ningún campo de referencia entre objetos: la reserva no tiene `client` ni `table` como campos; son aristas.
- Ninguna regla de negocio fuera de las condiciones de las aristas: la capacidad y el límite de 8 son texto en un `RelationTypeDoc` y en un `RelationDoc`.
