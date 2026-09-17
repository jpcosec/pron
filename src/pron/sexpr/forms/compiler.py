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

A noun compiles in pron.sexpr.forms.noun_compiler; each move form is one `Form`
(pron.sexpr.forms.form_registry); the shape of a form is pron.sexpr.forms.syntax.
"""

from __future__ import annotations

from difflib import get_close_matches
from typing import TYPE_CHECKING, Any

from pron.kernel.parts.part import Part
from pron.kernel.sexp.read_write import Sym, read_one, write
from pron.sexpr.forms.form_error import FormError
from pron.sexpr.forms.form_registry import FORMS
from pron.sexpr.forms.form_words import FormWords
from pron.sexpr.forms.not_a_move import NotAMove
from pron.sexpr.forms.noun_compiler import NounCompiler
from pron.sexpr.forms.syntax import MOVE_HEADS, NOUN_HEADS, form_head

if TYPE_CHECKING:
    from pron.world.lexicon import Lexicon
    from pron.world.world import World


class Compiler:
    """Turns forms into the parts a session plans and runs. Names are checked against the
    session's lexicon: a model, a relation or an alias outside the projection does not exist."""

    def __init__(self, lex: Lexicon, world: World):
        self.lex, self.world = lex, world
        self.words = FormWords(lex, world)
        self.noun = NounCompiler(self.words)

    def compile(self, expr: Any) -> list[Part]:
        if isinstance(expr, str) and not isinstance(expr, Sym):
            expr = read_one(expr)
        forms = expr[1:] if form_head(expr) == "move" else [expr]
        for f in forms:
            if form_head(f) in NOUN_HEADS:
                raise NotAMove(
                    f"A noun is not a move: did you mean {write([Sym('show'), f])}?"
                )
        return [self._form(f) for f in forms]

    def _form(self, form: Any) -> Part:
        head = form_head(form)
        move = FORMS.get(head)
        if move is None:
            close = get_close_matches(head, MOVE_HEADS, n=1, cutoff=0.75)
            hint = f"; did you mean ({close[0]} …)?" if close else ""
            raise FormError(f"unknown form: ({head} …){hint}")
        return move(self, *form[1:])
