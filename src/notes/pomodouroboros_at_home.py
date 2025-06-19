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
from re import MULTILINE, finditer
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
WORK_PERIOD = timedelta(hours=1)
BREAK_PERIOD = timedelta(minutes=30)


def main():  # noqa: D103
    beginnings = get_pomodoro_periods()
    if not beginnings:
        print(DONE_MSG)  # noqa: T201
        return
    if (time_until_day_begin := beginnings[0] - get_now()) > timedelta(0):
        print(EARLY_MSG)  # noqa: T201
        try:
            sleep(time_until_day_begin.total_seconds())
        except KeyboardInterrupt:
            print(DONE_MSG)  # noqa: T201
            return
    mode = "start"
    print(get_startup_message(beginnings))  # noqa: T201
    for pom_idx, begin in enumerate(beginnings):
        print(BEGIN_MSG)  # noqa: T201
        record_period(begin, begin)
        set_toggl_pomodoro(mode)
        mode = "continue"
        break_period = BREAK_PERIOD + GRACE_PERIOD
        try:
            sleep(WORK_PERIOD.total_seconds())
        except KeyboardInterrupt:
            print(EARLY_BREAK_MSG)  # noqa: T201
            if get_pom_time_elapsed(begin) < GRACE_PERIOD:
                print(SYNC_MSG)  # noqa: T201
                sleep(GRACE_PERIOD.total_seconds())
            break_period += WORK_PERIOD - get_pom_time_elapsed(begin)
            stop_tracking()
        record_period(begin, get_now())
        if _last_pom := (pom_idx + 1 >= (_pom_count := len(beginnings))):
            break
        try:
            print(get_break_msg(break_period))  # noqa: T201
            sleep(break_period.total_seconds())
        except KeyboardInterrupt:
            break
    print(DONE_MSG)  # noqa: T201
    if mode != "start":
        set_toggl_pomodoro("end")


GRACE_PERIOD = timedelta(seconds=5)
"""Wait a little after break ends to ensure auto-Pomodoro is in focus mode."""
EARLY_MSG = f"The first Pomodoro begins at {DAY_BEGIN.strftime('%H:%M')}."
BEGIN_MSG = f"Please set an intent and focus for {WORK_PERIOD.total_seconds() // 60:.0f} minutes."
EARLY_BREAK_MSG = "Taking early break..."
SYNC_MSG = "Waiting for Toggl web app activity to sync with desktop app..."
DONE_MSG = "Done for the day!"


def get_pomodoro_periods() -> list[datetime]:
    """Get Pomodoro periods for today."""
    begin = None
    beginnings: list[datetime] = []
    while (begin := begin + POM_PERIOD if begin else get_now()) + WORK_PERIOD < DAY_END:
        beginnings.append(begin)
    return beginnings


POM_PERIOD = WORK_PERIOD + BREAK_PERIOD


def get_startup_message(beginnings: list[datetime]) -> str:
    """Get startup message."""
    readable = [begin.astimezone(current_tz).strftime("%H:%M") for begin in beginnings]
    if len(readable) == 1:
        return f"Today's only Pomodoro will begin at {readable[0]}."
    return f"Today's Pomodoros will begin at {', '.join(readable[:-1])}, and {readable[-1]}."


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


def dumps(obj: dict[str, Any] | None = None) -> str:
    """Dump JSON data."""
    return json.dumps(ensure_ascii=False, sort_keys=True, indent=2, obj=obj or {})


Mode: TypeAlias = Literal["start", "break", "end", "continue"]


def set_toggl_pomodoro(mode: Mode):
    """Set Toggl Pomodoro."""
    desktop_centered_button_x = 316 if streaming() else -1560
    desktop_upper_button_y = 545 if streaming() else 445
    if mode == "continue":
        return
    click_mouse(
        *{  # pyright: ignore[reportArgumentType]
            "start": (desktop_centered_button_x, desktop_upper_button_y),
            "break": (desktop_centered_button_x, desktop_upper_button_y),
            "end": (desktop_centered_button_x, 598 if streaming() else 480),
        }[mode],
        count=2,
    )
    if mode == "start":
        return
    sleep(SLEEP)
    desktop_confirm = (204, 402) if streaming() else (-1640, 335)
    click_mouse(*desktop_confirm)


def get_pom_time_elapsed(begin: datetime) -> timedelta:
    """Get time elapsed since Pomodoro began."""
    return get_now() - begin


def get_now() -> datetime:
    """Get current `datetime` in UTC."""
    return datetime.now(UTC)


def stop_tracking():
    """Stop tracking in Toggl web app."""
    web_button_y = 185 if streaming() else 720
    web_stop_tracking = (1205, web_button_y) if streaming() else (-1265, web_button_y)
    click_mouse(*web_stop_tracking)


def get_break_msg(period: timedelta) -> str:
    """Get break message."""
    return f"Please take a break for {period.total_seconds() // 60:.0f} minutes!"


def ser_datetime(value: datetime):
    """Serialize datetime."""
    return value.astimezone(current_tz).isoformat(timespec="seconds")


def delete_tracking():
    """Delete the currently tracking activity in Toggl web app."""
    web_button_y = 185 if streaming() else 720
    web_more_options = (1250, web_button_y) if streaming() else (-1225, web_button_y)
    click_mouse(*web_more_options)
    sleep(SLEEP)
    web_delete_current = (1183, 291) if streaming() else (-1287, 799)
    click_mouse(*web_delete_current)


SLEEP = 0.5


def streaming() -> bool:
    """Check whether Sunshine streaming is active."""
    connetions = {
        datetime.strptime(m["at"], "%Y-%m-%d %H:%M:%S.%f"): (
            m["event"].casefold() == "connected"
        )
        for m in finditer(
            pattern=r"^\[(?P<at>[^\]]+)\]: Info: CLIENT (?P<event>(?:DIS)?CONNECTED)$",
            string=Path("C:/Program Files/Sunshine/config/sunshine.log").read_text(
                encoding="utf-8"
            ),
            flags=MULTILINE,
        )
    }
    connect_count = sum(connetions.values())
    disconnect_count = len(connetions) - connect_count
    return disconnect_count != connect_count


def click_mouse(x: int, y: int, count: int = 1):
    """Click mouse."""
    original_cursor_pos = win32api.GetCursorPos()
    win32api.SetCursorPos(*SetCursorPos(x, y).args())
    for _ in range(count):
        mouse_event(*MouseEvent(dw_flags=MOUSEEVENTF_LEFTDOWN).args())
        mouse_event(*MouseEvent(dw_flags=MOUSEEVENTF_LEFTUP).args())
    win32api.SetCursorPos(*SetCursorPos(*original_cursor_pos).args())


@dataclass
class Args:
    """Supplies `args` method to unpack values as args to functions with positional-only parameters."""

    def args(self) -> tuple[Any, ...]:
        """Get args."""
        return tuple(asdict(self).values())


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
        return (super().args(),)


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
