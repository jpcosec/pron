# 9. State Machine

Cada nodo puede tener una máquina de estados explícita.

Ejemplo:

```text
IDLE
 │
 ▼
PREPARING
 │
 ▼
RUNNING
 │
 ├──> RETRYING
 │
 ▼
VALIDATING
 │
 ├──> FAILED
 │
 ▼
COMPLETED
```

Pero el nodo puede extenderla.

Por ejemplo, un scraper:

```text
RESOLVE_SOURCE
      ↓
FETCH
      ↓
PARSE
      ↓
NORMALIZE
      ↓
VALIDATE
      ↓
STORE
```

La máquina de estados también debería ser parte del grafo/spec.

---

