"""Hasty implementation of Glyph's Pomodouroboros.

https://github.com/glyph/Pomodouroboros

Kid: I want Pomodouroboros, but it doesn't support Windows!
Parent: We have Pomodouroboros at home!
Pomodouroboros at home...
"""

from __future__ import annotations

import json
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import asdict, dataclass
from datetime import UTC, date, datetime, time, timedelta
from itertools import accumulate
from json import loads
from pathlib import Path
from re import MULTILINE, finditer
from time import sleep
from typing import Any, Literal, TypeAlias, TypeVar

import win32api
from cappa.base import invoke
from more_itertools import first, last, one
from sqlmodel import Session, col, create_engine, select
from win32api import mouse_event
from win32con import (
    IDYES,
    MB_DEFBUTTON2,
    MB_OK,
    MB_SYSTEMMODAL,
    MB_YESNO,
    MOUSEEVENTF_LEFTDOWN,
    MOUSEEVENTF_LEFTUP,
)

from notes import toggl
from notes.cli import Pom
from notes.times import current_tz


def main(  # sourcery skip: low-code-quality  # noqa: C901, PLR0912, PLR0915
    pom: Pom,
) -> None:
    """Start Pomodoros."""
    periods = get_periods(pom.toggl)
    work_period = periods.work
    break_period = periods.brk
    pom_period = work_period + periods.brk
    day_start = max(get_time_today(pom.start), get_now())
    day_end = get_time_today(pom.end)
    if not (poms := list(time_range(day_start, day_end + break_period, pom_period))):
        split_intents(pom.intents)
        print(DONE_MSG)  # noqa: T201
        return
    print(get_startup_message(poms))  # noqa: T201
    if day_start > get_now():
        print(EARLY_MSG)  # noqa: T201
        try:
            sleep((day_start - get_now()).total_seconds())
        except KeyboardInterrupt:
            split_intents(pom.intents)
            print(DONE_MSG)  # noqa: T201
            return
    set_toggl_pomodoro("start")
    for start in poms:  # noqa: PLR1702
        cancel = interrupted = False
        distracted = True
        intent = ""
        intent_set = done = None
        focused = (now := get_now()) - start
        checked_focus = checked_events = now
        record_period(
            data=pom.poms,
            done=done,
            end=now,
            focused=focused,
            intent_set=intent_set,
            intent=intent,
            start=start,
        )
        print(START_MSG)  # noqa: T201
        while start + work_period > get_now():
            try:
                sleep(CHECK_PERIOD.total_seconds())
            except KeyboardInterrupt:
                interrupted = True
                if prompt(ASK_CANCEL):
                    cancel = True
                    break
            if done:
                continue
            if not intent_set and start + SETTABLE_INTENT_PERIOD < get_now():
                while (
                    not (intent := get_intent(pom.toggl))
                    or intent == NO_INTENT
                    or not prompt(ask_intent(intent))
                ):
                    notify(SET_INTENT_MSG)
                    try:
                        sleep(SET_INTENT_SLEEP)
                    except KeyboardInterrupt:
                        if prompt(ASK_CANCEL):
                            cancel = True
                        intent = NO_INTENT
                        print(DID_NOT_SET_INTENT_MSG)  # noqa: T201
                        break
                if cancel:
                    break
                if intent and intent != NO_INTENT:
                    intents = set_intent(pom.intents, intent)
                    print(DID_SET_INTENT_MSG)  # noqa: T201
                intent_set = get_now()
                continue
            if (
                not intent_set
                and (intent := get_intent(pom.toggl))
                and intent != NO_INTENT
                and prompt(ask_intent(intent))
            ):
                intents = set_intent(pom.intents, intent)
                intent_set = get_now()
                print(DID_SET_INTENT_MSG)  # noqa: T201
                continue
            if not intent_set or not intent or intent == NO_INTENT:
                checked_focus = now
                continue
            now = get_now()
            events = get_events(pom.toggl, start=checked_events, end=now)
            checked_events = now
            if not events:
                continue
            intents = get_intents(pom.intents)
            new_related: list[str] = []
            new_unrelated: list[str] = []
            distracted = False
            for event in events:
                window = f"{event.path.stem} - {event.title}"
                if check_window(window, intents[intent]["related"]):
                    continue
                if check_window(window, intents[intent]["unrelated"]):
                    distracted = True
                    continue
                if prompt(ask_related(window, intent)):
                    new_related.append(window)
                else:
                    new_unrelated.append(window)
                    distracted = True
            if new_related or new_unrelated:
                set_intents(
                    pom.intents,
                    merge_intents(
                        intents,
                        {intent: {"related": new_related, "unrelated": new_unrelated}},
                    ),
                )
            now = get_now()
            if (distracted or interrupted) and prompt(ask_done(intent)):
                print(COMPLETED_INTENT_MSG)  # noqa: T201
                done = now
            interrupted = False
            if distracted:
                print(FOCUS_MSG)  # noqa: T201
            else:
                focused += now - checked_focus
            checked_focus = now
            record_period(
                data=pom.poms,
                done=done,
                end=now,
                focused=focused,
                intent_set=intent_set,
                intent=intent,
                start=start,
            )
        now = get_now()
        if intent != NO_INTENT and not done and prompt(ask_done(intent)):
            print(COMPLETED_INTENT_MSG)  # noqa: T201
            done = now
        if intent != NO_INTENT:
            focused += now - checked_focus
        record_period(
            data=pom.poms,
            done=done,
            end=now,
            focused=focused,
            intent_set=intent_set,
            intent=intent,
            start=start,
        )
        if cancel:
            break
        while start + pom_period > get_now():
            print(get_break_msg(break_period := (start + pom_period) - get_now()))  # noqa: T201
            try:
                sleep(break_period.total_seconds())
            except KeyboardInterrupt:
                if prompt(ASK_CANCEL):
                    cancel = True
                    break
        if cancel:
            break
    set_toggl_pomodoro("stop")
    split_intents(pom.intents)
    print(DONE_MSG)  # noqa: T201


