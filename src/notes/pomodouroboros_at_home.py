"""Hasty implementation of Glyph's Pomodouroboros.

https://github.com/glyph/Pomodouroboros

Kid: I want Pomodouroboros, but it doesn't support Windows!
Parent: We have Pomodouroboros at home!
Pomodouroboros at home...
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timedelta
from itertools import accumulate
from json import loads
from pathlib import Path
from re import MULTILINE, Match, finditer
from time import sleep
from typing import Literal, TypeAlias, TypedDict, TypeVar

import win32api
import win32gui
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
from notes.serialization import ser_datetime, ser_json
from notes.times import current_tz, get_now, get_time_today
from notes.win import MessageBox, MouseEvent, SetCursorPos, WindowInfo

# ! TODO: Implement as a state machine.


def main(  # sourcery skip: low-code-quality  # noqa: C901, PLR0912, PLR0915
    pom: Pom,
) -> None:
    """Start Pomodoros."""
    # ! SETUP
    periods = get_periods(pom.toggl)
    work_period = periods.work
    break_period = periods.brk
    pom_period = work_period + periods.brk
    day_start = max(get_time_today(pom.start), get_now())
    day_end = get_time_today(pom.end)
    print(  # noqa: T201
        get_startup_message(
            poms := list(time_range(day_start, day_end + break_period, pom_period))
            or [day_start]
        )
    )
    # ! EARLY
    if get_now() < day_start:
        print(EARLY_MSG)  # noqa: T201
        try:
            sleep((day_start - get_now()).total_seconds())
        except KeyboardInterrupt:
            set_split_intents(pom.intents)
            print(DONE_MSG)  # noqa: T201
            return
    # ! IN POMODORO
    set_toggl_pomodoro("start")
    for start in poms:  # noqa: PLR1702
        cancel = force_ask_done = False
        distracted = False
        after = reward = intent = ""
        intent_set = done = after_done = None
        focused = (now := get_now()) - start
        checked = now
        record_period(
            data=pom.poms,
            done=done,
            end=now,
            focused=focused,
            intent_set=intent_set,
            intent=intent,
            start=start,
            after=after,
            after_done=after_done,
            reward=reward,
        )
        # ! IN CHECKS
        print(START_MSG)  # noqa: T201
        while get_now() < start + work_period:
            # ! WAITING FOR CHECK
            try:
                sleep(CHECK_PERIOD.total_seconds())
            except KeyboardInterrupt:
                if prompt(ASK_CANCEL):
                    cancel = True
                    break
                if intent_set and intent and intent != NO_INTENT and not done:
                    force_ask_done = True
            if done:
                continue
            # ! CHECKING INTENT
            if not intent_set and get_now() > start + SETTABLE_INTENT_PERIOD:
                while (
                    not (intent := get_intent(pom.toggl))
                    or intent == NO_INTENT
                    or not prompt(ask_intent(intent))
                ):
                    notify(SET_INTENT_MSG)
                    try:
                        sleep(FORCE_SET_INTENT_PERIOD.total_seconds())
                    except KeyboardInterrupt:
                        if prompt(ASK_CANCEL):
                            cancel = True
                        intent = NO_INTENT
                        print(DID_NOT_SET_INTENT_MSG)  # noqa: T201
                        break
                if cancel:
                    break
                if intent and intent != NO_INTENT:
                    intents = set_intent(path=pom.intents, intent=intent)
                    after = input(f"{ASK_AFTER}\n")
                    reward = input(f"{ASK_REWARD}\n")
                    print(DID_SET_INTENT_MSG)  # noqa: T201
                intent_set = get_now()
                continue
            if (
                not intent_set
                and (intent := get_intent(pom.toggl))
                and intent != NO_INTENT
                and prompt(ask_intent(intent))
            ):
                intents = set_intent(path=pom.intents, intent=intent)
                after = input(f"{ASK_AFTER}\n")
                reward = input(f"{ASK_REWARD}\n")
                print(DID_SET_INTENT_MSG)  # noqa: T201
                intent_set = get_now()
                continue
            if not intent_set or not intent or intent == NO_INTENT:
                checked = get_now()
                continue
            # ! CHECKING FOCUS
            if not (foreground := win32gui.GetForegroundWindow()):
                focused += (now := get_now()) - checked
                checked = now
                continue
            intents = get_intents(pom.intents)
            window_info = WindowInfo.from_handle(foreground)
            window = f"{Path(window_info.process.name()).stem} - {window_info.text}"
            related = check_window(window, intents[intent]["related"])
            unrelated = check_window(window, intents[intent]["unrelated"])
            if not related and unrelated:
                distracted = True
            if not related and not unrelated:
                if prompt(ask_related(window, intent)):
                    intents[intent]["related"] = list(
                        ordered_union(*intents[intent]["related"], *[window])
                    )
                else:
                    intents[intent]["unrelated"] = list(
                        ordered_union(*intents[intent]["unrelated"], *[window])
                    )
                set_intents(pom.intents, intents)
            # ! CHECKING COMPLETION
            now = get_now()
            if (distracted or force_ask_done) and prompt(ask_done(intent)):
                print(COMPLETED_INTENT_MSG)  # noqa: T201
                done = now
            force_ask_done = False
            if distracted:
                distracted = False
                print(FOCUS_MSG)  # noqa: T201
            else:
                focused += now - checked
            checked = now
            record_period(
                data=pom.poms,
                done=done,
                end=now,
                focused=focused,
                intent_set=intent_set,
                intent=intent,
                start=start,
                after=after,
                after_done=after_done,
                reward=reward,
            )
        # ! FINAL CHECKING OF FOCUS AND COMPLETION
        now = get_now()
        if intent and intent != NO_INTENT and not done and prompt(ask_done(intent)):
            print(COMPLETED_INTENT_MSG)  # noqa: T201
            done = now
        if intent and intent != NO_INTENT and not distracted:
            focused += now - checked
        record_period(
            data=pom.poms,
            done=done,
            end=now,
            focused=focused,
            intent_set=intent_set,
            intent=intent,
            start=start,
            after=after,
            after_done=after_done,
            reward=reward,
        )
        if cancel:
            break
        # ! TAKING A BREAK
        while get_now() < start + pom_period:
            print(get_break_msg(break_period := (start + pom_period) - get_now()))  # noqa: T201
            try:
                sleep(break_period.total_seconds())
            except KeyboardInterrupt:
                if prompt(ASK_CANCEL):
                    cancel = True
                    break
                if (
                    intent_set
                    and intent
                    and intent != NO_INTENT
                    and not after_done
                    and prompt(ask_done(after))
                ):
                    print(COMPLETED_AFTER_MSG)  # noqa: T201
                    after_done = now
        if (
            intent_set
            and intent
            and intent != NO_INTENT
            and not after_done
            and prompt(ask_done(after))
        ):
            print(COMPLETED_AFTER_MSG)  # noqa: T201
            after_done = now
        record_period(
            data=pom.poms,
            done=done,
            end=now,
            focused=focused,
            intent_set=intent_set,
            intent=intent,
            start=start,
            after=after,
            after_done=after_done,
            reward=reward,
        )
        if cancel:
            break
    # ! STOPPING POMODOROS AND CLEANING UP
    set_toggl_pomodoro("stop")
    set_split_intents(pom.intents)
    print(DONE_MSG)  # noqa: T201


CHECK_PERIOD = timedelta(minutes=1)
SETTABLE_INTENT_PERIOD = timedelta(minutes=5)
FORCE_SET_INTENT_PERIOD = timedelta(seconds=5)

NO_INTENT = "No intent 🆔 2025-08-13T115432-0700"

DONE_MSG = "Done for the day!"
EARLY_MSG = "Waiting for first Pomodoro to begin..."
START_MSG = "Pomodoro has begun."
SET_INTENT_MSG = "Please set an intent."
DID_SET_INTENT_MSG = "Congratulations on setting your intent!"
ASK_AFTER = "What do you intend to do during your break?"
ASK_REWARD = "What small reward will you get if you complete your intent?"
DID_NOT_SET_INTENT_MSG = "No intent for this Pomodoro."
ASK_CANCEL = "A Pomodoro is in progress. Do you want to cancel it?"
UNRELATED_MSG = "Please focus on your intent."
COMPLETED_INTENT_MSG = "Congratulations on completing your intent!"
COMPLETED_AFTER_MSG = "Congratulations on taking an intentional break!"
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


def set_split_intents(path: Path) -> dict[str, Intent]:
    """Add individual intents from compound intents to intents."""
    # TODO: Ask user which entries to split among intents
    set_intents(
        path,
        intents := merge_intents(
            (intents := get_intents(path)),
            {
                match.group(0).strip(): get_default_intent(match.group(0).strip())
                for name in intents
                for match in split_intents(name)
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


def set_intent(path: Path, intent: str) -> dict[str, Intent]:
    """Add intent to intents file."""
    return set_intents(
        path, merge_intents(get_intents(path), {intent: {**get_default_intent(intent)}})
    )


def get_default_intent(intent: str) -> Intent:
    """Get default intent."""
    return {
        "related": [
            *(
                [match.group(0).strip() for match in split_intents(intent)]
                if intent.count("🆔") > 1
                else [intent]
            ),
            "intents.json",
            "Obsidian - Today",
            "pomodouroboros.json",
            "ShellExperienceHost",
            "Toggl Track",
            "TogglTrack",
            "WindowsTerminal - 🍅",
        ],
        "unrelated": [],
    }


def split_intents(intent: str) -> Iterable[Match[str]]:
    """Split intents."""
    yield from finditer(
        pattern=rf"[^{get_sep(intent)}]+🆔[^{get_sep(intent)}]+",
        string=intent,
        flags=MULTILINE,
    )


def set_intents(path: Path, intents: dict[str, Intent]) -> dict[str, Intent]:
    """Set intents."""
    path.write_text(encoding="utf-8", data=ser_json(intents) + "\n")
    return intents


def merge_intents(
    intents: Mapping[str, Intent], other: Mapping[str, Intent]
) -> dict[str, Intent]:
    """Merge intents."""
    return {  # pyright: ignore[reportReturnType]  # TODO: Stop using TypedDict
        name: {
            key: list(
                ordered_union(
                    *(intents.get(name) or get_default_intent(name))[key],
                    *(other.get(name) or get_default_intent(name))[key],
                )
            )
            for key in KINDS
        }
        for name in ordered_union(*intents, *other)
    }


def get_intents(path: Path) -> dict[str, Intent]:
    """Get intents."""
    return loads(path.read_text(encoding="utf-8"))


T = TypeVar("T")


def ordered_union(*args: T) -> Iterable[T]:
    """Get the ordered union of unique elements over two iterables."""
    yield from dict.fromkeys(args)


class Intent(TypedDict):
    """Intent model."""

    related: list[str]
    unrelated: list[str]


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
    after: str,
    after_done: datetime | None = None,
    reward: str | None = None,
    start: datetime,
) -> None:
    """Record period."""
    # TODO: Handle `<this> or <that>` better. Currently doing it to allow manual overwrite
    poms = loads(data.read_text(encoding="utf-8"))
    pom = poms.get(intent) or {"intent": "", "after": "", "reward": ""}
    data.write_text(
        encoding="utf-8",
        data=ser_json({
            **poms,
            ser_datetime(start): {
                "done": ser_datetime(done) if done else None,
                "focused": focused / (end - start),
                "end": ser_datetime(end),
                "intent": pom["intent"] or intent,
                "intent_set": ser_datetime(intent_set) if intent_set else None,
                "after": pom["after"] or after,
                "after_done": ser_datetime(after_done) if after_done else None,
                "reward": pom["reward"] or reward,
            },
        })
        + "\n",
    )


Mode: TypeAlias = Literal["start", "stop"]


def set_toggl_pomodoro(mode: Mode) -> None:
    """Set Toggl Pomodoro."""
    c = DISPLAYS[get_displays()]
    for _ in range(2):
        click_mouse(
            *{
                "start": (c["desktop_centered_button_x"], c["desktop_upper_button_y"]),
                "stop": (c["desktop_centered_button_x"], c["desktop_lower_button_y"]),
            }[mode]
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


def click_mouse(x: int, y: int) -> None:
    """Click mouse."""
    original_cursor_pos = win32api.GetCursorPos()
    win32api.SetCursorPos(*SetCursorPos(x, y).args())
    sleep(SHORT_SLEEP)
    mouse_event(*MouseEvent(dw_flags=MOUSEEVENTF_LEFTDOWN).args())
    mouse_event(*MouseEvent(dw_flags=MOUSEEVENTF_LEFTUP).args())
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


if __name__ == "__main__":
    invoke(Pom)
