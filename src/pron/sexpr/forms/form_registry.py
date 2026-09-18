"""The move forms by head (spec 13). `(move FORM ...)` is not among them: it only groups
the forms of one move, and the compiler opens it.
"""

from __future__ import annotations

from pron.sexpr.forms.assert_form import AssertForm
from pron.sexpr.forms.bare_form import BareForm
from pron.sexpr.forms.create_form import CreateForm
from pron.sexpr.forms.form import Form
from pron.sexpr.forms.goal_form import GoalForm
from pron.sexpr.forms.read_form import ReadForm
from pron.sexpr.forms.say_form import SayForm
from pron.sexpr.forms.show_form import ShowForm
from pron.sexpr.forms.why_form import WhyForm
from pron.sexpr.forms.write_form import WriteForm

FORMS: dict[str, Form] = {
    f.head: f
    for f in (
        ShowForm(),
        ReadForm("targets", asked="object"),
        ReadForm("sources", asked="subject"),
        AssertForm(),
        CreateForm(),
        WriteForm("change", 3),
        WriteForm("add", 3),
        WriteForm("remove", 2, optional=1),
        WriteForm("clean", 2),
        WriteForm("forget", 1),
        SayForm(),
        BareForm("undo"),
        BareForm("refresh"),
        WhyForm(),
        GoalForm(),
    )
}
