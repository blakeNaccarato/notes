"""Toggl events.

Derived from https://gist.github.com/blakeNaccarato/8e114a7216da6ce7f7882fd77ab8c5cd
"""

from typing import Any

import sqlalchemy as sa
from sqlmodel import Field, SQLModel


def IdField():  # noqa: N802  # Derived from `Field()`, also a class-like function
    """Field as it is named in the database. Allows the SQLModel field name to vary."""
    return DbField(name="Id", sa_type=sa.Integer, primary_key=True)


def DbField(name: str, sa_type, **kwds: Any):  # noqa: N802  # Derived from `Field()`, also a class-like function
    """Field as it is named in the database. Allows the SQLModel field name to vary."""
    return Field(sa_column=sa.Column(name, sa_type, **kwds))


class Event(SQLModel, table=True):
    """Event."""

    __tablename__ = "TimelineEvents"  # pyright: ignore[reportAssignmentType]

    id: int = IdField()  # pyright: ignore[reportRedeclaration]
    filename: str = DbField(name="Filename", sa_type=sa.Text)
    title: str = DbField(name="Title", sa_type=sa.Text)
    start_time: int = DbField(name="StartTime", sa_type=sa.Integer)
    end_time: int = DbField(name="EndTime", sa_type=sa.Integer)
    idle: int = DbField(name="Idle", sa_type=sa.Integer)


class Entry(SQLModel, table=True):
    """Entries."""

    __tablename__ = "TimeEntries"  # pyright: ignore[reportAssignmentType]

    id: int = IdField()  # pyright: ignore[reportRedeclaration]
    description: str = DbField(name="Description", sa_type=sa.Text)
    duration: int | None = DbField(name="Duration", sa_type=sa.Integer)


class Preferences(SQLModel, table=True):
    """Preferences."""

    id: int = IdField()  # pyright: ignore[reportRedeclaration]
    pomodoro_break_interval_in_minutes: int = DbField(
        name="PomodoroBreakIntervalInMinutes", sa_type=sa.Integer
    )
    pomodoro_focus_interval_in_minutes: int = DbField(
        name="PomodoroFocusIntervalInMinutes", sa_type=sa.Integer
    )
