---
id: atom-knar-viewmodel-render
title: La proyección al modelo de vista puede separarse del render final
five_wh_one_plus: how
tags:
- system:knar
- topic:rendering
- domain:system_architecture
- kind:software
- impl:pending
provenance: Derivado de source/spec.md, secciones 15. Declaración del spec; no prueba
  de implementación.
---

# La proyección al modelo de vista puede separarse del render final

## Answer

El ejemplo projection.article transforma ArticleKnowledge en ArticleViewModel mediante ClojureScript. AstroRenderer recibe después ese modelo y genera HTML, separando la construcción de la representación de su renderizado final.
