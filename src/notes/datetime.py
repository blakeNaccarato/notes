"""Datetime-related values."""

from datetime import datetime

__all__ = ["current_tz"]

current_tz = datetime.now().astimezone().tzinfo
