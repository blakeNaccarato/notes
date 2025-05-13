"""Hasty implementation of Glyph's Pomodouroboros.

https://github.com/glyph/Pomodouroboros

Kid: I want Pomodouroboros, but it doesn't support Windows!
Parent: We have Pomodouroboros at home!
Pomodouroboros at home...
"""

import json
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime, time, timedelta
from json import loads
from pathlib import Path
from time import sleep
from typing import Any, Literal, TypeAlias

import win32api
from win32api import mouse_event
from win32con import MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP

from notes.times import current_tz

DATA = Path("data/local/vaults/personal/_data/pomodouroboros.json")
DAY_BEGIN = datetime.combine(date.today(), time(hour=9, tzinfo=current_tz))
DAY_END = datetime.combine(date.today(), time(hour=17, tzinfo=current_tz))
# ? Should match Toggl's Pomodoro settings
WORK_PERIOD = timedelta(hours=1, minutes=10)
BREAK_PERIOD = timedelta(minutes=20)


def main():  # noqa: D103
    if get_now() + WORK_PERIOD > DAY_END:
        print(DONE_MSG)  # noqa: T201
        return
    if (time_until_day_begin := DAY_BEGIN - get_now()) > timedelta(0):
        print(STARTUP_MSG)  # noqa: T201
        try:
            sleep(time_until_day_begin.total_seconds())
        except KeyboardInterrupt:
            print(DONE_MSG)  # noqa: T201
            return
    mode = "start"
    begin = get_now() - POM_PERIOD
    while (begin := begin + POM_PERIOD) + WORK_PERIOD < DAY_END:
        print(BEGIN_MSG)  # noqa: T201
        record_period(begin, begin)
        set_toggl_pomodoro(mode)
        mode = "continue"
        break_period = BREAK_PERIOD + BREAK_OFFSET
        try:
            sleep(WORK_PERIOD.total_seconds())
        except KeyboardInterrupt:
            print(EARLY_BREAK_MSG)  # noqa: T201
            if get_pom_time_elapsed(begin) < (grace_period := timedelta(seconds=5)):
                print(SYNC_MSG)  # noqa: T201
                sleep(grace_period.total_seconds())
            break_period += WORK_PERIOD - get_pom_time_elapsed(begin)
            stop_tracking()
        print(get_break_msg(break_period))  # noqa: T201
        record_period(begin, get_now())
        try:
            sleep(break_period.total_seconds())
        except KeyboardInterrupt:
            break
    print(DONE_MSG)  # noqa: T201
    if mode != "start":
        set_toggl_pomodoro("end")


def get_pom_time_elapsed(begin: datetime) -> timedelta:
    """Get time elapsed since Pomodoro began."""
    return get_now() - begin


POM_PERIOD = WORK_PERIOD + BREAK_PERIOD
BREAK_OFFSET = timedelta(seconds=5)
"""Wait a little after break ends to ensure auto-Pomodoro is in focus mode."""
STARTUP_MSG = f"The first Pomodoro begins at {DAY_BEGIN.strftime('%H:%M')}."
BEGIN_MSG = f"Please set an intent and focus for {WORK_PERIOD.total_seconds() // 60:.0f} minutes."
EARLY_BREAK_MSG = "Taking early break..."
SYNC_MSG = "Waiting for Toggl web app activity to sync with desktop app..."
DONE_MSG = "Done for the day!"


def get_break_msg(period: timedelta) -> str:
    """Get break message."""
    return f"Please take a break for {period.total_seconds() // 60:.0f} minutes!"


def record_period(start: datetime, end: datetime | None = None):
    """Record period."""
    if not DATA.exists():
        DATA.write_text(encoding="utf-8", data=dumps())
    DATA.write_text(
        encoding="utf-8",
        data=dumps({
            **loads(DATA.read_text(encoding="utf-8")),
            ser_datetime(start): ser_datetime(end or start),
        })
        + "\n",
    )


def ser_datetime(value: datetime):
    """Serialize datetime."""
    return value.astimezone(current_tz).isoformat(timespec="seconds")


Mode: TypeAlias = Literal["start", "break", "end", "continue"]


