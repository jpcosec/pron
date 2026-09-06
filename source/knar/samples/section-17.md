# 17. Composite Nodes

Una aplicación completa puede comportarse como un nodo.

Internamente:

```text
CompositeNode
│
├── Node A
├── Node B
├── Node C
└── Node D
```

Externamente:

```text
Input<X>
   ↓
CompositeNode
   ↓
Output<Y>
```

Esto permite composición recursiva.

Un workflow entero puede convertirse en una pieza de otro workflow.

---

