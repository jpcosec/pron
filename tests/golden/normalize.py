"""The normalizer of the characterization snapshots: only what is genuinely nondeterministic.

- move ids `move-<utc second>-<n>`: the second is the wall clock and <n> counts within that
  second, so both change run to run. Numbered in order of appearance (`<move-1>`, ...), so
  "this move refers to that one" is still pinned.
- sha256 hex digests (`hash_c`, `hash_before`, `hash_after`, `hash_mundo`): these are the
  one exception. They repeat run to run today, but their value is sldb's hashing detail, not
  pron's behavior, and the move to sldb's library API may change it. What pron does with them
  is compare them, so they are numbered in order of appearance: "the world did not change in
  this move" and "this read saw what that write left" stay pinned.
- ISO timestamps with a time part (`at`): the wall clock. One placeholder, because whether
  two moves share a second is timing.
- the test's tmp directory: pytest picks it. Replaced by `<tmp>`; the path under it stays.
  Likewise the checkout of this repo, where pron's own knowledge base imports from: `<repo>`.
"""

from __future__ import annotations

import re
from typing import Any

MOVE_ID = re.compile(r"move-\d{8}T\d{6}-\d{3,}")
HASH = re.compile(r"\b[0-9a-f]{64}\b")
AT = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:[+-]\d{2}:\d{2}|Z)?")


class Normalizer:
    """One per script: the numbering of placeholders runs across all its turns."""

    def __init__(self, *roots: object, repo: object = None):
        paths = {str(r): "<tmp>" for r in roots} | (
            {str(repo): "<repo>"} if repo else {}
        )
        self.roots = sorted(paths.items(), key=lambda kv: len(kv[0]), reverse=True)
        self.seen: dict[str, dict[str, str]] = {"move": {}, "hash": {}}

    def __call__(self, value: Any) -> Any:
        if isinstance(value, dict):
            return {self(k): self(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [self(v) for v in value]
        return self._text(value) if isinstance(value, str) else value

    def _text(self, text: str) -> str:
        for root, label in self.roots:
            text = text.replace(root, label)
        text = MOVE_ID.sub(lambda m: self._numbered("move", m.group(0)), text)
        text = HASH.sub(lambda m: self._numbered("hash", m.group(0)), text)
        return AT.sub("<at>", text)

    def _numbered(self, kind: str, raw: str) -> str:
        table = self.seen[kind]
        return table.setdefault(raw, f"<{kind}-{len(table) + 1}>")
