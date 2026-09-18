"""spec 14 §4, nivel 3: a model declared in JSON — its fields checked, its module written the
way pron's models are, and that module checked by import and roundtrip."""

from __future__ import annotations

import pytest

from mcp_wiring.wired import DISH
from pron.mcp.schema.field_decl import FieldDecl
from pron.mcp.schema.model_check import ModelCheck
from pron.mcp.schema.model_source import ModelSource
from pron.mcp.writes.arg_error import ArgError


@pytest.mark.parametrize(
    "raw",
    [
        "price",
        {"name": "class", "type": "str", "description": "d"},
        {"name": "_x", "type": "str", "description": "d"},
        {"name": "x", "type": "dict", "description": "d"},
        {"name": "x", "type": "Literal[1, 2]", "description": "d"},
        {"name": "x", "type": "str", "description": " "},
    ],
)
def test_a_field_that_is_not_one_is_refused(raw):
    with pytest.raises(ArgError):
        FieldDecl.of(raw)


def test_a_field_becomes_its_line():
    course, tags = FieldDecl.of(DISH[2]), FieldDecl.of(DISH[3])
    assert course.enum == ("main", "dessert") and course.required
    assert course.source() == (
        "    course: Literal['main', 'dessert'] = Field(description='Course.')"
    )
    assert "default=[]" in tags.source() and tags.default_json() == "[]"
    assert FieldDecl.of({**DISH[0], "default": "x"}).default_json() == '"x"'


def test_a_model_needs_a_camel_name_and_distinct_fields():
    for name, fields in [("dish", DISH), ("Dish", []), ("Dish", [DISH[0], DISH[0]])]:
        with pytest.raises(ArgError):
            ModelSource.of(name, fields, None, None)


def test_the_default_template_is_a_section_per_field():
    source = ModelSource.of("SideDish", DISH, None, None)
    assert source.snake == "side_dish"
    template = source.default_template()
    assert template.startswith("# SideDish\n\n## Title\n\n⸢rev•title⸥")
    assert "## Tags\n\n- ⸢rev,list•tags⸥" in template


def test_a_generated_module_imports_and_roundtrips():
    source = ModelSource.of("Dish", DISH, None, None)
    check = ModelCheck(source.module(), "Dish")()
    assert check["ok"], check
    assert check["payload"] == {
        "title": "example",
        "price": 1,
        "course": "main",
        "tags": ["example"],
    }


def test_a_module_that_does_not_work_says_why():
    broken = ModelSource.of("Dish", DISH, "# ⸢rev•nothing⸥", None)
    assert not ModelCheck(broken.module(), "Dish")()["ok"]
    assert ModelCheck("raise ValueError('no')", "Dish")()["errors"] == ["import: no"]
