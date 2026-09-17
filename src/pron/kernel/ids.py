"""Export ids and addresses, with the store they belong to (spec 02, 12 §5).

An export id is `Model:doc` for a document of the local store and `store:Model:doc` for
one of a store linked into it; an address is `st.{Model}.doc` or `store:st.{Model}.doc`
(sldb's own prefix form). `None` and "local" both mean the local store. Nothing else in
pron splits an id by hand.
"""

from __future__ import annotations

import re

LOCAL = "local"


def is_local(store: str | None) -> bool:
    return store is None or store == LOCAL


def split_id(export_id: str) -> tuple[str | None, str, str]:
    """('A', 'Model', 'doc') for 'A:Model:doc'; (None, 'Model', 'doc') for 'Model:doc'."""
    parts = export_id.split(":", 2)
    if len(parts) == 3:
        return (None if parts[0] == LOCAL else parts[0]), parts[1], parts[2]
    if len(parts) == 2:
        return None, parts[0], parts[1]
    raise ValueError(f"not an export id: {export_id!r}")


def join_id(store: str | None, model: str, doc: str) -> str:
    return f"{model}:{doc}" if is_local(store) else f"{store}:{model}:{doc}"


def split_relation_doc_id(export_id: str) -> tuple[str | None, str] | None:
    """(store, doc name) for 'RelationDoc:{name}' or 'A:RelationDoc:{name}', None otherwise.
    A RelationDoc's name embeds export ids (colons), so the ordinary split_id cannot parse
    these; the store prefix carries no colon, so this match is unambiguous."""
    m = re.fullmatch(r"(?:([^:]+):)?RelationDoc:(.+)", export_id)
    if m is None:
        return None
    return (None if m.group(1) in (None, LOCAL) else m.group(1)), m.group(2)


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
    store, model, doc = split_id(export_id)
    a = f"st.{{{model}}}.{doc}"
    return a if store is None else f"{store}:{a}"


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
    """The id as the documents of `store` write it: a document of that same store carries no
    prefix, so the store reads its own documents the same alone and through a daemon."""
    s, model, doc = split_id(export_id)
    return join_id(None, model, doc) if s is not None and s == store else export_id


def qualify(export_id: str, store: str | None) -> str:
    """The id as a session that links `store` names it: an unprefixed id read from a document
    of that store belongs to that store."""
    s, model, doc = split_id(export_id)
    return (
        join_id(store, model, doc) if s is None and not is_local(store) else export_id
    )


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
