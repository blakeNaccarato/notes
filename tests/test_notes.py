"""Tests."""

from filecmp import dircmp


def test_stages(stage, args, kwargs, result, expected):
    """Test that stages can run."""
    # sourcery skip: no-conditionals-in-tests
    stage(*args, **kwargs)
    if result and expected:
        cmp = dircmp(result, expected)
        assert cmp.left_list == cmp.right_list
