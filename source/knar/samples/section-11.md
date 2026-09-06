# 11. Tipos concretos de nodo

No necesariamente deben ser clases diferentes.

Preferiblemente son especializaciones configuradas de `ExecutableNode`.

```text
ExecutableNode
│
├── AgentNode
├── ToolNode
├── ProjectorNode
├── AdapterNode
├── WorkflowNode
└── CompositeNode
```

Pero conceptualmente podrían ser simplemente:

```clojure
{:kind :node
 :runtime :llm
 ...}
```

vs.

```clojure
{:kind :node
 :runtime :postgres
 ...}
```

Esto evita una jerarquía de clases innecesaria.

---

