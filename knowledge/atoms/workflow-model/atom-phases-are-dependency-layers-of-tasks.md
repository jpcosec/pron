---
id: atom-phases-are-dependency-layers-of-tasks
title: Phases are dependency layers of tasks
five_wh_one_plus: what
tags:
- system:deskops
- topic:tasks
- topic:phases
- topic:dependencies
---

# Phases are dependency layers of tasks

## Answer

Tasks form an execution dependency graph. A phase is one horizontal layer of that graph: tasks whose dependencies are already satisfied and whose execution can proceed in parallel because they do not overlap operationally. A phase has execution meaning, not business meaning; it is the workflow unit above individual tasks and below the whole board.
