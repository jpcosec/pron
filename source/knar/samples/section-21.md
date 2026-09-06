# 21. Lenguaje

Recomendación inicial:

```text
Semantic model / orchestration:
    Clojure

Browser / UI projections:
    ClojureScript

Existing knowledge models:
    Python / Pydantic

Web rendering:
    Astro

LLM runtime:
    adapter

External systems:
    adapters
```

No intentaría migrar inmediatamente Pydantic.

Primero:

```text
Markdown
   ↕
Pydantic knowledge layer
   ↕
AgentSpec
   ↕
Clojure runtime
```

Después puedes decidir si el modelo semántico termina moviéndose completamente a EDN/Clojure.

---

