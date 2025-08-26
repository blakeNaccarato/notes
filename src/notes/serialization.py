"""Serialization."""

import json
from datetime import datetime
from typing import Any

from notes.times import current_tz


def ser_json(obj: dict[str, Any] | None = None, sort: bool = True) -> str:
    """Dump JSON data."""
    return json.dumps(ensure_ascii=False, sort_keys=sort, indent=2, obj=obj or {})


def ser_datetime(value: datetime) -> str:
    """Serialize datetime."""
    return value.astimezone(current_tz).isoformat(timespec="seconds")
