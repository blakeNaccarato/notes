"""Hasty implementation of Glyph's Pomodouroboros.

https://github.com/glyph/Pomodouroboros

Kid: I want Pomodouroboros, but it doesn't support Windows!
Parent: We have Pomodouroboros at home!
Pomodouroboros at home...
"""

import asyncio
import json
from asyncio import Lock, TaskGroup, run
from collections.abc import Callable
from ctypes import windll
from datetime import UTC, datetime, timedelta
from json import loads
from typing import Any

from aiopath import AsyncPath
from playwright.async_api import Locator, PlaywrightContextManager, ViewportSize

from notes.datetime import current_tz

# sourcery skip: remove-redundant-condition
DEBUG = False  # noqa: RUF034, RUF100
DATA = (
    AsyncPath("data/local" if DEBUG else "data/local/vaults/personal/_data")
    / "pomodouroboros.json"
)
PERIODS = 2 if DEBUG else 4  # noqa: RUF034, RUF100
HOURS = 0 if DEBUG else 1  # noqa: RUF034, RUF100
MINUTES = 0 if DEBUG else 30  # noqa: RUF034, RUF100
SECONDS = 5 if DEBUG else 0  # noqa: RUF034, RUF100
BREAK_HOURS = 0  # noqa: RUF034, RUF100
BREAK_MINUTES = 0 if DEBUG else 20  # noqa: RUF034, RUF100
BREAK_SECONDS = 1 if DEBUG else 0  # noqa: RUF034, RUF100


async def main():  # noqa: D103
    if not await DATA.exists():
        await DATA.write_text(encoding="utf-8", data=dumps())
    async with PlaywrightContextManager() as pw:
        browser = await pw.chromium.launch(
            args=(["--disable-blink-features=AutomationControlled", "--mute-audio"]),
            channel="chrome",
            headless=False,
        )
        ctx = await browser.new_context(
            viewport=ViewportSize(width=WIDTH, height=HEIGHT)
        )
        loc, lock = (await ctx.new_page()).locator("*"), Lock()
        async with TaskGroup() as tg:
            now = get_now()
            for start in [now + i * PERIOD for i in range(PERIODS)]:
                tg.create_task(run_pomodoro(loc, lock, start))
        await loc.page.close()
        await ctx.close()
        await browser.close()


PERIOD = timedelta(hours=HOURS, minutes=MINUTES, seconds=SECONDS)
WIDTH = 728
HEIGHT = 536


async def run_pomodoro(loc: Locator, lock: Lock, start: datetime):
    """Run Pomodoro."""
    async with lock:
        await asyncio.sleep((start - get_now()).total_seconds())
        await loc.page.goto(TIMER)
        await loc.get_by_placeholder(":00:00").type(
            f"{HOURS:02}:{MINUTES:02}:{SECONDS:02}"
        )
        await loc.get_by_role("button", name="Start").click()
        await asyncio.sleep((PERIOD - BREAK_PERIOD).total_seconds())
        await asyncio.to_thread(prompt_break, start)
        await asyncio.sleep(BREAK_PERIOD.total_seconds())
    await DATA.write_text(
        encoding="utf-8",
        data=dumps({
            **loads(await DATA.read_text(encoding="utf-8")),
            ser_datetime(start): await asyncio.to_thread(prompt_pom_end, start),
        })
        + "\n",
    )


TIMER = "https://www.google.com/search?q=timer"
BREAK_PERIOD = timedelta(
    hours=BREAK_HOURS, minutes=BREAK_MINUTES, seconds=BREAK_SECONDS
)


def dumps(obj: dict[str, Any] | None = None) -> str:
    """Dump JSON data."""
    return json.dumps(ensure_ascii=False, sort_keys=True, indent=2, obj=obj or {})


def get_now() -> datetime:
    """Get current `datetime` in UTC."""
    return datetime.now(UTC)


def ser_datetime(start: datetime) -> str:
    """Serialize `datetime`."""
    return start.astimezone(current_tz).isoformat(timespec="seconds")


def prompt_break(start: datetime):
    """Prompt user to take a break."""
    SHOW_MSG_BOX(
        WINDOW_HANDLE,
        BREAK_MSG,
        f"{NAME}: {start.strftime('%H:%M:%S')}",
        OK_CANCEL_ABOVE_ALL,
    )


def prompt_pom_end(start: datetime) -> str:
    """Prompt user as Pomodoro ends."""
    return POM_END_BUTTONS[
        SHOW_MSG_BOX(
            WINDOW_HANDLE,
            POM_END_MSG,
            f"{NAME}: {start.strftime('%H:%M:%S')}",
            YES_NO_CANCEL_ABOVE_ALL,
        )
    ]


NAME = "Pomodouroboros at Home"
SHOW_MSG_BOX: Callable[[int, str, str, int], int] = windll.user32.MessageBoxW
WINDOW_HANDLE = 0
BREAK_MSG = "Take a break!"
POM_END_MSG = "Did you accomplish your intention?"
MB_OK = 0x1
MB_YESNOCANCEL = 0x3
MB_SYSTEMMODAL = 0x1000
OK_CANCEL_ABOVE_ALL = MB_OK | MB_SYSTEMMODAL
YES_NO_CANCEL_ABOVE_ALL = MB_YESNOCANCEL | MB_SYSTEMMODAL
ID_YES = 6
ID_NO = 7
ID_CANCEL = 2
POM_END_BUTTONS = {ID_YES: "🍅", ID_NO: "🥫", ID_CANCEL: "❌"}


if __name__ == "__main__":
    run(main())
