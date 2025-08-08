"""Hasty implementation of Glyph's Pomodouroboros.

https://github.com/glyph/Pomodouroboros

Kid: I want Pomodouroboros, but it doesn't support Windows!
Parent: We have Pomodouroboros at home!
Pomodouroboros at home...
"""

import json
from collections.abc import Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime, time, timedelta
from json import loads
from pathlib import Path
from re import MULTILINE, finditer
from time import sleep
from typing import Any, Literal, TypeAlias
from winsound import MB_ICONEXCLAMATION, MB_OK

import win32api
from cappa.base import invoke
from sqlalchemy import Engine, create_engine
from sqlmodel import Session, select
from win32api import mouse_event
from win32con import MB_SYSTEMMODAL, MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP

from notes import toggl
from notes.cli import Pom
from notes.times import current_tz

# ? Should match Toggl's Pomodoro settings
WORK_PERIOD = timedelta(hours=1)
BREAK_PERIOD = timedelta(minutes=30)


def main(pom: Pom) -> None:  # noqa: C901, PLR0912
    """Start Pomodoros."""
    day_start = get_time_today(pom.begin)
    day_end = get_time_today(pom.end)
    starts = [
        day_start + period
        for period in split_period(day_end - day_start, WORK_PERIOD)
        if day_start + period < day_end
    ]
    if not starts:
        print(DONE_MSG)  # noqa: T201
        return
    print(get_startup_message(starts))  # noqa: T201
    if (time_until_start := starts[0] - get_now()) > timedelta(0):
        print(EARLY_MSG)  # noqa: T201
        try:
            sleep(time_until_start.total_seconds())
        except KeyboardInterrupt:
            print(DONE_MSG)  # noqa: T201
            return
    mode = "start"
    for pom_idx, start in enumerate(starts):
        print(START_MSG)  # noqa: T201
        if pom.data:
            record_period(pom.data, start, end=start, distractions=0)
        set_toggl_pomodoro(mode)
        mode = "continue"
        break_period = BREAK_PERIOD + GRACE_PERIOD
        distractions = 0
        try:
            if pom.event_data:
                distractions = sleep_check_distractions(
                    pom.event_data,
                    allowed=pom.allow,
                    period=WORK_PERIOD,
                    interval=CHECK_INTERVAL,
                )
            else:
                sleep(WORK_PERIOD.total_seconds())
        except KeyboardInterrupt:
            print(EARLY_BREAK_MSG)  # noqa: T201
            if get_pom_time_elapsed(start) < GRACE_PERIOD:
                print(SYNC_MSG)  # noqa: T201
                sleep(GRACE_PERIOD.total_seconds())
            break_period += WORK_PERIOD - get_pom_time_elapsed(start)
            stop_tracking()
        if pom.data:
            record_period(pom.data, start, end=get_now(), distractions=distractions)
        if _last_pom := (pom_idx + 1 >= (_pom_count := len(starts))):
            break
        try:
            print(get_break_msg(break_period))  # noqa: T201
            sleep(break_period.total_seconds())
        except KeyboardInterrupt:
            break
    print(DONE_MSG)  # noqa: T201
    if mode != "start":
        set_toggl_pomodoro("end")


EARLY_MSG = "Waiting for the first Pomodoro to begin..."
START_MSG = f"Please set an intent and focus for {WORK_PERIOD.total_seconds() // 60:.0f} minutes."
GRACE_PERIOD = timedelta(seconds=5)
"""Wait a little after break ends to ensure auto-Pomodoro is in focus mode."""
CHECK_INTERVAL = timedelta(minutes=1)
EARLY_BREAK_MSG = "Taking early break..."
SYNC_MSG = "Waiting for Toggl web app activity to sync with desktop app..."
DONE_MSG = "Done for the day!"


def sleep_check_distractions(
    path: Path, allowed: Sequence[str], period: timedelta, interval: timedelta
) -> int:
    """Sleep for a duration, checking periodically for distractions."""
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    distractions = 0
    allowed = [a.casefold() for a in allowed]
    for p in split_period(period, interval):
        now = get_now()
        sleep(p.total_seconds())
        events = get_events(engine, start=now, end=(now := get_now()))
        if any(event.path.stem.casefold() not in allowed for event in events):
            distractions += 1
            win32api.MessageBox(
                *MessageBox(
                    0, INTENT_MSG, APP_NAME, MB_SYSTEMMODAL | MB_ICONEXCLAMATION
                ).args()
            )
    return distractions


APP_NAME = "Pomodouroboros at Home"
INTENT_MSG = "Please focus on your intent."


@dataclass
class Event:
    """Event model."""

    id: int
    path: Path
    title: str
    start: datetime
    end: datetime


