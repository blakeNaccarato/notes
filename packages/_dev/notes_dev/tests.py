"""Tests."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from _pytest.mark.structures import ParameterSet


@dataclass
class Args:
    args: list[Any]
    kwargs: dict[str, Any]


@dataclass
class Expectation:
    result: Path
    expected: Path


type Stages = list[ParameterSet]
type AllArgs = dict[str, Args]
type Expected = dict[str, Expectation]


def get_args() -> AllArgs:
    return {
        module: Args(*args)
        for module, args in {"notes.stages.sync_settings": (["amsl"], {})}.items()
    }


def get_expected() -> Expected:
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