CHECK_PERIOD = timedelta(seconds=30)
SETTABLE_INTENT_PERIOD = timedelta(minutes=5)
SET_INTENT_SLEEP = 5

NO_INTENT = "No intent 🆔 2025-08-13T115432-0700"

DONE_MSG = "Done for the day!"
EARLY_MSG = "Waiting for first Pomodoro to begin..."
START_MSG = "Pomodoro has begun."
SET_INTENT_MSG = "Please set an intent."
DID_SET_INTENT_MSG = "Congratulations on setting your intent!"
DID_NOT_SET_INTENT_MSG = "No intent for this Pomodoro."
ASK_CANCEL = "A Pomodoro is in progress. Do you want to cancel it?"
UNRELATED_MSG = "Please focus on your intent."
COMPLETED_INTENT_MSG = "Congratulations on completing your intent!"
FOCUS_MSG = "Oops, I got distracted!"


def notify(message: str):
    """Notify user."""
    win32api.MessageBox(
        *MessageBox(0, message, APP_NAME, MB_SYSTEMMODAL | MB_OK).args()
    )


def prompt(message: str) -> bool:
    """Prompt user."""
    return (
        win32api.MessageBox(
            *MessageBox(
                0, message, APP_NAME, MB_SYSTEMMODAL | MB_YESNO | MB_DEFBUTTON2
            ).args()
        )
        == IDYES
    )


APP_NAME = "Pomodouroboros at Home"


def check_window(window: str, checks: list[str]) -> bool:
    """Check if window is related to intent."""
    return any(check.casefold() in window.casefold() for check in checks or {})


def split_intents(path: Path) -> dict[str, dict[Kind, list[str]]]:
    """Split compound intents, clearing related/unrelated events on split intents."""
    # TODO: Ask user which entries to split among intents
    set_intents(
        path,
        intents := merge_intents(
            (intents := get_intents(path)),
            {
                match.group(0).strip(): get_default_intent(match.group(0).strip())
                for name in intents
                for match in finditer(
                    pattern=rf"[^{get_sep(name)}]+🆔[^{get_sep(name)}]+",
                    string=name,
                    flags=MULTILINE,
                )
                if name.count("🆔") > 1
            },
        ),
    )
    return intents


def get_sep(name: str) -> str:
    """Get separator."""
    return ";" if ";" in name else ","


Kind: TypeAlias = Literal["related", "unrelated"]
KINDS: tuple[Kind, ...] = ("related", "unrelated")


