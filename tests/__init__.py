"""Test setup."""

from dataclasses import dataclass
from pathlib import Path
from typing import TypeAlias

import pytest
from _pytest.mark.structures import ParameterSet
from boilercore.paths import get_module_rel, walk_modules


@dataclass
class Expectation:
    result: Path
    expected: Path


Stages: TypeAlias = list[ParameterSet]
Expected: TypeAlias = dict[str, Expectation]


def init() -> tuple[Stages, Expected]:
    """Get stages and expected results. Runs at the end of this module."""
    return get_stages(), get_expected()


def get_expected() -> Expected:
    vaults = Path("data") / "local" / "vaults"
    expected_root = Path("tests") / "expected"
    expected: dict[str, Expectation] = {
        module: Expectation(path, expected_root / path)
        for module, path in {
            "notes.stages.move_timestamped": vaults / "personal" / "_timestamped"
        }.items()
    }

    return expected


def get_stages():
    notes = Path("src") / "notes"
    stages = notes / "stages"
    return [
        (
            pytest.param(
                module,
                id=(rel := get_module_rel(module, "stages")),
                marks=[pytest.mark.skip] if rel in {"originlab"} else [],
            )
        )
        for module in walk_modules(stages, notes)
    ]


STAGES, EXPECTED = init()
