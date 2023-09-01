"""Tests."""

import importlib

import pytest

from tests import STAGES


@pytest.mark.parametrize("stage", STAGES)
def test_stages(stage: str):
    """Test that stages can run."""
    importlib.import_module(stage).main()
