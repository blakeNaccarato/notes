"""Hasty implementation of Glyph's Pomodouroboros.

https://github.com/glyph/Pomodouroboros

Kid: I want Pomodouroboros, but it doesn't support Windows!
Parent: We have Pomodouroboros at home!
Pomodouroboros at home...
"""

import asyncio
import json
import subprocess
from asyncio import CancelledError, TaskGroup
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
PERIODS = 2 if DEBUG else 6  # noqa: RUF034, RUF100
HOURS = 0 if DEBUG else 1  # noqa: RUF034, RUF100
MINUTES = 0 if DEBUG else 30  # noqa: RUF034, RUF100
SECONDS = 5 if DEBUG else 0  # noqa: RUF034, RUF100


async def main():  # noqa: D103
    if not await DATA.exists():
        await DATA.write_text(encoding="utf-8", data=dumps())
    async with TaskGroup() as tg:
        now = get_now()
        tg.create_task(run_pomodoro(now.astimezone(current_tz), first=True))
        for start in [now + i * PERIOD for i in range(1, PERIODS)]:
            tg.create_task(run_pomodoro(start.astimezone(current_tz)))


async def run_pomodoro(start: datetime, first: bool = False):
    """Run Pomodoro."""
    await asyncio.sleep((start - get_now()).total_seconds())
    await record_period(start, PERIOD)
    if first:
        await asyncio.to_thread(toggle_toggl_pomodoro)
    try:
        await asyncio.sleep(PERIOD.total_seconds())
    except CancelledError as exc:
        exc.add_note("Pomodoro cancelled.")
        await record_period(start, get_now() - start)
        await asyncio.to_thread(toggle_toggl_pomodoro)
        raise


PERIOD = timedelta(hours=HOURS, minutes=MINUTES, seconds=SECONDS)


async def record_period(start: datetime, period: timedelta):
    """Record start time."""
    await DATA.write_text(
        encoding="utf-8",
        data=dumps({
            **loads(await DATA.read_text(encoding="utf-8")),
            ser_datetime(start): ser_datetime(start + period),
        })
        + "\n",
    )


def ser_datetime(start):
    """Serialize datetime."""
    return start.isoformat(timespec="seconds")


def toggle_toggl_pomodoro():
    """Toggle Toggl Pomodoro."""
    subprocess.run(
        capture_output=True,
        check=True,
        args=[
            "pwsh",
            "-NonInteractive",
            "-NoProfile",
            "-Command",
            TOGGLE_TOGGL_POMODORO,
        ],
    )


TOGGLE_TOGGL_POMODORO = """\
Import-Module 'AutoItX';
Invoke-AU3MouseClick -X -1240 -Y 350;
Invoke-AU3MouseClick -X -1240 -Y 350;
Invoke-AU3MouseClick -X -1320 -Y 270;
"""


def dumps(obj: dict[str, Any] | None = None) -> str:
    """Dump JSON data."""
    return json.dumps(ensure_ascii=False, sort_keys=True, indent=2, obj=obj or {})


def get_now() -> datetime:
    """Get current `datetime` in UTC."""
    return datetime.now(UTC)


if __name__ == "__main__":
    asyncio.run(main())
