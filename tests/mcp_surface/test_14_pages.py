"""spec 14 §2, §3: a set comes paged — the ten best of a ranked search, fifty of any other set —
with its total and `truncated: true` when documents follow the page; `limit` and `offset`
rule when given."""

from __future__ import annotations

import pytest

from mcp_surface.mounted import ids
from pron.mcp.page import SET_LIMIT, Page


def test_a_ranked_search_brings_the_ten_best_unless_told(app):
    answer = app.tools.call("kb_get", uri="kb://rest/?table")
    assert len(answer["documents"]) == 10 and answer["total"] > 10
    assert answer["truncated"] is True
    three = app.tools.call("kb_get", uri="kb://rest/?table", limit=3)
    assert ids(three) == ids(answer)[:3] and three["total"] == answer["total"]


def test_find_pages_with_limit_and_offset(app):
    whole = app.tools.call("kb_find", world="rest", model="Table")
    assert whole["total"] == len(whole["documents"]) and "truncated" not in whole
    page = app.tools.call("kb_find", world="rest", model="Table", limit=2, offset=1)
    assert ids(page) == ids(whole)[1:3] and page["offset"] == 1
    assert page["truncated"] is True and page["total"] == whole["total"]
    ranked = app.tools.call("kb_find", world="rest", model="Table", text="table")
    assert len(ranked["documents"]) == min(10, ranked["total"])


def test_listings_and_selectors_carry_their_total(app):
    listing = app.tools.call("kb_get", uri="kb://rest/Table", limit=1)
    assert len(listing["documents"]) == 1 and listing["truncated"] is True
    terrace = app.tools.call("kb_get", uri="kb://rest/@terrace")
    assert terrace["total"] == 3 and "truncated" not in terrace


def test_a_set_is_cut_at_fifty_by_default():
    rows = [{"id": str(i)} for i in range(SET_LIMIT + 5)]
    answer = Page().cut({"documents": rows, "notes": []})
    assert len(answer["documents"]) == SET_LIMIT and answer["total"] == SET_LIMIT + 5
    assert answer["truncated"] is True and answer["notes"] == []
    assert Page(offset=SET_LIMIT).cut({"documents": rows})["documents"] == rows[50:]
    assert Page(2).cut({"value": 1}) == {"value": 1}
    with pytest.raises(ValueError):
        Page(-1)