def get_events(engine: Engine, start: datetime, end: datetime) -> Sequence[Event]:
    """Get events."""
    with Session(engine) as session:
        start_ms_timestamp = 1000 * start.timestamp()
        end_ms_timestamp = 1000 * end.timestamp()
        events = session.exec(
            select(toggl.Event)
            .where(start_ms_timestamp < toggl.Event.end)
            .where(toggl.Event.end < end_ms_timestamp)
        ).all()
        return [
            Event(
                id=event.id,
                path=Path(event.path),
                title=event.title,
                start=get_ms_timestamp(event.start),
                end=get_ms_timestamp(event.end),
            )
            for event in events
            if event.id
        ]


def split_period(period: timedelta, interval: timedelta) -> list[timedelta]:
    """Fit as many intervals into period as possible, with the final interval as the remainder."""
    total_duration = period.total_seconds()
    (sleep_count, remainder) = divmod(total_duration, interval.total_seconds())
    return [
        *([interval] * int(sleep_count)),
        *([timedelta(seconds=remainder)] if remainder else []),
    ]


def get_startup_message(starts: list[datetime]) -> str:
    """Get startup message."""
    readable = [start.astimezone(current_tz).strftime("%H:%M") for start in starts]
    if len(readable) == 1:
        return f"Today's only Pomodoro will begin at {readable[0]}."
    if len(readable) == 2:
        return f"Today's Pomodoros will begin at {readable[0]} and {readable[1]}."
    return f"Today's Pomodoros will begin at {', '.join(readable[:-1])}, and {readable[-1]}."


def record_period(
    data: Path, start: datetime, end: datetime | None = None, distractions: int = 0
) -> None:
    """Record period."""
    if not data.exists():
        data.write_text(encoding="utf-8", data=dumps())
    data.write_text(
        encoding="utf-8",
        data=dumps({
            **loads(data.read_text(encoding="utf-8")),
            ser_datetime(start): {
                "end": ser_datetime(end or start),
                "distractions": distractions,
            },
        })
        + "\n",
    )


def dumps(obj: dict[str, Any] | None = None) -> str:
    """Dump JSON data."""
    return json.dumps(ensure_ascii=False, sort_keys=True, indent=2, obj=obj or {})


Mode: TypeAlias = Literal["start", "break", "end", "continue"]


def set_toggl_pomodoro(mode: Mode) -> None:
    """Set Toggl Pomodoro."""
    if mode == "continue":
        return
    desktop_centered_button_x = 316 if streaming() else -1560
    desktop_upper_button_y = 545 if streaming() else 445
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


def stop_tracking() -> None:
    """Stop tracking in Toggl web app."""
    # ? Toggl Track app at 80% zoom
    web_button_x = 1205 if streaming() else -1265
    web_button_y = 185 if streaming() else 720
    click_mouse(web_button_x, web_button_y)


def get_break_msg(period: timedelta) -> str:
    """Get break message."""
    return f"Please take a break for {period.total_seconds() // 60:.0f} minutes!"


def get_now() -> datetime:
    """Get current `datetime` in UTC."""
    return datetime.now(UTC)


def get_time_today(value: time) -> datetime:
    """Get `datetime` for today in UTC."""
    return datetime.combine(date.today(), value, tzinfo=current_tz).astimezone(UTC)


def get_ms_timestamp(value: float) -> datetime:
    """Get time for milliseconds timestamp."""
    return datetime.fromtimestamp(value / 1000, tz=current_tz)


def ser_datetime(value: datetime) -> str:
    """Serialize datetime."""
    return value.astimezone(current_tz).isoformat(timespec="seconds")


def delete_tracking() -> None:
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
    connections = {
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
    connect_count = sum(connections.values())
    disconnect_count = len(connections) - connect_count
    return disconnect_count != connect_count


def click_mouse(x: int, y: int, count: int = 1) -> None:
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
class MessageBox(Args):
    """`MessageBox` parameters to display modal dialogs ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-messagebox
    """

    hwnd: int | None = None
    """Window handle ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-messagebox#:~:text=%5Bin%2C%20optional%5D%20hWnd
    """
    message: str = ""
    """Message to be displayed ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-messagebox#:~:text=%5Bin%2C%20optional%5D%20lpText
    """
    title: str | None = None
    """Dialog box title ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-messagebox#:~:text=%5Bin%2C%20optional%5D%20lpCaption
    """
    style: int = MB_OK
    """Dialog box style ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-messagebox#:~:text=is%20Error.-,%5Bin%5D%20uType,-Type%3A%20UINT
    """


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

    def args(self) -> tuple[Any, ...]:  # pyright: ignore[reportIncompatibleMethodOverride]
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
    invoke(Pom)
