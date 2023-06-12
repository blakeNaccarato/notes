"""Test configuration."""

from pathlib import Path
from shutil import copytree

import pytest

TEST_DATA = Path("tests/data")


@pytest.fixture()
def tmp_project(monkeypatch, tmp_path: Path) -> Path:
    """Produce a temporary project directory."""

    import notes

    monkeypatch.setattr(notes, "PARAMS_FILE", tmp_path / "params.yaml")
    monkeypatch.setattr(notes, "DATA_DIR", tmp_path / "cloud")

    from notes.models.params import PARAMS

    copytree(TEST_DATA / "cloud", PARAMS.paths.data, dirs_exist_ok=True)

    return tmp_path
