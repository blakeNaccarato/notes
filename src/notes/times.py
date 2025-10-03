"""Datetime-related values."""

from datetime import UTC, date, datetime, time

current_tz = datetime.now().astimezone().tzinfo
min_datetime = datetime.min.replace(tzinfo=UTC)


def get_now() -> datetime:
    """Get current `datetime` in UTC."""
    return datetime.now(UTC)


def get_time_today(value: time) -> datetime:
    """Get `datetime` for today in UTC."""
    return datetime.combine(date.today(), value, tzinfo=current_tz).astimezone(UTC)
