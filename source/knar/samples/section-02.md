## 2. Principio central

```text
Knowledge Graph
     │
     ▼
 Agent/Node Spec
     │
     ▼
Executable Nodes
     │
     ├── LLM
     ├── Tool
     ├── SQL
     ├── API
     ├── Projector
     ├── Workflow
     └── External Runtime
```

El **grafo define qué existe y qué significa**.

El runtime solamente materializa y ejecuta esa definición.

Por tanto:

> **El grafo es semántico. El workflow es derivado.**

Esto lo diferencia de sistemas como n8n, donde el grafo representa principalmente flujo de ejecución.

---

