"""Hasty implementation of Glyph's Pomodouroboros.

https://github.com/glyph/Pomodouroboros

Kid: I want Pomodouroboros, but it doesn't support Windows!
Parent: We have Pomodouroboros at home!
Pomodouroboros at home...
"""

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
from more_itertools import first, one
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
    day_start = max(get_time_today(pom.start), get_now())
    day_end = get_time_today(pom.end)
    periods = get_periods(pom.toggl)
    poms = list(
        time_range(day_start, day_end - periods.brk, periods.work + periods.brk)
    )
    if not poms:
        print(DONE_MSG)  # noqa: T201
        return
    print(get_startup_message(poms))  # noqa: T201
    for start in poms:
        if get_now() + periods.work > day_end:
            break
        if (time_until_start := start - get_now()) > timedelta(0):
            print(EARLY_MSG)  # noqa: T201
            try:
                sleep(time_until_start.total_seconds())
            except KeyboardInterrupt:
                print(DONE_MSG)  # noqa: T201
                return
        end = start + periods.work
        checks = time_range(start + CHECK_PERIOD, end, CHECK_PERIOD)
        distracted = False
        focused = timedelta(0)
        intent = ""
        intents = sync_intents(pom.intents, pom.toggl)
        intent_set = done = None
        interrupted = False
        last_check = get_now()
        print(START_MSG)  # noqa: T201
        set_toggl_pomodoro("start")
        for check in checks:
            if get_now() > end:
                break
            if not distracted:
                focused += get_now() - last_check
            distracted = False
            last_check = get_now()
            if (check_period := check - last_check) < timedelta(0):
                continue
            record_period(
                data=pom.poms,
                done=done,
                end=last_check,
                focused=focused,
                intent_set=intent_set,
                intent=intent,
                start=start,
            )
            try:
                sleep(check_period.total_seconds())
            except KeyboardInterrupt:
                interrupted = True
                break
            if done:
                continue
            if not intent_set and check > start + SETTABLE_INTENT_PERIOD:
                while not (intent := get_intent(pom.toggl)) or (
                    win32api.MessageBox(
                        *MessageBox(
                            0,
                            get_intent_msg(intent),
                            APP_NAME,
                            MB_SYSTEMMODAL | MB_YESNO | MB_DEFBUTTON2,
                        ).args()
                    )
                    != IDYES
                ):
                    win32api.MessageBox(
                        *MessageBox(
                            0, SET_INTENT_MSG, APP_NAME, MB_SYSTEMMODAL | MB_OK
                        ).args()
                    )
                print(DID_SET_INTENT_MSG)  # noqa: T201
                intent_set = get_now()
                continue
            if (
                not intent_set
                and (intent := get_intent(pom.toggl))
                and (
                    win32api.MessageBox(
                        *MessageBox(
                            0,
                            get_intent_msg(intent),
                            APP_NAME,
                            MB_SYSTEMMODAL | MB_YESNO | MB_DEFBUTTON2,
                        ).args()
                    )
                    == IDYES
                )
            ):
                print(DID_SET_INTENT_MSG)  # noqa: T201
                intent_set = get_now()
                continue
            if not intent_set or not (
                events := get_events(pom.toggl, start=last_check, end=check)
            ):
                continue
            new_unrelated = False
            for event in events:
                if distracted or new_unrelated:
                    break
                event_bin_only = f"{event.path.stem} -"
                window = f"{event_bin_only} {event.title}"
                if any(
                    related.casefold() in window.casefold()
                    for related in intents.get(intent, {}).get("related", {})
                ):
                    continue
                if any(
                    unrelated.casefold() in window.casefold()
                    for unrelated in intents.get(intent, {}).get("unrelated", {})
                ):
                    distracted = True
                    continue
                if (
                    win32api.MessageBox(
                        *MessageBox(
                            0,
                            get_related_msg(window),
                            APP_NAME,
                            MB_SYSTEMMODAL | MB_YESNO | MB_DEFBUTTON2,
                        ).args()
                    )
                    == IDYES
                ):
                    intents[intent]["related"].append(event_bin_only)
                    continue
                intents[intent]["unrelated"].append(event_bin_only)
                distracted = new_unrelated = True
            sync_intents(pom.intents, pom.toggl, intents)
            if (
                distracted
                and not new_unrelated
                and (
                    win32api.MessageBox(
                        *MessageBox(
                            0,
                            get_complete_intent_msg(intent),
                            APP_NAME,
                            MB_SYSTEMMODAL | MB_YESNO | MB_DEFBUTTON2,
                        ).args()
                    )
                    == IDYES
                )
            ):
                print(COMPLETED_INTENT_MSG)  # noqa: T201
                done = get_now()
        if not done and (
            win32api.MessageBox(
                *MessageBox(
                    0,
                    get_complete_intent_msg(intent),
                    APP_NAME,
                    MB_SYSTEMMODAL | MB_YESNO | MB_DEFBUTTON2,
                ).args()
            )
            == IDYES
        ):
            print(COMPLETED_INTENT_MSG)  # noqa: T201
            done = get_now()
        focused += get_now() - last_check
        record_period(
            data=pom.poms,
            done=done,
            end=done or get_now(),
            focused=focused,
            intent_set=intent_set,
            intent=intent,
            start=start,
        )
        if interrupted or get_now() + periods.brk > day_end:
            break
        if (time_until_end := end - get_now()) < timedelta(0):
            continue
        print(get_break_msg(time_until_end))  # noqa: T201
        try:
            sleep(time_until_end.total_seconds())
        except KeyboardInterrupt:
            break
    print(DONE_MSG)  # noqa: T201
    set_toggl_pomodoro("end")


