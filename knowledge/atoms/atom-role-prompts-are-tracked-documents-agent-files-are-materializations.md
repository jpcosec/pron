---
# atom-xxx, unique identifier
id: atom-role-prompts-are-tracked-documents-agent-files-are-materializations
# Short, descriptive title
title: Role prompts are tracked documents, agent files are materializations
# what | why | how | how_not | when | where | for_whom
five_wh_one_plus: how_not
# e.g., system:deskops, topic:templates
tags:
- system:deskops
- topic:roles
- topic:drift-control
- topic:materialization
# Optional URL or path to the authoritative source of this knowledge
provenance: docs/agent-system-prompts/
---

# Role prompts are tracked documents, agent files are materializations

## Answer

_Answer the selected 5WH1+ question as one stable knowledge unit._

Workflow role prompts (supervisor, executor, tester) must not be maintained as hand-edited copies in agent config directories such as ~/.pi/agent/agents/. The canonical role definition is an sldb-tracked document under the desk surface; installed agent files are regenerated materializations. Hand copies drift and silently lose content, as happened when the installed deskops-supervisor agent lost the role-lock check, dispatch guidance, evidence expectations, and closeout checklist sections.