def get_default_intent(intent: str) -> dict[Kind, list[str]]:
    """Get default intent."""
    return {
        "related": [
            intent,
            "database.sqlite",
            "intents.json",
            "Obsidian - Today",
            "pomodouroboros.json",
            "ShellExperienceHost",
            "TogglTrack",
            "WindowsTerminal - 🍅",
        ],
        "unrelated": [],
    }


def set_intent(path: Path, intent: str) -> dict[str, dict[Kind, list[str]]]:
    """Add intent to intents file."""
    return set_intents(
        path, merge_intents(get_intents(path), {intent: get_default_intent(intent)})
    )


def set_intents(
    path: Path, intents: dict[str, dict[Kind, list[str]]]
) -> dict[str, dict[Kind, list[str]]]:
    """Get intents."""
    path.write_text(encoding="utf-8", data=dumps(intents))
    return intents


def merge_intents(
    intents: Mapping[str, dict[Kind, list[str]]],
    other: Mapping[str, dict[Kind, list[str]]],
) -> dict[str, dict[Kind, list[str]]]:
    """Merge intents."""
    return {
        name: {
            key: list(
                ordered_union(
                    (intents.get(name) or get_default_intent(name))[key],
                    (other.get(name) or get_default_intent(name))[key],
                )
            )
            for key in KINDS
        }
        for name in ordered_union(intents, other)
    }


def get_intents(path: Path) -> dict[str, dict[Kind, list[str]]]:
    """Get intents."""
    return loads(path.read_text(encoding="utf-8"))


T = TypeVar("T")


def ordered_union(iterable: Iterable[T], other: Iterable[T]) -> Iterable[T]:
    """Get the ordered union of unique elements over two iterables."""
    yield from dict.fromkeys((*iterable, *other))


@dataclass
class Periods:
    """Periods."""

    work: timedelta
    brk: timedelta


def get_periods(path: Path) -> Periods:
    """Get periods."""
    with Session(create_engine(f"sqlite:///{path.as_posix()}")) as session:
        prefs = one(session.exec(select(toggl.Preferences)))
        return Periods(
            work=timedelta(minutes=prefs.pomodoro_focus_interval_in_minutes),
            brk=timedelta(minutes=prefs.pomodoro_break_interval_in_minutes),
        )


def get_intent(path: Path) -> str:
    """Get active intent."""
    with Session(create_engine(f"sqlite:///{path.as_posix()}")) as session:
        intent = first(
            session.exec(
                select(toggl.Entry)
                .where(col(toggl.Entry.duration).is_(None))
                .order_by(col(toggl.Entry.id).desc())
            ),
            None,
        )
    return intent.description if intent else ""


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
                path=Path(event.filename),
                title=event.title,
                start=get_ms_timestamp(event.start_time),
                end=get_ms_timestamp(event.end_time),
            )
            for event in session.exec(
                select(toggl.Event)
                .where(
                    toggl.Event.end_time > SECONDS_TO_MILLISECONDS * start.timestamp()
                )
                .where(toggl.Event.end_time < SECONDS_TO_MILLISECONDS * end.timestamp())
            ).all()
            if event.id
        ]


SECONDS_TO_MILLISECONDS = 1000


def time_range(start: datetime, stop: datetime, step: timedelta) -> Iterable[datetime]:
    """Get a range of times."""
    yield from (
        start + (period - step)
        for period in accumulate(
            [step] * int((stop - start).total_seconds() / step.total_seconds())
        )
    )


def get_startup_message(starts: list[datetime]) -> str:
    """Get startup message."""
    if not starts:
        return "No Pomodoros today."
    readable = [start.astimezone(current_tz).strftime("%H:%M") for start in starts]
    if len(readable) == 1:
        return f"Today's only Pomodoro will begin at {readable[0]}."
    if len(readable) == 2:
        return f"Today's Pomodoros will begin at {readable[0]} and {readable[1]}."
    return f"Today's Pomodoros will begin at {', '.join(readable[:-1])}, and {readable[-1]}."


def record_period(
    *,
    done: datetime | None,
    data: Path,
    focused: timedelta,
    end: datetime,
    intent: str,
    intent_set: datetime | None,
    start: datetime,
) -> None:
    """Record period."""
    data.write_text(
        encoding="utf-8",
        data=dumps({
            **loads(data.read_text(encoding="utf-8")),
            ser_datetime(start): {
                "done": ser_datetime(done) if done else None,
                "focused": focused / (end - start),
                "end": ser_datetime(end),
                "intent": intent,
                "intent_set": ser_datetime(intent_set) if intent_set else None,
            },
        })
        + "\n",
    )


