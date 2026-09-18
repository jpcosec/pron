"""A write tool's answer (spec 14 §4): the `Response` (12 §3) as JSON — `text`, `outcome`,
`move_id`, and from its `record` the writes, each with `done`. What the agent needs to go on
comes too when the move left it: the error, what was missing, the candidates of an
ambiguous noun (its pending question, spec 14 §1), and the forms it resolved to.
"""

from __future__ import annotations

import json
from typing import Any

from pron.kernel.parts.response import Response

KEPT = ("error", "missing", "candidates", "resolved", "forms")
# what a write keeps for undo, and is no business of the agent
PRIVATE = ("path", "hash_c")


def response_json(resp: Response, dry_run: bool = False) -> dict[str, Any]:
    record = resp.record or {}
    out: dict[str, Any] = {
        "text": resp.text,
        "outcome": resp.outcome,
        "move_id": resp.move_id,
        "writes": [_write(w) for w in record.get("writes", [])],
        "dry_run": dry_run,
    }
    out.update({k: record[k] for k in KEPT if k in record})
    return json.loads(json.dumps(out, default=str))


def _write(w: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in w.items() if k not in PRIVATE}
