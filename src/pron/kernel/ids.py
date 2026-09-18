"""Export ids and addresses, with the store they belong to (spec 02, 12 §5).

An export id is `Model:doc` for a document of the local store and `store:Model:doc` for
one of a store linked into it; an address is `st.{Model}.doc` or `store:st.{Model}.doc`
(sldb's own prefix form). `None` and "local" both mean the local store. Nothing else in
pron splits an id by hand.

The implementation is `pron.world.doc_id.DocId`; these are its string-in, string-out
forms. They parse with `DocId.parse`, which reads a RelationDoc's id whole (its name
embeds the ids of its two ends, colons and all) and only then falls back to the blind
split at the first two colons that every other id gets.
"""

from __future__ import annotations

from pron.world.doc_id import LOCAL, DocId, is_local

__all__ = ["LOCAL", "DocId", "is_local"]


def split_id(export_id: str) -> tuple[str | None, str, str]:
    """('A', 'Model', 'doc') for 'A:Model:doc'; (None, 'Model', 'doc') for 'Model:doc'."""
    d = DocId.parse(export_id)
    return d.store, d.model, d.name


def join_id(store: str | None, model: str, doc: str) -> str:
    return str(DocId(store, model, doc))


def split_relation_doc_id(export_id: str) -> tuple[str | None, str] | None:
    """(store, doc name) for 'RelationDoc:{name}' or 'A:RelationDoc:{name}', None otherwise.
    A RelationDoc's name embeds export ids (colons), so the ordinary split_id cannot parse
    these; `DocId.parse` can, and this is its RelationDoc half."""
    d = DocId.parse_relation(export_id)
    return None if d is None else (d.store, d.name)


def model_of(export_id: str) -> str:
    return split_id(export_id)[1]


def doc_of(export_id: str) -> str:
    return split_id(export_id)[2]


def store_of(export_id: str) -> str | None:
    return split_id(export_id)[0]


def scope(store: str | None, model: str, family: bool = True) -> str:
    """The sldb scope of a model in a store: 'A:st.{Model+}' or 'st.{Model+}'."""
    s = f"st.{{{model}{'+' if family else ''}}}"
    return s if is_local(store) else f"{store}:{s}"


def address_of(export_id: str) -> str:
    return DocId.parse(export_id).address


def export_id(address: str) -> str:
    """st.{Model}.doc → Model:doc; A:st.{Model}.doc → A:Model:doc; an export id passes through."""
    a = address
    if a.startswith("st.{"):
        model, doc = a[4:].split("}.", 1)
        return f"{model.rstrip('+')}:{doc}"
    if ":st.{" in a:
        store, rest = a.split(":", 1)
        return f"{store}:{export_id(rest)}"
    return a


def relativize(export_id: str, store: str | None) -> str:
    """The id as the documents of `store` write it (`DocId.relativize`)."""
    d = DocId.parse(export_id)
    return _unless_same(export_id, d, d.relativize(store))


def qualify(export_id: str, store: str | None) -> str:
    """The id as a session that links `store` names it (`DocId.qualify`)."""
    d = DocId.parse(export_id)
    return _unless_same(export_id, d, d.qualify(store))


def _unless_same(export_id: str, before: DocId, after: DocId) -> str:
    """An id that did not move is returned as it was written, 'local:' prefix and all."""
    return export_id if after == before else str(after)


def convert_record(
    record: dict,
    fn,
    keys: tuple[str, ...] = ("address", "source", "target", "source_id", "target_id"),
) -> dict:
    """The same record with every id under those keys passed through fn, at any depth."""

    def walk(x):
        if isinstance(x, dict):
            return {
                k: (fn(v) if k in keys and isinstance(v, str) and ":" in v else walk(v))
                for k, v in x.items()
            }
        if isinstance(x, list):
            return [walk(v) for v in x]
        return x

    return walk(record)


def normalize_address(address: str) -> str:
    """A:st.{M+}.doc and A:st.{M}.doc are the same address."""
    return address.replace("+}", "}")
