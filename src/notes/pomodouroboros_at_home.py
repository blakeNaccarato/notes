"""Hasty implementation of Glyph's Pomodouroboros.

https://github.com/glyph/Pomodouroboros

Kid: I want Pomodouroboros, but it doesn't support Windows!
Parent: We have Pomodouroboros at home!
Pomodouroboros at home...
"""

import json
from collections.abc import Iterable, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime, time, timedelta
from itertools import accumulate
from json import loads
from pathlib import Path
from re import MULTILINE, finditer
from time import sleep
from typing import Any, Literal, TypeAlias

import win32api
from cappa.base import invoke
from sqlalchemy import create_engine
from sqlmodel import Session, select
from win32api import mouse_event
from win32con import (
    IDYES,
    MB_OK,
    MB_SYSTEMMODAL,
    MB_YESNO,
    MOUSEEVENTF_LEFTDOWN,
    MOUSEEVENTF_LEFTUP,
)

from notes import toggl
from notes.cli import Pom
from notes.times import current_tz

# ? Should match Toggl's Pomodoro settings
WORK_PERIOD = timedelta(hours=1)
BREAK_PERIOD = timedelta(minutes=30)


def main(pom: Pom) -> None:  # sourcery skip: low-code-quality  # noqa: C901, PLR0912
    """Start Pomodoros."""
    day_start = max(get_time_today(pom.begin), get_now())
    day_end = get_time_today(pom.end)
    poms = list(time_range(day_start, day_end, WORK_PERIOD + BREAK_PERIOD))
    if poms and poms[-1] + WORK_PERIOD > day_end:
        poms = poms[:-1]
    if not poms:
        print(DONE_MSG)  # noqa: T201
        return
    print(get_startup_message(poms))  # noqa: T201
    for start in poms:
        if (time_until_start := start - get_now()) > timedelta(0):
            print(EARLY_MSG)  # noqa: T201
            try:
                sleep(time_until_start.total_seconds())
            except KeyboardInterrupt:
                print(DONE_MSG)  # noqa: T201
                return
        intent = get_intent(pom.intents)
        interrupted = False
        distractions = 0
        checks = time_range(start, start + WORK_PERIOD, CHECK_PERIOD)
        last_check = start
        record_period(pom.poms, intent, start, end=start, distractions=distractions)
        print(START_MSG)  # noqa: T201
        set_toggl_pomodoro("start")
        for check in checks:
            done = False
            if (check_period := check - get_now()) < timedelta(0):
                continue
            try:
                sleep(check_period.total_seconds())
            except KeyboardInterrupt:
                interrupted = True
                break
            if (
                not done
                and pom.events
                and (events := get_events(pom.events, start=last_check, end=check))
                and any(
                    allowed.casefold()
                    not in f"{event.path.stem.casefold()} - {event.title.casefold()}"
                    for allowed in get_allowed(pom.intents, intent)
                    for event in events
                )
            ):
                distractions += 1
                if done := (
                    win32api.MessageBox(
                        *MessageBox(
                            0, INTENT_MSG, APP_NAME, MB_SYSTEMMODAL | MB_YESNO
                        ).args()
                    )
                    == IDYES
                ):
                    print(COMPLETED_INTENT_MSG)  # noqa: T201
            last_check = check
        record_period(pom.poms, intent, start, end=get_now(), distractions=distractions)
        if interrupted:
            break
        try:
            if (time_until_end := (start + WORK_PERIOD) - get_now()) > timedelta(0):
                sleep(time_until_end.total_seconds())
            record_period(
                pom.poms, intent, start, end=get_now(), distractions=distractions
            )
            print(get_break_msg(BREAK_PERIOD))  # noqa: T201
            sleep(BREAK_PERIOD.total_seconds())
        except KeyboardInterrupt:
            break
    print(DONE_MSG)  # noqa: T201
    set_toggl_pomodoro("end")


EARLY_MSG = "Waiting for Pomodoro to begin..."
START_MSG = "Pomodoro has begun."
DONE_MSG = "Done for the day!"
APP_NAME = "Pomodouroboros at Home"
INTENT_MSG = "Have you completed your intent?"
COMPLETED_INTENT_MSG = "Congratulations on completing your intent!"
CHECK_PERIOD = timedelta(minutes=1)


