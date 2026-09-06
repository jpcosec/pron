# 15. Proyectores

Los proyectores convierten conocimiento en representaciones.

```text
Knowledge
   │
   ├──> Markdown
   ├──> HTML
   ├──> JSON
   ├──> Diagram
   ├──> Audio
   └──> Wiki
```

Ejemplo:

```yaml
id: projection.article

runtime:
  type: clojurescript

inputs:
  - ArticleKnowledge

outputs:
  - ArticleViewModel
```

Después:

```text
ArticleViewModel
       ↓
AstroRenderer
       ↓
HTML
```

---

