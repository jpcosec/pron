# 16. Página compleja

Una página grande no debería ser un único nodo.

```text
Knowledge Graph
      │
      ├── HeaderProjector
      ├── ArticleProjector
      ├── RelationGraphProjector
      ├── SourcesProjector
      └── NavigationProjector
               │
               ▼
          PageComposer
               │
               ▼
          AstroRenderer
               │
               ▼
             HTML
```

Esto permite testear cada pieza separadamente.

---

