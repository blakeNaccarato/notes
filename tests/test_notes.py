"""Tests."""

import importlib
from pathlib import Path

import pytest

STAGES = sorted(Path("src/notes/stages").glob("[!__]*.py"))


@pytest.mark.slow()
@pytest.mark.usefixtures("tmp_project")
@pytest.mark.parametrize(
    ("stage", "x"),
    (
        {stage.stem: "" for stage in STAGES}
        | {stage.stem: "xfail" for stage in STAGES if stage.stem in []}
    ).items(),
)
def test_stages(stage: str, x: str):
    """Test that stages can run."""
    if x == "xfail":
        pytest.xfail("Stage not yet implemented.")
    importlib.import_module(f"notes.stages.{stage}").main()
