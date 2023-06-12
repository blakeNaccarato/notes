"""Test configuration."""

from pathlib import Path
from shutil import copytree

import pytest

TEST_DATA = Path("tests/data")
TEST_DATA.mkdir(exist_ok=True)


@pytest.fixture()
def tmp_project(monkeypatch, tmp_path: Path) -> Path:
    """Produce a temporary project directory."""

    import notes
    from notes import DATA_DIR as ORIG_DATA_DIR

    monkeypatch.setattr(notes, "PARAMS_FILE", tmp_path / "params.yaml")
    monkeypatch.setattr(notes, "DATA_DIR", tmp_path)

    from notes.models.params import PARAMS

    copytree(TEST_DATA, PARAMS.paths.data, dirs_exist_ok=True)
    for directory in [
        path
        for path in sorted(ORIG_DATA_DIR.iterdir())
        if path.is_dir() and path.name not in ["external", "local"]
    ]:
        copytree(directory, PARAMS.paths.data / directory.name, dirs_exist_ok=True)

    return tmp_path
