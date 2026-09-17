"""Forms: the structured language of pron (spec 13). The surface turns a sentence into forms and
does nothing else; evaluating forms resolves every noun (addresses, predicates, proper names,
complements, referents of the dialogue), asks when a noun is ambiguous or a field is missing,
checks, writes, refreshes and records. A runtime that already has its documents writes the forms.

Nouns
    (doc "Model:name" ...)                 documents by export id
    (the Model clause ...)                 one document
    (a Model clause ...)                   any one
    (all Model clause ...)                 every document that matches (find is the same)
    (it "word" [Model])  (them "word" [Model])  (me "word")      referents of the dialogue
        clauses: (where "<sldb predicate>")  (named "proper name")  (of NOUN)  (of-name "word" ...)
                 (plural)  (asked)  (set field value)  (not-a-value Model field "text")

Moves
    (show NOUN)
    (targets relation [NOUN] [(of Model)] [(where "...")])   what NOUN relates to
    (sources relation [NOUN] [(of Model)] [(where "...")])   what relates to NOUN
    (assert relation SUBJECT OBJECT)
    (create Model [(as "doc-name")] (field value) ...)
    (change NOUN field value)  (add NOUN field value)  (remove NOUN field [value])
    (clean NOUN field)  (forget NOUN)
    (say alias NOUN)                                 an action alias
    (say alias SUBJECT OBJECT)                       a relation alias
    (say alias (slot "$referent:M" NOUN) (slot "$object:M" NOUN) [(as "doc-name")] (field value) ...)
    (undo)  (refresh)  (why [NOUN])
    (move FORM ...)                                  several parts, one move

Values are strings, numbers, true, false, nil, or (list value ...).
"""

from __future__ import annotations

from difflib import get_close_matches
from typing import TYPE_CHECKING, Any

from pron.kernel.ids import address_of, model_of
from pron.kernel.item import Item
from pron.kernel.noun_phrase import NounPhrase
from pron.kernel.part import Part
from pron.kernel.sexp import Sym, read_one, write
from pron.kernel.word import Word
from pron.sexpr.form_error import FormError
from pron.sexpr.not_a_move import NotAMove
from pron.sexpr.resolution import address_to_export_id
from pron.sexpr.unknown_word import UnknownWord
from pron.world.store_error import StoreError

if TYPE_CHECKING:
    from pron.session import Session

NOUN_HEADS = ("doc", "the", "a", "all", "find", "it", "them", "me")
REFERENT_HEADS = {"it": "singular", "them": "plural", "me": "speaker"}
MOVE_HEADS = (
    "show",
    "targets",
    "sources",
    "assert",
    "create",
    "change",
    "add",
    "remove",
    "clean",
    "forget",
    "say",
    "undo",
    "refresh",
    "why",
    "move",
)


# -- evaluation: forms → parts whose nouns the session resolves ---------------------------------


