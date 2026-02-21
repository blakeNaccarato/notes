"""Commands."""

from dataclasses import asdict

from cappa import Output

from my_shortcuts.actions import play_clicks, record_clicks
from my_shortcuts.cli import BaseCommand, CliKwds, Play, Record


def play(params: Play, output: Output):
    play_clicks(**get_kwds(params, output))


def record(params: Record, output: Output):
    record_clicks(params.verbose, output)


def get_kwds(params: BaseCommand, output: Output):
    return CliKwds(**asdict(params), output=output)
