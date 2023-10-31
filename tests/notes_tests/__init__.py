"""Helper functions for tests."""

from dataclasses import dataclass
from pathlib import Path
from typing import Any, TypeAlias

import pytest
from _pytest.mark.structures import ParameterSet
from boilercore.paths import get_module_rel, walk_modules


@dataclass
class Args:
    args: list[Any]
    kwargs: dict[str, Any]


@dataclass
class Expectation:
    result: Path
    expected: Path


Stages: TypeAlias = list[ParameterSet]
AllArgs: TypeAlias = dict[str, Args]
Expected: TypeAlias = dict[str, Expectation]


def get_stages() -> Stages:
    return [
        (
            pytest.param(
                module,
                id=get_module_rel(module, "stages"),
                marks=(
                    [pytest.mark.xfail]
                    if module
                    in {
                        "notes.stages.sync_settings"  # Repo state not mocked yet
                    }
                    else []
                ),
            )
        )
        for module in (
            f"notes.{module}"
            for module in walk_modules(Path("src") / "notes" / "stages")
        )
    ]


def get_args() -> AllArgs:
    return {
        module: Args(*args)
        for module, args in {"notes.stages.sync_settings": (["grad"], {})}.items()
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


STAGES = get_stages()
ARGS = get_args()
EXPECTED = get_expected()
