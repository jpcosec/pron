"""spec 14 §4, Auditoría: kb_audit is what pron check says plus check_edges, and the report
of the server's --audit MODULE:FUNC on the world's root when there is one. Level 0."""

from __future__ import annotations

from mcp_wiring.wired import restaurant, wire

AUDIT = """
def frozen(root):
    return {"ok": True, "root": str(root), "queries": 2}


def broken(root):
    raise RuntimeError("the spec moved")
"""


def test_audit_is_the_integrity_of_the_world(tmp_path):
    app, w = wire(restaurant(tmp_path), "reader")
    answer = app.tools.call("kb_audit", world=w)
    assert answer["ok"] and answer["lints"] == [] and "audit" not in answer


def test_audit_calls_the_worlds_own_function(tmp_path):
    world = restaurant(tmp_path)
    (tmp_path / "kitchen_audit.py").write_text(AUDIT, encoding="utf-8")
    assert world.store.pythonpath == str(tmp_path)
    app, w = wire(world, audit="kitchen_audit:frozen")
    report = app.tools.call("kb_audit", world=w)["audit"]
    assert report == {"ok": True, "root": str(world.root), "queries": 2}
    app, w = wire(world, audit="kitchen_audit:broken")
    report = app.tools.call("kb_audit", world=w)["audit"]
    assert report == {"ok": False, "error": "RuntimeError: the spec moved"}
