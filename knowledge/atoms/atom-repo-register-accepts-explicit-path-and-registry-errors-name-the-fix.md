---
id: atom-repo-register-accepts-explicit-path-and-registry-errors-name-the-fix
title: Repo register accepts explicit --path and registry errors name the fix
five_wh_one_plus: what
tags: []
provenance: null
---

# Repo register accepts explicit --path and registry errors name the fix

## Answer

deskops repo register <name> --path <abs> registers a sibling repository explicitly; registry resolution failures produce an actionable message naming the supported path instead of a bare not-found error, and register never crashes on model-entry shadowing.
