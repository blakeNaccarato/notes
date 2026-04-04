"""Types."""

from typing import Literal, TypedDict

type PythonVersion = Literal["3.11", "3.12", "3.13", "3.14"]
"""Python version."""
SubmoduleInfoKind = Literal["paths", "urls"]
"""Submodule info kind."""
Op = Literal[" @ ", "=="]
"""Allowable operator."""
ops: tuple[Op, ...] = (" @ ", "==")
"""Allowable operators."""
type ChangeType = Literal["breaking", "deprecation", "change"]
"""Type of change to add to changelog."""
type Action = Literal["default", "error", "ignore", "always", "module", "once"]
"""Action to take for a warning."""


class Dep(TypedDict):
    """Dependency."""

    op: Op
    """Operator."""
    rev: str
    """Revision."""
