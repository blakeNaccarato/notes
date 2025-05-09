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

DATA = AsyncPath("data/local/vaults/personal/_data/pomodouroboros.json")
PERIODS = 6
PERIOD = timedelta(hours=1, minutes=30)
BREAK = timedelta(minutes=20)


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
    await record_period(start, PERIOD - BREAK)
    if first:
        await asyncio.to_thread(set_toggl_pomodoro, start=True)
    try:
        await asyncio.sleep(PERIOD.total_seconds())
    except CancelledError as exc:
        exc.add_note("Pomodoro cancelled.")
        await record_period(start, get_now() - start)
        await asyncio.to_thread(set_toggl_pomodoro, start=False)
        raise


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


def set_toggl_pomodoro(start: bool):
    """Set the Toggl Pomodoro."""
    subprocess.run(
        capture_output=True,
        check=True,
        args=[
            "pwsh",
            "-NonInteractive",
            "-NoProfile",
            "-Command",
            "; ".join([
                "Import-Module 'AutoItX'",
                *[f"{CLICK} {START if start else STOP};"] * 2,
                f"{CLICK} {CONFIRM};",
            ]),
        ],
    )


CLICK = "Invoke-AU3MouseClick"
START = "-X -1240 -Y 350"
STOP = "-X -1240 -Y 380"
CONFIRM = "-X -1320 -Y 270"


def dumps(obj: dict[str, Any] | None = None) -> str:
    """Dump JSON data."""
    return json.dumps(ensure_ascii=False, sort_keys=True, indent=2, obj=obj or {})


def get_now() -> datetime:
    """Get current `datetime` in UTC."""
    return datetime.now(UTC)


if __name__ == "__main__":
    asyncio.run(main())
