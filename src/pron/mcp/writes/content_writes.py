"""The level-1 write tools of one session (spec 14 §4, nivel 1): documents and edges, each a
form evaluated in the session, each answering the `Response` as JSON."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.mcp.writes.content_forms import ContentForms
from pron.mcp.writes.edge_ids import EdgeIds
from pron.mcp.writes.form_runner import FormRunner
from pron.world.mutability import CONTENT

if TYPE_CHECKING:
    from pron.session import Session

Answer = dict[str, Any]


class ContentWrites:
    """`kb_doc_create`, `kb_doc_edit`, `kb_doc_forget`, `kb_edge_assert`, `kb_edge_expire`,
    `kb_undo`, as methods of the session they write in."""

    def __init__(self, session: Session):
        self.session = session
        self.runner = FormRunner(session)

    def doc_create(
        self,
        model: str,
        fields: dict[str, Any],
        name: str | None = None,
        dry_run: bool = False,
    ) -> Answer:
        f = ContentForms.doc_create
        return self.runner(CONTENT, lambda: f(model, fields, name), dry_run)

    def doc_edit(
        self, id: str, ops: list[dict[str, Any]], dry_run: bool = False
    ) -> Answer:
        return self.runner(CONTENT, lambda: ContentForms.doc_edit(id, ops), dry_run)

    def doc_forget(self, id: str, dry_run: bool = False) -> Answer:
        return self.runner(CONTENT, lambda: ContentForms.doc_forget(id), dry_run)

    def edge_assert(
        self, source: str, relation: str, target: str, dry_run: bool = False
    ) -> Answer:
        f = ContentForms.edge_assert
        return self.runner(CONTENT, lambda: f(source, relation, target), dry_run)

    def edge_expire(
        self, source: str, relation: str, target: str, dry_run: bool = False
    ) -> Answer:
        ids = EdgeIds(self.session)
        form = lambda: ContentForms.edge_expire(ids(relation, source, target))  # noqa: E731
        return self.runner(CONTENT, form, dry_run)

    def undo(self, dry_run: bool = False) -> Answer:
        return self.runner(CONTENT, ContentForms.undo, dry_run)
