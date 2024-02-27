"""Test configuration."""

from collections.abc import Callable
from importlib import import_module
from pathlib import Path
from typing import Any

import pytest
from boilercore import filter_certain_warnings
from boilercore.testing import get_session_path

import notes
from notes_tests import ARGS, EXPECTED, STAGES


# Can't be session scope
@pytest.fixture(autouse=True)
def _filter_certain_warnings():
    """Filter certain warnings."""
    filter_certain_warnings(notes)


@pytest.fixture(scope="session")
def project_session_path(tmp_path_factory):
    """Set the project directory."""
    return get_session_path(tmp_path_factory, notes)


@pytest.fixture(params=STAGES)
def stage_module_name(request, project_session_path) -> str:
    """Name of a stage module."""
    return request.param


@pytest.fixture()
def stage(stage_module_name) -> Callable[..., None]:
    """Stage."""
    return import_module(stage_module_name).main


@pytest.fixture()
def args(stage_module_name) -> Any:
    """Positional arguments."""
    arguments = ARGS.get(stage_module_name)
    return arguments.args if arguments else ()


@pytest.fixture()
def kwargs(stage_module_name) -> dict[str, Any]:
    """Keyword arguments."""
    arguments = ARGS.get(stage_module_name)
    return arguments.kwargs if arguments else {}


@pytest.fixture()
def result(stage_module_name, project_session_path) -> Path | None:
    """Resulting data directory."""
    expectation = EXPECTED.get(stage_module_name)
    return project_session_path / expectation.result if expectation else None


@pytest.fixture()
def expected(stage_module_name) -> Path | None:
    """Expected data directory."""
    expectation = EXPECTED.get(stage_module_name)
    return expectation.expected if expectation else None
