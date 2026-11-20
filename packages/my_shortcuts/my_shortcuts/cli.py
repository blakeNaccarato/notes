"""Command line interface."""

from dataclasses import dataclass
from typing import TypedDict

from cappa import Output, Subcommands, command


@dataclass
class BaseCommand:
    """Base command."""

    dry: bool = False
    verbose: bool = False


class CliKwds(TypedDict):
    """Basic CLI parameters and output as keywords."""

    dry: bool
    verbose: bool
    output: Output


@command(invoke="my_shortcuts.commands.play")  # ty: ignore[not-callable]
class Play(BaseCommand):
    """Play back clicks."""


@command(invoke="my_shortcuts.commands.record")  # ty: ignore[not-callable]
class Record(BaseCommand):
    """Record clicks."""


@command  # ty: ignore[not-callable]
class MyShortcuts:
    """My shortcuts."""

    commands: Subcommands[Record | Play]
