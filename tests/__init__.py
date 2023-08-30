"""Tests."""
from pathlib import Path

import pytest
from boilercore.paths import get_module_rel, walk_modules

NOTES = Path("src") / "notes"
STAGES_DIR = NOTES / "stages"
STAGES = (
    (
        pytest.param(
            module,
            id=(rel := get_module_rel(module, "stages")),
            marks=[pytest.mark.skip] if rel in {"originlab"} else [],
        )
    )
    for module in walk_modules(STAGES_DIR, NOTES)
)
