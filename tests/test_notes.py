"""Tests."""

from filecmp import dircmp


def test_stages(stage, result, expected):
    """Test that stages can run."""
    stage()
    if result and expected:
        cmp = dircmp(result, expected)
        assert cmp.left_list == cmp.right_list
