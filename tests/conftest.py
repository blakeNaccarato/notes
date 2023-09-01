"""Test configuration."""

from collections.abc import Callable
from importlib import import_module
from pathlib import Path

import pytest
from boilercore import filter_certain_warnings
from boilercore.testing import get_session_path

import notes
from tests import EXPECTED, STAGES


@pytest.fixture(scope="session")
def project_session_path(tmp_path_factory):
    """Set the project directory."""
    return get_session_path(tmp_path_factory, notes)


# Can't be session scope
@pytest.fixture(autouse=True)
def _filter_certain_warnings():
    """Filter certain warnings."""
    filter_certain_warnings()


@pytest.fixture(params=STAGES)
def stage_module_name(request, project_session_path) -> str:
    """Name of a stage module."""
    return request.param


@pytest.fixture()
def stage(stage_module_name) -> Callable[..., None]:
    """Get the expected data directory."""
    return import_module(stage_module_name).main


@pytest.fixture()
def result(stage_module_name, project_session_path) -> Path | None:
    """Get the resulting data directory."""
    expectation = EXPECTED.get(stage_module_name)
    return project_session_path / expectation.result if expectation else None


@pytest.fixture()
def expected(stage_module_name) -> Path | None:
    """Get the expected data directory."""
    expectation = EXPECTED.get(stage_module_name)
    return expectation.expected if expectation else None