def dumps(obj: dict[str, Any] | None = None, sort: bool = True) -> str:
    """Dump JSON data."""
    return json.dumps(ensure_ascii=False, sort_keys=sort, indent=2, obj=obj or {})


Mode: TypeAlias = Literal["start", "stop"]


def set_toggl_pomodoro(mode: Mode) -> None:
    """Set Toggl Pomodoro."""
    c = DISPLAYS[get_displays()]
    click_mouse(
        *{
            "start": (c["desktop_centered_button_x"], c["desktop_upper_button_y"]),
            "stop": (c["desktop_centered_button_x"], c["desktop_lower_button_y"]),
        }[mode],
        count=2,
    )
    if mode == "start":
        return
    desktop_confirm = (c["desktop_confirm_x"], c["desktop_confirm_y"])
    click_mouse(*desktop_confirm)


DISPLAYS: dict[tuple[tuple[int, int], ...], dict[str, int]] = {
    ((1920, 1334),): {
        "desktop_centered_button_x": 316,
        "desktop_upper_button_y": 545,
        "desktop_lower_button_y": 598,
        "desktop_confirm_x": 241,
        "desktop_confirm_y": 484,
    },
    ((1920, 1080),): {
        "desktop_centered_button_x": 316,
        "desktop_upper_button_y": 545,
        "desktop_lower_button_y": 598,
        "desktop_confirm_x": 204,
        "desktop_confirm_y": 402,
    },
    ((0, 0),): {
        "desktop_centered_button_x": -1560,
        "desktop_upper_button_y": 445,
        "desktop_lower_button_y": 480,
        "desktop_confirm_x": -1640,
        "desktop_confirm_y": 335,
    },
}


def click_mouse(x: int, y: int, count: int = 1) -> None:
    """Click mouse."""
    original_cursor_pos = win32api.GetCursorPos()
    win32api.SetCursorPos(*SetCursorPos(x, y).args())
    sleep(SHORT_SLEEP)
    for _ in range(count):
        mouse_event(*MouseEvent(dw_flags=MOUSEEVENTF_LEFTDOWN).args())
        mouse_event(*MouseEvent(dw_flags=MOUSEEVENTF_LEFTUP).args())
        sleep(SHORT_SLEEP)
    win32api.SetCursorPos(*SetCursorPos(*original_cursor_pos).args())


SHORT_SLEEP = 0.5


def get_displays() -> tuple[tuple[int, int], ...]:
    """Get display resolution signature using Sunshine logs."""
    string = Path("C:/Program Files/Sunshine/config/sunshine.log").read_text(
        encoding="utf-8"
    )
    info_pat = r"\[(?P<at>[^\]]+)\]: Info:"
    connections = {
        datetime.strptime(m["at"], "%Y-%m-%d %H:%M:%S.%f"): (
            m["event"].casefold() == "connected"
        )
        for m in finditer(
            pattern=rf"^{info_pat} CLIENT (?P<event>(?:DIS)?CONNECTED)$",
            string=string,
            flags=MULTILINE,
        )
    }
    connect_count = sum(connections.values())
    disconnect_count = len(connections) - connect_count
    if disconnect_count == connect_count:
        return ((0, 0),)
    width, height = last(
        (m["width"], m["height"])
        for m in finditer(
            pattern=rf"^{info_pat} Desktop resolution \[(?P<width>\d+)x(?P<height>\d+)\]$",
            string=string,
            flags=MULTILINE,
        )
    )
    # TODO: Return resolutions from "currently available display devices" when not streaming.
    return ((int(width), int(height)),)


def ask_intent(intent: str) -> str:
    """Ask whether set intent is correct."""
    return f'Is "{intent}" your intent?'


def ask_related(window: str, intent: str) -> str:
    """Ask whether window is related to intent."""
    return f'Is "{window}" related to your intent to "{intent}"?'


def ask_done(intent: str) -> str:
    """Ask whether user completed their intent."""
    return f'Did you complete "{intent}"?'


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
