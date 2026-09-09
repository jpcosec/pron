"""Deterministic normalization of relative dates and times with the session clock (spec 11 §3)."""

from __future__ import annotations

import re
from datetime import date, datetime, timedelta
from typing import Any

WEEKDAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
]
RELATIVE = {"today": 0, "tomorrow": 1, "yesterday": -1}
TIME_RE = re.compile(r"^(\d{1,2})(?::(\d{2}))?\s*(am|pm)?$", re.I)


def session_date(now: Any) -> date:
    if isinstance(now, datetime):
        return now.date()
    if isinstance(now, date):
        return now
    if isinstance(now, str) and now:
        return datetime.fromisoformat(now).date()
    return date.today()


def parse_day(token: str, now: Any = None) -> str | None:
    """A weekday name → the next occurrence (today counts as ambiguous, resolved as next);
    today/tomorrow/yesterday; an ISO date. Returns YYYY-MM-DD or None."""
    t = token.lower().strip()
    base = session_date(now)
    if t in RELATIVE:
        return (base + timedelta(days=RELATIVE[t])).isoformat()
    if t in WEEKDAYS:
        target = WEEKDAYS.index(t)
        delta = (target - base.weekday()) % 7
        return (
            (base + timedelta(days=delta or 7)).isoformat()
            if delta == 0
            else (base + timedelta(days=delta)).isoformat()
        )
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", t):
        return t
    return None


def parse_time(token: str) -> str | None:
    """'9pm' → 21:00, '21' → 21:00, '9:30pm' → 21:30, '21:00' → 21:00."""
    m = TIME_RE.match(token.strip())
    if not m:
        return None
    hour, minute, ampm = (
        int(m.group(1)),
        int(m.group(2) or 0),
        (m.group(3) or "").lower(),
    )
    if ampm == "pm" and hour < 12:
        hour += 12
    if ampm == "am" and hour == 12:
        hour = 0
    if not (0 <= hour < 24 and 0 <= minute < 60):
        return None
    return f"{hour:02d}:{minute:02d}"