APP_NAME = "Pomodouroboros at Home"
DONE_MSG = "Done for the day!"
EARLY_MSG = "Waiting for Pomodoro to begin..."
START_MSG = "Pomodoro has begun."
CHECK_PERIOD = timedelta(minutes=1)
SETTABLE_INTENT_PERIOD = timedelta(minutes=10)
SET_INTENT_MSG = "Please set an intent."
DID_SET_INTENT_MSG = "Congratulations on setting your intent!"
UNRELATED_MSG = "Please focus on your intent."
COMPLETE_INTENT_MSG = "Did you complete your intent?"
COMPLETED_INTENT_MSG = "Congratulations on completing your intent!"


def sync_intents(
    path: Path, db: Path, intents: Mapping[str, dict[str, list[str]]] | None = None
) -> Mapping[str, dict[str, list[str]]]:
    """Sync intents."""
    intent_id = "🆔 "
    with Session(create_engine(f"sqlite:///{db.as_posix()}")) as session:
        toggl_intents = session.exec(
            select(toggl.Entry).filter(
                col(toggl.Entry.description).like(f"%{intent_id}%")
            )
        ).all()
    all_intents = get_intents(path)
    for name, other in (intents or {}).items():
        if not (intent := all_intents.get(name, {})):
            continue
        for key in ["related", "unrelated"]:
            intent[key] = ordered_union(intent[key], other[key])
    all_intents = dict(
        sorted(
            {
                **{
                    intent.description: {"related": [], "unrelated": []}
                    for intent in toggl_intents
                },
                **all_intents,
            }.items(),
            key=lambda i: i[0].casefold().split(intent_id)[-1],
            reverse=True,
        )
    )
    path.write_text(encoding="utf-8", data=dumps(all_intents))
    return all_intents


def get_intents(path: Path) -> dict[str, dict[str, list[str]]]:
    """Get intents."""
    return loads(path.read_text(encoding="utf-8"))


T = TypeVar("T")


def ordered_union(iterable: Iterable[T], other: Iterable[T]) -> list[T]:
    """Get the ordered union of unique elements over two iterables."""
    return list(dict.fromkeys([*iterable, *other]))


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


def get_pom_time_elapsed(begin: datetime) -> timedelta:
    """Get time elapsed since Pomodoro began."""
    return get_now() - begin


def get_intent_msg(intent: str) -> str:
    """Get intent message."""
    return f'Is "{intent}" your intent?'


def get_related_msg(window: str) -> str:
    """Get related message."""
    return f'Is "{window}" related to your intent?'


def get_complete_intent_msg(intent: str) -> str:
    """Get complete intent message."""
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
    sleep(SHORT_SLEEP)


SHORT_SLEEP = 0.5


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
