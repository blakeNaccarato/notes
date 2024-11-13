"""Tests."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeAlias

from _pytest.mark.structures import ParameterSet


@dataclass
class Args:  # noqa: D101
    args: list[Any]
    kwargs: dict[str, Any]


@dataclass
class Expectation:  # noqa: D101
    result: Path
    expected: Path


Stages: TypeAlias = list[ParameterSet]
AllArgs: TypeAlias = dict[str, Args]
Expected: TypeAlias = dict[str, Expectation]


def get_args() -> AllArgs:  # noqa: D103
    return {
        module: Args(*args)
        for module, args in {"notes.stages.sync_settings": (["amsl"], {})}.items()
    }


def get_expected() -> Expected:  # noqa: D103
    vaults = Path("data") / "local" / "vaults"
    expected_root = Path("tests") / "expected"
    return {
        module: Expectation(path, expected_root / path)
        for module, path in {
            "notes.stages.move_timestamped": vaults / "personal" / "_timestamped"
        }.items()
    }


STAGES = ["sanitize_source_tags", "sync_settings"]
ARGS = get_args()
EXPECTED = get_expected()