def set_toggl_pomodoro(mode: Mode):
    """Set Toggl Pomodoro."""
    if mode == "continue":
        return
    click_mouse(*TOGGL_DESKTOP_STATE_TRANSITIONS[mode], count=2)
    if mode == "start":
        return
    sleep(SLEEP)
    click_mouse(*TOGGL_DESKTOP_CONFIRM)


TOGGL_DESKTOP_CENTERED_BUTTON_X = -1560
TOGGL_DESKTOP_UPPER_BUTTON_Y = 445
TOGGL_DESKTOP_STATE_TRANSITIONS = {
    "continue": None,
    "start": (TOGGL_DESKTOP_CENTERED_BUTTON_X, TOGGL_DESKTOP_UPPER_BUTTON_Y),
    "break": (TOGGL_DESKTOP_CENTERED_BUTTON_X, TOGGL_DESKTOP_UPPER_BUTTON_Y),
    "end": (TOGGL_DESKTOP_CENTERED_BUTTON_X, 480),
}
TOGGL_DESKTOP_CONFIRM = (-1640, 335)


def stop_tracking():
    """Stop tracking in Toggl web app."""
    click_mouse(*TOGGL_WEB_STOP_TRACKING)


def delete_tracking():
    """Delete the currently tracking activity in Toggl web app."""
    click_mouse(*TOGGL_WEB_MORE_OPTIONS)
    sleep(SLEEP)
    click_mouse(*TOGGL_WEB_DELETE_CURRENT)


TOGGL_WEB_BUTTON_Y = 745
TOGGL_WEB_STOP_TRACKING = (-1285, TOGGL_WEB_BUTTON_Y)
TOGGL_WEB_MORE_OPTIONS = (-1230, TOGGL_WEB_BUTTON_Y)
TOGGL_WEB_DELETE_CURRENT = (-1308, 844)

SLEEP = 0.5


def click_mouse(x: int, y: int, count: int = 1):
    """Click mouse."""
    for _ in range(count):
        set_mouse(x, y, down=True)
        set_mouse(x, y, down=False)


def set_mouse(x: int, y: int, down: bool = True):
    """Set mouse position and left click state."""
    win32api.SetCursorPos(*SetCursorPos(x, y).args())
    mouse_event(
        *MouseEvent(
            dw_flags=MOUSEEVENTF_LEFTDOWN if down else MOUSEEVENTF_LEFTUP
        ).args()
    )


def dumps(obj: dict[str, Any] | None = None) -> str:
    """Dump JSON data."""
    return json.dumps(ensure_ascii=False, sort_keys=True, indent=2, obj=obj or {})


def get_now() -> datetime:
    """Get current `datetime` in UTC."""
    return datetime.now(UTC)


@dataclass
class Args:
    """Supplies `args` method to unpack values as args to functions with positional-only parameters."""

    def args(self):
        """Get args."""
        return asdict(self).values()


@dataclass
class SetCursorPos(Args):
    """`SetCursorPosition` parameters to move the cursor ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setcursorpos
    """

    x: int = 0
    """Cursor x-position ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setcursorpos#:~:text=%5Bin%5D%20x
    """
    y: int = 0
    """Cursor y-position ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setcursorpos#:~:text=%5Bin%5D%20y
    """

    def args(self):
        """Get args. `pywin32` API expects `SetCursorPos` args as (`x`, `y`) tuple."""
        return (tuple(super().args()),)


@dataclass
class MouseEvent(Args):
    """`mouse_event` parameters to move and click the mouse ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-mouse_event
    """

    dw_flags: int = 0
    """Controls mouse motion and clicking ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-mouse_event#:~:text=%5Bin%5D%20dwFlags
    """
    dx: int = 0
    """Cursor x-position, relative or absolute depending on `dw_flags` ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-mouse_event#:~:text=%5Bin%5D%20dx
    """
    dy: int = 0
    """Cursor y-position, relative or absolute depending on `dw_flags` ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-mouse_event#:~:text=%5Bin%5D%20dy
    """
    dw_data: int = 0
    """Wheel and X button actions ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-mouse_event#:~:text=%5Bin%5D%20dwData
    """
    dw_extra_info: int = 0
    """Additional info associated with the event ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-mouse_event#:~:text=%5Bin%5D%20dwExtraInfo
    """


if __name__ == "__main__":
    main()
