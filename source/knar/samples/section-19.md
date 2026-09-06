# 19. Flujo de conocimiento

El patrón fundamental queda:

```text
       ┌────────────────────┐
       │   Knowledge Graph  │
       └─────────┬──────────┘
                 │ project
                 ▼
       ┌────────────────────┐
       │   Executable Node  │
       └─────────┬──────────┘
                 │ execute
                 ▼
       ┌────────────────────┐
       │      Runtime       │
       └─────────┬──────────┘
                 │ output
                 ▼
       ┌────────────────────┐
       │   Typed Artifact   │
       └─────────┬──────────┘
                 │ validate
                 ▼
       ┌────────────────────┐
       │   Knowledge Graph  │
       └────────────────────┘
```

El sistema completo es un loop de transformación del conocimiento.

---

