"""Test Pomodouroboros at home."""

import pytest

from notes.pomodouroboros_at_home import set_toggl_pomodoro

pytestmark = pytest.mark.slow


@pytest.mark.parametrize("mode", ["start", "end"])
def test_set_toggl_pomodoro(mode):
    """Set a Pomodoro."""
    set_toggl_pomodoro(mode)