def get_intent(intents: Path) -> str:
    """Get intent."""
    while not (
        intent := get_intents(intents)[
            int(
                input(
                    "\n".join([
                        INTENT_PROMPT,
                        *[f"  {i}. {v}" for i, v in enumerate(get_intents(intents))],
                    ])
                    + "\nEnter a number: "
                )
            )
        ]
    ) and not get_allowed(intents, intent):
        pass
    return intent


INTENT_PROMPT = "Please select your intent for this Pomodoro."


def get_allowed(path: Path, intent: str) -> list[str]:
    """Get intent."""
    return (loads(path.read_text(encoding="utf-8")).get(intent) or {}).get(
        "allowed"
    ) or []


def get_intents(path: Path) -> list[str]:
    """Get intents."""
    return list(loads(path.read_text(encoding="utf-8")))


def merge_allowed(
    intents: dict[str, dict[str, Sequence[str]]], name: str, allowed: Sequence[str]
) -> list[str]:
    """Get allowed activities."""
    return list(
        dict.fromkeys([*intent["allowed"], *allowed])
        if (intent := intents.get(name))
        else allowed
    )


@dataclass
class Event:
    """Event model."""

    id: int
    path: Path
    title: str
    start: datetime
    end: datetime


def get_events(path: Path, start: datetime, end: datetime) -> Sequence[Event]:
    """Get events."""
    with Session(create_engine(f"sqlite:///{path.as_posix()}")) as session:
        return [
            Event(
                id=event.id,
                path=Path(event.path),
                title=event.title,
                start=get_ms_timestamp(event.start),
                end=get_ms_timestamp(event.end),
            )
            for event in session.exec(
                select(toggl.Event)
                .where(toggl.Event.end > SECONDS_TO_MILLISECONDS * start.timestamp())
                .where(toggl.Event.end < SECONDS_TO_MILLISECONDS * end.timestamp())
            ).all()
            if event.id
        ]


SECONDS_TO_MILLISECONDS = 1000


def time_range(start: datetime, stop: datetime, step: timedelta) -> Iterable[datetime]:
    """Get a range of times."""
    yield from (
        start,
        *[
            start + period
            for period in accumulate(
                [step] * int((stop - start).total_seconds() / step.total_seconds())
            )
        ],
    )


def get_startup_message(starts: list[datetime]) -> str:
    """Get startup message."""
    readable = [start.astimezone(current_tz).strftime("%H:%M") for start in starts]
    if len(readable) == 1:
        return f"Today's only Pomodoro will begin at {readable[0]}."
    if len(readable) == 2:
        return f"Today's Pomodoros will begin at {readable[0]} and {readable[1]}."
    return f"Today's Pomodoros will begin at {', '.join(readable[:-1])}, and {readable[-1]}."


def record_period(
    data: Path,
    intent: str,
    start: datetime,
    end: datetime | None = None,
    distractions: int = 0,
) -> None:
    """Record period."""
    data.write_text(
        encoding="utf-8",
        data=dumps({
            **loads(data.read_text(encoding="utf-8")),
            ser_datetime(start): {
                "end": ser_datetime(end or start),
                "intent": intent,
                "distractions": distractions,
            },
        })
        + "\n",
    )


def dumps(obj: dict[str, Any] | None = None) -> str:
    """Dump JSON data."""
    return json.dumps(ensure_ascii=False, sort_keys=True, indent=2, obj=obj or {})


Mode: TypeAlias = Literal["start", "end"]


def set_toggl_pomodoro(mode: Mode) -> None:
    """Set Toggl Pomodoro."""
    desktop_centered_button_x = 316 if streaming() else -1560
    desktop_upper_button_y = 545 if streaming() else 445
    click_mouse(
        *{  # pyright: ignore[reportArgumentType]
            "start": (desktop_centered_button_x, desktop_upper_button_y),
            "end": (desktop_centered_button_x, 598 if streaming() else 480),
        }[mode],
        count=2,
    )
    if mode == "start":
        return
    sleep(SHORT_SLEEP)
    desktop_confirm = (204, 402) if streaming() else (-1640, 335)
    click_mouse(*desktop_confirm)
    # ? Stop tracking in Toggl web app. Toggl Track app at 80% zoom
    sleep(SHORT_SLEEP)
    web_button_x = 1205 if streaming() else -1265
    web_button_y = 185 if streaming() else 720
    click_mouse(web_button_x, web_button_y)


SHORT_SLEEP = 0.5


def get_pom_time_elapsed(begin: datetime) -> timedelta:
    """Get time elapsed since Pomodoro began."""
    return get_now() - begin


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
