---
id: atom-cross-project-messaging-uses-transport-verbs
title: Cross-project messaging uses transport verbs, not inbox nouns
five_wh_one_plus: why
tags:
- system:deskops
- topic:messaging
---

# Cross-project messaging uses transport verbs, not inbox nouns

## Answer

"Put this in the inbox" makes agents write local files: "inbox" names a place, so the affordance is local persistence. "Send a message to X" names origin, destination, and channel, so agents route through the CLI. Cross-project communication must be expressed as `deskops message send ... --to <project>` (with `list`/`read`/`ack` for the receiving side); delivery returns an explicit verification result (sender, target, path, tracked status).
