"""Hasty implementation of Glyph's Pomodouroboros.

https://github.com/glyph/Pomodouroboros

Kid: I want Pomodouroboros, but it doesn't support Windows!
Parent: We have Pomodouroboros at home!
Pomodouroboros at home...
"""

import asyncio
import json
import subprocess
from asyncio import TaskGroup
from collections.abc import Callable
from ctypes import windll
from datetime import UTC, datetime, timedelta
from json import loads
from typing import Any

from aiopath import AsyncPath

from notes.times import current_tz

# sourcery skip: remove-redundant-condition
DEBUG = False  # noqa: RUF034, RUF100
DATA = (
    AsyncPath("data/local" if DEBUG else "data/local/vaults/personal/_data")
    / "pomodouroboros.json"
)
PERIODS = 2 if DEBUG else 4  # noqa: RUF034, RUF100
HOURS = 0 if DEBUG else 1  # noqa: RUF034, RUF100
MINUTES = 0 if DEBUG else 10  # noqa: RUF034, RUF100
SECONDS = 5 if DEBUG else 0  # noqa: RUF034, RUF100
BREAK_HOURS = 0  # noqa: RUF034, RUF100
BREAK_MINUTES = 0 if DEBUG else 20  # noqa: RUF034, RUF100
BREAK_SECONDS = 1 if DEBUG else 0  # noqa: RUF034, RUF100


async def main():  # noqa: D103
    if not await DATA.exists():
        await DATA.write_text(encoding="utf-8", data=dumps())
    async with TaskGroup() as tg:
        now = get_now()
        tg.create_task(run_pomodoro(now.astimezone(current_tz), first=True))
        for start in [now + i * PERIOD for i in range(1, PERIODS)]:
            tg.create_task(run_pomodoro(start.astimezone(current_tz)))


PERIOD = timedelta(hours=HOURS, minutes=MINUTES, seconds=SECONDS)


async def run_pomodoro(start: datetime, first: bool = False):
    """Run Pomodoro."""
    await asyncio.sleep((start - get_now()).total_seconds())
    if first:
        await asyncio.to_thread(begin_toggl_pomodoro_focus_session)
    await asyncio.to_thread(prompt_pom_begin, start)
    await asyncio.sleep((PERIOD - BREAK_PERIOD).total_seconds())
    pom = await asyncio.to_thread(prompt_pom_success, start)
    await asyncio.sleep(BREAK_PERIOD.total_seconds())
    await DATA.write_text(
        encoding="utf-8",
        data=dumps({
            **loads(await DATA.read_text(encoding="utf-8")),
            start.isoformat(timespec="seconds"): pom,
        })
        + "\n",
    )


def begin_toggl_pomodoro_focus_session():
    """Begin focus session on Toggl Pomodoro."""
    subprocess.run(
        capture_output=True,
        check=True,
        args=["pwsh", "-NonInteractive", "-NoProfile", "-Command", TOGGLE_POMODORO],
    )


TOGGLE_POMODORO = """\
Import-Module 'AutoItX'; \
Invoke-AU3MouseClick -X -1240 -Y 350; \
Invoke-AU3MouseClick -X -1240 -Y 350; \
Invoke-AU3MouseClick -X -1320 -Y 270; \
"""
BREAK_PERIOD = timedelta(
    hours=BREAK_HOURS, minutes=BREAK_MINUTES, seconds=BREAK_SECONDS
)


def dumps(obj: dict[str, Any] | None = None) -> str:
    """Dump JSON data."""
    return json.dumps(ensure_ascii=False, sort_keys=True, indent=2, obj=obj or {})


def get_now() -> datetime:
    """Get current `datetime` in UTC."""
    return datetime.now(UTC)


def prompt_pom_begin(start: datetime):
    """Prompt that a Pomodoro has begun."""
    SHOW_MSG_BOX(
        WINDOW_HANDLE,
        BEGIN_MSG,
        f"{NAME}: {start.isoformat(timespec='seconds')}",
        OK_CANCEL_ABOVE_ALL,
    )


NAME = "Pomodouroboros at Home"
SHOW_MSG_BOX: Callable[[int, str, str, int], int] = windll.user32.MessageBoxW
WINDOW_HANDLE = 0
POM_END_MSG = "Time for a break! Did you accomplish your intention?"
MB_OK = 0x1
MB_YESNOCANCEL = 0x3
MB_SYSTEMMODAL = 0x1000
BEGIN_MSG = "Beginning focus session."
OK_CANCEL_ABOVE_ALL = MB_OK | MB_SYSTEMMODAL


def prompt_pom_success(start: datetime) -> str:
    """Prompt user about Pomodoro success."""
    return POM_END_BUTTONS[
        SHOW_MSG_BOX(
            WINDOW_HANDLE,
            POM_END_MSG,
            f"{NAME}: {start.isoformat(timespec='seconds')}",
            YES_NO_CANCEL_ABOVE_ALL,
        )
    ]


YES_NO_CANCEL_ABOVE_ALL = MB_YESNOCANCEL | MB_SYSTEMMODAL
ID_YES = 6
ID_NO = 7
ID_CANCEL = 2
POM_END_BUTTONS = {ID_YES: "🍅", ID_NO: "🥫", ID_CANCEL: "❌"}

if __name__ == "__main__":
    asyncio.run(main())
