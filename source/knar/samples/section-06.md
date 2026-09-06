# 6. Knowledge Projection

Un agente no recibe necesariamente toda la base.

Recibe una **proyección del grafo** apropiada para su tarea.

```text
Knowledge Graph
      │
      ├── Agent A Projection
      ├── Agent B Projection
      ├── SQL Projection
      └── UI Projection
```

Ejemplo:

```clojure
{:knowledge
 {:roots [:customers :orders]
  :relations [:belongs-to :references]
  :depth 2
  :permissions [:read]}}
```

El CLI actual de la base de conocimiento puede inicialmente implementar esta capa.

Más adelante debería existir una API estable:

```text
knowledge.query()
knowledge.resolve()
knowledge.project()
knowledge.write()
knowledge.validate()
```

El agente no debería estar haciendo parsing arbitrario de Markdown.

---

