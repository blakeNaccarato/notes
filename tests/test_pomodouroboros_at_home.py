"""Test Pomodouroboros at home."""

import pytest

from notes.pomodouroboros_at_home import (
    delete_tracking,
    set_toggl_pomodoro,
    stop_tracking,
)

pytestmark = pytest.mark.slow


@pytest.mark.parametrize("mode", ["start", "break", "end", "continue"])
def test_set_toggl_pomodoro(mode):
    """Set a Pomodoro."""
    set_toggl_pomodoro(mode)


def test_delete_tracking():
    """Tracking is deleted."""
    delete_tracking()


def test_stop_tracking():
    """Tracking is stopped."""
    stop_tracking()
