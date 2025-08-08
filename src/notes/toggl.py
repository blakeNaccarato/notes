"""Toggl events.

Derived from https://gist.github.com/blakeNaccarato/8e114a7216da6ce7f7882fd77ab8c5cd
"""

from typing import Any

import sqlalchemy as sa
from sqlmodel import Field, SQLModel


def DbField(name: str, sa_type, **kwds: Any):  # noqa: N802  # Derived from `Field()`, also a class-like function
    """Field as it is named in the database. Allows the SQLModel field name to vary."""
    return Field(sa_column=sa.Column(name, sa_type, **kwds))


class Event(SQLModel, table=True):
    """Task and latest info."""

    __tablename__ = "TimelineEvents"  # pyright: ignore[reportAssignmentType]

    id: int = DbField(name="Id", sa_type=sa.Integer, primary_key=True)  # pyright: ignore[reportRedeclaration]
    path: str = DbField(name="Filename", sa_type=sa.Text)
    title: str = DbField(name="Title", sa_type=sa.Text)
    start: int = DbField(name="StartTime", sa_type=sa.Integer)
    end: int = DbField(name="EndTime", sa_type=sa.Integer)
    idle: int = DbField(name="Idle", sa_type=sa.Integer)
