"""Test configuration."""

import pytest
from boilercore import filter_certain_warnings
from boilercore.testing import get_session_path

import notes


@pytest.fixture(scope="session", autouse=True)
def _project_session_path(tmp_path_factory: pytest.TempPathFactory):
    """Set the project directory."""
    get_session_path(tmp_path_factory, notes)


# Can't be session scope
@pytest.fixture(autouse=True)
def _filter_certain_warnings():
    """Filter certain warnings."""
    filter_certain_warnings()
