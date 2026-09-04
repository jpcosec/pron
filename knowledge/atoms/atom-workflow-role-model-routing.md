---
# atom-xxx, unique identifier
id: atom-workflow-role-model-routing
# Short, descriptive title
title: Workflow role model routing
# what | why | how | how_not | when | where | for_whom
five_wh_one_plus: how
# e.g., system:deskops, topic:templates
tags:
- system:deskops
- topic:roles
- topic:model-routing
# Optional URL or path to the authoritative source of this knowledge
provenance: null
---

# Workflow role model routing

## Answer

_Answer the selected 5WH1+ question as one stable knowledge unit._

Each deskops workflow role is bound to an explicit model in its installed agent frontmatter (~/.pi/agent/agents/), not left to inherit the pi default. Supervisor: fireworks/accounts/fireworks/models/kimi-k3 (paid API, routing and review). Executor: openai-codex/gpt-5.4 with fallback google-gemini-cli/gemini-3.1-pro-preview (both on plan; supervisor may override per dispatch with model=). Tester: openrouter/nvidia/nemotron-3-super-120b-a12b:free with fallback openrouter/openai/gpt-oss-20b:free. Rationale: paid kimi only where judgment gates money, plan subscriptions for heavy implementation, free tier for mechanical validation.
