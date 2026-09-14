"""Forms: the structured moves pron evaluates (spec 13). A sentence becomes forms after the surface
resolves every phrase (spec 06), and a runtime that already knows its documents writes the forms
directly. Both go through the same evaluation: permissions, pre-validation, writes, refresh,
MoveDoc and undo.

Nouns
    (doc "Model:name" ...)                     documents by export id
    (the Model clause ...)                     exactly one document; more than one is ambiguous
    (find Model clause ...)                    every document that matches
        clauses: (where "<sldb predicate>") (named "proper name")

Moves
    (show NOUN)
    (targets relation NOUN [(of Model)] [(where "...")])   what NOUN relates to
    (sources relation NOUN [(of Model)] [(where "...")])   what relates to NOUN
    (assert relation SUBJECT OBJECT)
    (create Model (field value) ...)
    (change NOUN field value)  (add NOUN field value)  (remove NOUN field [value])
    (clean NOUN field)  (forget NOUN)
    (say alias NOUN)                           an action alias on NOUN
    (say alias (slot "$referent:M" NOUN) (slot "$object:M" NOUN [(alternatives id ...)]) (field value) ...)
    (undo)  (refresh)  (why [NOUN])
    (move FORM ...)                            several parts, one move

Values are strings, numbers, true, false, nil, or (list value ...).
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pron.ids import address_of, model_of
from pron.lexicon import Word
from pron.resolve import Resolution
from pron.response import Response
from pron.sexp import Sym, read_one, write
from pron.store import StoreError
from pron.surface.interpret import Part
from pron.surface.nouns import NounPhrase

if TYPE_CHECKING:
    from pron.session import Session

WRITE_VERBS = ("change", "add", "remove", "clean", "forget")


class FormError(ValueError):
    """A form that is not well made: unknown head, wrong arity, a word not in the projection."""


# -- printing: a resolved move → forms ------------------------------------------------------------


def of_move(parts: list[Part], plans: list[dict[str, Any]], session: "Session") -> Any:
    forms = [of_part(p, plan, session) for p, plan in zip(parts, plans)]
    return forms[0] if len(forms) == 1 else [Sym("move"), *forms]


def of_part(part: Part, plan: dict[str, Any], session: "Session") -> Any:
    k = part.kind
    if k == "nominal":
        return [Sym("show"), _noun(plan["subject"])]
    if k == "read":
        assert part.verb is not None and part.verb.relation is not None
        asked = part.payload.get("asked", "object")
        head = "targets" if asked == "object" and "subject" in plan else "sources"
        given = plan["subject"] if head == "targets" else plan["object"]
        form: list[Any] = [Sym(head), Sym(part.verb.relation), _noun(given)]
        asked_np = part.subject if asked == "subject" else part.object
        if asked_np is not None and asked_np.model:
            form.append([Sym("of"), Sym(asked_np.model)])
        if asked_np is not None:
            for where in session._leftover_predicates(asked_np, part.leftovers):
                form.append([Sym("where"), where])
        return form
    if k == "assert":
        assert part.verb is not None and part.verb.relation is not None
        return [Sym("assert"), Sym(part.verb.relation), _noun(plan["subject"]), _noun(plan["object"])]
    if k == "action":
        verb = part.payload.get("verb", part.verb.payload.get("verb") if part.verb else None)
        if verb == "create":
            assert part.subject is not None and part.subject.model is not None
            return [Sym("create"), Sym(part.subject.model), *_fields(part.payload["fields"])]
        if part.payload.get("alias") and part.verb is not None:
            return [Sym("say"), Sym(part.verb.payload["symbol"]), _noun(plan["subject"])]
        form = [Sym(verb), _noun(plan["subject"])]
        if part.field_name is not None:
            form.append(Sym(part.field_name))
        if verb in ("change", "add") or (verb == "remove" and part.value is not None):
            form.append(_value(part.value))
        return form
    if k == "compose":
        assert part.verb is not None
        form = [Sym("say"), Sym(part.verb.payload["symbol"])]
        seen: set[str] = set()
        for step, resolved in zip(part.verb.payload.get("steps", []), plan["steps"]):
            for slot_key, res in resolved.items():
                slot = step[slot_key]
                if slot in seen:
                    continue
                seen.add(slot)
                binding: list[Any] = [Sym("slot"), slot, _noun(res)]
                if res.candidates and res.note.startswith("any"):
                    binding.append([Sym("alternatives"), *[_eid(c) for c in res.candidates]])
                form.append(binding)
        literals = {key: v for key, v in part.payload.items() if not key.startswith("_")}
        form.extend(_fields(literals))
        return form
    if k == "why":
        target = session._why_target(part)
        return [Sym("why"), [Sym("doc"), target]] if target else [Sym("why")]
    if k in ("undo", "refresh"):
        return [Sym(k)]
    raise FormError(f"a part of kind {k} has no form")


def _noun(res: Resolution) -> list[Any]:
    return [Sym("doc"), *res.export_ids()]


def _eid(address: str) -> str:
    from pron.resolve import address_to_export_id

    return address_to_export_id(address)


def _fields(fields: dict[str, Any]) -> list[Any]:
    return [[Sym(k), _value(v)] for k, v in fields.items()]


def _value(v: Any) -> Any:
    if isinstance(v, (list, tuple)):
        return [Sym("list"), *[_value(x) for x in v]]
    return v


# -- evaluation: forms → a move the session runs ------------------------------------------------


class Compiler:
    """Turns forms into the parts and plans Session runs. Nouns resolve here, against the
    projection: a model, a relation or an alias outside it does not exist for the session."""

    def __init__(self, session: "Session", trace: list[str], record: dict[str, Any]):
        self.s = session
        self.lex = session.lex
        self.trace = trace
        self.record = record

    def compile(self, expr: Any) -> tuple[list[Part], list[dict[str, Any]]] | Response:
        if isinstance(expr, str) and not isinstance(expr, Sym):
            expr = read_one(expr)
        forms = expr[1:] if _head(expr) == "move" else [expr]
        parts, plans = [], []
        for form in forms:
            got = self._form(form)
            if isinstance(got, Response):
                return got
            parts.append(got[0])
            plans.append(got[1])
        return parts, plans

    def _form(self, form: Any) -> tuple[Part, dict[str, Any]] | Response:
        head = _head(form)
        args = form[1:]
        fn = getattr(self, "_f_" + head.replace("-", "_"), None)
        if fn is None:
            raise FormError(f"unknown form: ({head} …)")
        return fn(*args)

    # nouns

    def noun(self, form: Any, need_model: str | None = None) -> Resolution | Response:
        head = _head(form)
        if head == "doc":
            ids = [str(x) for x in form[1:]]
            for eid in ids:
                if not self._model_in_projection(model_of(eid)):
                    return Response(f"I don't have that word: {model_of(eid)}.", "missing")
                try:
                    self.s.world.store.hash_of(eid)
                except StoreError:
                    return Response(f"There is no {eid}.", "missing")
            model = model_of(ids[0]) if ids else need_model
            np = NounPhrase(model, "the", "singular" if len(ids) == 1 else "plural")
            self.s._note_reads([address_of(e) for e in ids], self.record)
            return Resolution(np, [address_of(e) for e in ids], "unico", note="by address")
        if head in ("the", "find"):
            model = str(form[1])
            if not self._model_in_projection(model):
                return Response(f"I don't have that word: {model}.", "missing")
            np = NounPhrase(model, "the" if head == "the" else "all", "singular" if head == "the" else "plural")
            for clause in form[2:]:
                ch = _head(clause)
                if ch == "where":
                    np.predicates.append(str(clause[1]))
                elif ch == "named":
                    np.proper.append(str(clause[1]))
                else:
                    raise FormError(f"unknown clause in ({head} {model} …): ({ch} …)")
            res = self.s._resolve_phrase(np, need_model, self.trace, self.record)
            if res.outcome == "missing":
                return self.s._missing(res, self.trace, self.record)
            if head == "the" and len(res.addresses) > 1:
                ids = res.export_ids()
                self.record["candidates"] = ids
                return Response("Which one? " + " · ".join(f"(doc \"{e}\")" for e in ids), "ambiguo")
            if head == "the" and not res.addresses:
                return Response(f"There is no {model} like that.", "missing")
            return res
        raise FormError(f"not a noun: ({head} …)")

    def _model_in_projection(self, model: str) -> bool:
        return bool(set(self.s.world.family_of(model)) & set(self.lex.models)) or model in self.lex.models

    # moves

    def _f_show(self, noun: Any):
        res = self.noun(noun)
        if isinstance(res, Response):
            return res
        return Part("nominal", subject=res.phrase), {"subject": res}

    def _f_targets(self, relation: Any, noun: Any, *clauses: Any):
        return self._read(str(relation), noun, clauses, asked="object")

    def _f_sources(self, relation: Any, noun: Any, *clauses: Any):
        return self._read(str(relation), noun, clauses, asked="subject")

    def _read(self, relation: str, noun: Any, clauses, asked: str):
        w = self._relation_word(relation)
        rt = self.lex.relation_types.get(relation, {})
        given_types = rt.get("source_types" if asked == "object" else "target_types") or []
        res = self.noun(noun, given_types[0] if given_types else None)
        if isinstance(res, Response):
            return res
        asked_model = None
        predicates: list[str] = []
        for clause in clauses:
            ch = _head(clause)
            if ch == "of":
                asked_model = str(clause[1])
            elif ch == "where":
                predicates.append(str(clause[1]))
            else:
                raise FormError(f"unknown clause in a read: ({ch} …)")
        asked_np = NounPhrase(asked_model, None, "plural", predicates=predicates)
        part = Part("read", verb=w, payload={"asked": asked, "where": predicates})
        role = "subject" if asked == "object" else "object"
        setattr(part, role, res.phrase)
        setattr(part, "object" if role == "subject" else "subject", asked_np)
        return part, {role: res}

    def _f_assert(self, relation: Any, subject: Any, obj: Any):
        rel = str(relation)
        w = self._relation_word(rel)
        rt = self.lex.relation_types.get(rel, {})
        s = self.noun(subject, (rt.get("source_types") or [None])[0])
        if isinstance(s, Response):
            return s
        o = self.noun(obj, (rt.get("target_types") or [None])[0])
        if isinstance(o, Response):
            return o
        return Part("assert", subject=s.phrase, object=o.phrase, verb=w), {"subject": s, "object": o}

    def _f_create(self, model: Any, *fields: Any):
        m = str(model)
        if not self._model_in_projection(m):
            return Response(f"I don't have that word: {m}.", "missing")
        payload = self._field_pairs(fields)
        missing = self.s.kernel.required_missing(m, payload)
        if missing:
            return Response(f"{m} needs {', '.join(missing)}.", "missing")
        part = Part(
            "action",
            subject=NounPhrase(m, "a", "singular"),
            verb=self._kernel_word("create"),
            payload={"verb": "create", "fields": payload},
        )
        return part, {}

    def _write(self, verb: str, noun: Any, field_name: Any = None, value: Any = None):
        res = self.noun(noun)
        if isinstance(res, Response):
            return res
        part = Part(
            "action",
            subject=res.phrase,
            verb=self._kernel_word(verb),
            field_name=str(field_name) if field_name is not None else None,
            value=_unvalue(value),
            payload={"verb": verb},
        )
        return part, {"subject": res}

    def _f_change(self, noun, field_name, value):
        return self._write("change", noun, field_name, value)

    def _f_add(self, noun, field_name, value):
        return self._write("add", noun, field_name, value)

    def _f_remove(self, noun, field_name, value=None):
        return self._write("remove", noun, field_name, value)

    def _f_clean(self, noun, field_name):
        return self._write("clean", noun, field_name)

    def _f_forget(self, noun):
        return self._write("forget", noun)

    def _f_say(self, symbol: Any, *args: Any):
        w = self._alias_word(str(symbol))
        if w.kind == "alias-action":
            if len(args) != 1:
                raise FormError(f"(say {symbol} NOUN): an action alias takes one noun")
            rest = w.ref.split(":", 1)[1]
            verb, _, assign = rest.partition(" ")
            fld, value = assign.split("=", 1)
            res = self.noun(args[0], w.model)
            if isinstance(res, Response):
                return res
            part = Part(
                "action",
                subject=res.phrase,
                verb=w,
                field_name=fld.split(".", 1)[1],
                value=value,
                payload={"verb": verb, "alias": True},
            )
            return part, {"subject": res}
        if w.kind == "alias-relation":
            if len(args) != 2:
                raise FormError(f"(say {symbol} SUBJECT OBJECT): a relation alias takes two nouns")
            return self._f_assert(Sym(w.relation or ""), args[0], args[1])
        if w.kind == "alias-compose":
            return self._compose(w, args)
        raise FormError(f"(say {symbol} …): an alias of kind {w.kind} is not a move; use it inside a noun")

    def _compose(self, w: Word, args: tuple[Any, ...]):
        bindings: dict[str, Resolution] = {}
        literals: dict[str, Any] = {}
        for arg in args:
            head = _head(arg)
            if head == "slot":
                slot = str(arg[1])
                kind, _, model = slot[1:].partition(":")
                res = self.noun(arg[2], model or None)
                if isinstance(res, Response):
                    return res
                for extra in arg[3:]:
                    if _head(extra) == "alternatives":
                        res.candidates = [address_of(str(e)) for e in extra[1:]]
                        res.note = "any of them; the first one"
                bindings[slot] = res
            else:
                literals[head] = _unvalue(arg[1])
        plan: dict[str, Any] = {"steps": []}
        for step in w.payload.get("steps", []):
            resolved = {}
            for slot_key in ("source", "target"):
                slot = step.get(slot_key)
                if isinstance(slot, str) and slot.startswith("$") and slot != "$created":
                    if slot not in bindings:
                        return Response(f"(say {w.payload['symbol']} …) needs (slot \"{slot}\" NOUN).", "missing")
                    resolved[slot_key] = bindings[slot]
            plan["steps"].append(resolved)
        planned = self.s._compose_permissions(w)
        if isinstance(planned, Response):
            return planned
        return Part("compose", verb=w, payload=literals), plan

    def _f_undo(self):
        return Part("undo", verb=self._kernel_word("undo")), {}

    def _f_refresh(self):
        return Part("refresh", verb=self._kernel_word("refresh")), {}

    def _f_why(self, noun: Any = None):
        part = Part("why")
        if noun is not None:
            res = self.noun(noun)
            if isinstance(res, Response):
                return res
            part.payload["target"] = res.export_ids()[0] if res.addresses else None
        return part, {}

    # words

    def _relation_word(self, relation: str) -> Word:
        w = next((x for x in self.lex.words if x.kind == "relation" and x.relation == relation), None)
        if w is None:
            raise FormError(f"I don't have that word: relation {relation}")
        return w

    def _kernel_word(self, verb: str) -> Word:
        w = next((x for x in self.lex.words if x.kind == "action" and x.payload.get("verb") == verb), None)
        if w is None:
            raise StoreError(f"in this session I cannot {verb}")
        return w

    def _alias_word(self, symbol: str) -> Word:
        w = next((x for x in self.lex.words if x.kind.startswith("alias-") and x.payload.get("symbol") == symbol), None)
        if w is None:
            raise FormError(f"I don't have that word: alias {symbol}")
        return w

    def _field_pairs(self, fields: tuple[Any, ...]) -> dict[str, Any]:
        out = {}
        for pair in fields:
            if not isinstance(pair, list) or len(pair) != 2:
                raise FormError(f"a field is (name value), got {write(pair)}")
            out[str(pair[0])] = _unvalue(pair[1])
        return out


def _head(form: Any) -> str:
    if not isinstance(form, list) or not form or not isinstance(form[0], Sym):
        raise FormError(f"not a form: {write(form)}")
    return str(form[0])


def _unvalue(v: Any) -> Any:
    if isinstance(v, list) and v and v[0] == Sym("list"):
        return [_unvalue(x) for x in v[1:]]
    if isinstance(v, Sym):
        return str(v)
    return v