class Compiler:
    """Turns forms into the parts a session plans and runs. Names are checked against the
    session's lexicon: a model, a relation or an alias outside the projection does not exist."""

    def __init__(self, session: "Session"):
        self.s = session
        self.lex = session.lex

    def compile(self, expr: Any) -> list[Part]:
        if isinstance(expr, str) and not isinstance(expr, Sym):
            expr = read_one(expr)
        forms = expr[1:] if _head(expr) == "move" else [expr]
        for f in forms:
            if _head(f) in NOUN_HEADS:
                raise NotAMove(
                    f"A noun is not a move: did you mean {write([Sym('show'), f])}?"
                )
        return [self._form(f) for f in forms]

    def _form(self, form: Any) -> Part:
        head = _head(form)
        fn = getattr(self, "_f_" + head.replace("-", "_"), None)
        if fn is None:
            close = get_close_matches(head, MOVE_HEADS, n=1, cutoff=0.75)
            hint = f"; did you mean ({close[0]} …)?" if close else ""
            raise FormError(f"unknown form: ({head} …){hint}")
        part: Part = fn(*form[1:])
        return part

    # nouns

    def noun(self, form: Any) -> NounPhrase:
        head = _head(form)
        if head not in NOUN_HEADS:
            raise FormError(f"not a noun: ({head} …)")
        if head == "doc":
            ids = [str(x) for x in form[1:]]
            for eid in ids:
                self._need_model(model_of(eid))
            np = NounPhrase(
                model_of(ids[0]) if ids else None,
                "the",
                "singular" if len(ids) == 1 else "plural",
            )
            np.given = [address_of(e) for e in ids]
            return np
        if head in REFERENT_HEADS:
            word = str(form[1]) if len(form) > 1 else head
            who = REFERENT_HEADS[head]
            number = "plural" if who == "plural" else "singular"
            item = Item("referent", word, number=number, meta={"who": who})
            np = NounPhrase(None, None, number, referent=item, items=[item])
            if len(form) > 2:
                np.hint = str(form[2])
            return np
        model = str(form[1])
        self._need_model(model)
        det = {"a": "any", "all": "all", "find": "all"}.get(head, "the")
        np = NounPhrase(model, det, "plural" if det == "all" else "singular")
        for clause in form[2:]:
            ch = _head(clause)
            if ch == "where":
                np.predicates.append(str(clause[1]))
            elif ch == "named":
                np.proper.append(str(clause[1]))
            elif ch == "plural":
                np.number = "plural"
            elif ch == "asked":
                np.interrogated = True
            elif ch == "of":
                np.complements.append(self.noun(clause[1]))
            elif ch == "of-name":
                np.complements.append([str(x) for x in clause[1:]])
            elif ch == "set":
                np.captures[str(clause[1])] = _unvalue(clause[2])
            elif ch == "not-a-value":
                np.unknown_values.append(
                    (str(clause[1]), str(clause[2]), str(clause[3]))
                )
            else:
                raise FormError(f"unknown clause in ({head} {model} …): ({ch} …)")
        return np

    def _need_model(self, model: str) -> None:
        if model not in self.lex.models and not (
            set(self.s.world.family_of(model)) & set(self.lex.models)
        ):
            raise UnknownWord(f"I don't have that word: {model}")

    # moves

    def _f_show(self, noun: Any) -> Part:
        return Part("nominal", subject=self.noun(noun))

    def _f_targets(self, relation: Any, *rest: Any) -> Part:
        return self._read(str(relation), rest, asked="object")

    def _f_sources(self, relation: Any, *rest: Any) -> Part:
        return self._read(str(relation), rest, asked="subject")

    def _read(self, relation: str, rest: tuple[Any, ...], asked: str) -> Part:
        w = self._relation_word(relation)
        part = Part("read", verb=w, payload={"asked": asked, "where": []})
        given_role = "subject" if asked == "object" else "object"
        asked_model = None
        for item in rest:
            h = _head(item)
            if h in NOUN_HEADS:
                setattr(part, given_role, self.noun(item))
            elif h == "of":
                asked_model = str(item[1])
            elif h == "where":
                part.payload["where"].append(str(item[1]))
            else:
                raise FormError(f"unknown clause in a read: ({h} …)")
        if asked_model is not None or part.payload["where"]:
            setattr(
                part,
                asked,
                NounPhrase(
                    asked_model, None, "plural", predicates=list(part.payload["where"])
                ),
            )
        return part

    def _f_assert(self, relation: Any, subject: Any, obj: Any) -> Part:
        w = self._relation_word(str(relation))
        return Part("assert", subject=self.noun(subject), object=self.noun(obj), verb=w)

    def _f_create(self, model: Any, *fields: Any) -> Part:
        m = str(model)
        self._need_model(m)
        name = next((str(f[1]) for f in fields if _is_clause(f, "as")), None)
        payload = self._field_pairs(tuple(f for f in fields if not _is_clause(f, "as")))
        extra = {"name": name} if name else {}
        return Part(
            "action",
            subject=NounPhrase(m, "any", "singular"),
            verb=self._kernel_word("create"),
            payload={"verb": "create", "fields": payload, **extra},
        )

    def _write(
        self, verb: str, noun: Any, field_name: Any = None, value: Any = None
    ) -> Part:
        return Part(
            "action",
            subject=self.noun(noun),
            verb=self._kernel_word(verb),
            field_name=str(field_name) if field_name is not None else None,
            value=_unvalue(value),
            payload={"verb": verb},
        )

    def _f_change(self, noun: Any, field_name: Any, value: Any) -> Part:
        return self._write("change", noun, field_name, value)

    def _f_add(self, noun: Any, field_name: Any, value: Any) -> Part:
        return self._write("add", noun, field_name, value)

    def _f_remove(self, noun: Any, field_name: Any, value: Any = None) -> Part:
        return self._write("remove", noun, field_name, value)

    def _f_clean(self, noun: Any, field_name: Any) -> Part:
        return self._write("clean", noun, field_name)

    def _f_forget(self, noun: Any) -> Part:
        return self._write("forget", noun)

    def _f_say(self, symbol: Any, *args: Any) -> Part:
        w = self._alias_word(str(symbol))
        if w.kind == "alias-action":
            if len(args) != 1:
                raise FormError(f"(say {symbol} NOUN): an action alias takes one noun")
            return Part(
                "action",
                subject=self.noun(args[0]),
                verb=w,
                field_name=w.field_name,
                value=w.payload.get("value"),
                payload={"verb": w.payload.get("verb"), "alias": True},
            )
        if w.kind == "alias-relation":
            if len(args) != 2:
                raise FormError(
                    f"(say {symbol} SUBJECT OBJECT): a relation alias takes two nouns"
                )
            return Part(
                "assert", subject=self.noun(args[0]), object=self.noun(args[1]), verb=w
            )
        if w.kind == "alias-compose":
            slots: dict[str, NounPhrase] = {}
            literals: dict[str, Any] = {}
            for arg in args:
                h = _head(arg)
                if h == "slot":
                    np = self.noun(arg[2])
                    for extra in arg[3:]:
                        if _is_clause(extra, "alternatives"):
                            np.alternatives = [address_of(str(e)) for e in extra[1:]]
                    slots[str(arg[1])] = np
                elif h == "as":
                    literals["_name"] = str(arg[1])
                else:
                    literals[h] = _unvalue(arg[1])
            part = Part("compose", verb=w, payload=literals)
            part.payload["_slots"] = slots
            return part
        raise FormError(f"(say {symbol} …): an alias of kind {w.kind} is not a move")

    def _f_undo(self) -> Part:
        return Part("undo", verb=self._kernel_word("undo"))

    def _f_refresh(self) -> Part:
        return Part("refresh", verb=self._kernel_word("refresh"))

    def _f_why(self, noun: Any = None) -> Part:
        part = Part("why")
        if noun is not None:
            np = self.noun(noun)
            if np.given:
                part.payload["target"] = address_to_export_id(np.given[0])
        return part

    # words

    def _relation_word(self, relation: str) -> Word:
        w = next(
            (
                x
                for x in self.lex.words
                if x.kind == "relation" and x.relation == relation
            ),
            None,
        )
        if w is None:
            raise UnknownWord(f"I don't have that word: relation {relation}")
        return w

    def _kernel_word(self, verb: str) -> Word:
        w = next(
            (
                x
                for x in self.lex.words
                if x.kind == "action" and x.payload.get("verb") == verb
            ),
            None,
        )
        if w is None:
            raise StoreError(f"in this session I cannot {verb}")
        return w

    def _alias_word(self, symbol: str) -> Word:
        w = next(
            (
                x
                for x in self.lex.words
                if x.kind.startswith("alias-") and x.payload.get("symbol") == symbol
            ),
            None,
        )
        if w is None:
            raise UnknownWord(f"I don't have that word: alias {symbol}")
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


def _is_clause(form: Any, name: str) -> bool:
    return isinstance(form, list) and bool(form) and form[0] == Sym(name)


def _unvalue(v: Any) -> Any:
    if isinstance(v, list) and v and v[0] == Sym("list"):
        return [_unvalue(x) for x in v[1:]]
    if isinstance(v, Sym):
        return str(v)
    return v
