"""Configure tests."""

from collections.abc import Sequence
from os import environ

import pytest


def pytest_collection_modifyitems(items):
    """Skip slow tests when all tests run in VSCode."""
    if not environ.get("VSCODE_PID") or all(
        item.name != "test_all_tests_run" for item in items
    ):
        return
    for item in items:
        if not (add_marker := getattr(item, "add_marker", None)):
            continue
        markers = [
            *item.own_markers,
            *(
                pytestmark
                if isinstance(
                    (pytestmark := getattr(item.module, "pytestmark", [])), Sequence
                )
                else [pytestmark]
            ),
        ]
        if any(m.name == "slow" for m in markers):
            add_marker(pytest.mark.skip(reason="Skip when running all tests in VSCode"))
