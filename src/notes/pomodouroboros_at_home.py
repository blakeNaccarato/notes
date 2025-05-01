"""Hasty implementation of Glyph's Pomodouroboros.

https://github.com/glyph/Pomodouroboros

Kid: I want Pomodouroboros, but it doesn't support Windows!
Parent: We have Pomodouroboros at home!
Pomodouroboros at home...
"""

import asyncio
import ctypes
import json
from asyncio import Lock, TaskGroup, run
from datetime import datetime, timedelta
from json import loads
from typing import Any

from aiopath import AsyncPath
from playwright.async_api import Locator, PlaywrightContextManager, ViewportSize

# sourcery skip: remove-redundant-condition
DEBUG = False  # noqa: RUF034, RUF100

PERIODS = 2 if DEBUG else 4  # noqa: RUF034, RUF100
HOURS = 0 if DEBUG else 1  # noqa: RUF034, RUF100
MINUTES = 0 if DEBUG else 30  # noqa: RUF034, RUF100

SECONDS = 5 if DEBUG else 0  # noqa: RUF034, RUF100
BREAK_HOURS = 0  # noqa: RUF034, RUF100
BREAK_MINUTES = 0 if DEBUG else 20  # noqa: RUF034, RUF100
BREAK_SECONDS = 1 if DEBUG else 0  # noqa: RUF034, RUF100

NAME = "Pomodouroboros at Home"
DATA = AsyncPath("data/local/vaults/personal/_data/pomodouroboros.json")
TIMER = "https://www.google.com/search?q=timer"
PERIOD = timedelta(hours=HOURS, minutes=MINUTES, seconds=SECONDS)
BREAK_PERIOD = timedelta(
    hours=BREAK_HOURS, minutes=BREAK_MINUTES, seconds=BREAK_SECONDS
)
WIDTH = 728
HEIGHT = 536
HWND = 0
MB_OK = 0x1
MB_YESNOCANCEL = 0x3
MB_SYSTEMMODAL = 0x1000
IDYES = 6
IDNO = 7
IDCANCEL = 2
OPTIONS = {IDYES: "🍅", IDNO: "🥫", IDCANCEL: "❌"}


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
            now = datetime.now()
            for start in [now + i * PERIOD for i in range(PERIODS)]:
                tg.create_task(run_pomodoro(loc, lock, start))
        await loc.page.close()
        await ctx.close()
        await browser.close()


async def run_pomodoro(loc: Locator, lock: Lock, start: datetime):
    """Run a Pomodoro."""
    window_title = f"{NAME}: {start.strftime('%H:%M:%S')}"
    async with lock:
        await asyncio.sleep((start - datetime.now()).total_seconds())
        await loc.page.goto(TIMER)
        await loc.get_by_placeholder(":00:00").type(
            f"{HOURS:02}:{MINUTES:02}:{SECONDS:02}"
        )
        await loc.get_by_role("button", name="Start").click()
        await asyncio.sleep((PERIOD - BREAK_PERIOD).total_seconds())
        await asyncio.to_thread(
            ctypes.windll.user32.MessageBoxW,
            HWND,
            "Take a break!",
            window_title,
            MB_OK | MB_SYSTEMMODAL,
        )
        await asyncio.sleep(BREAK_PERIOD.total_seconds())
    await DATA.write_text(
        encoding="utf-8",
        data=dumps({
            **loads(await DATA.read_text(encoding="utf-8")),
            f"{start.isoformat(timespec='seconds')}-0700": OPTIONS[
                await asyncio.to_thread(
                    ctypes.windll.user32.MessageBoxW,
                    HWND,
                    "Did you accomplish your intention?",
                    window_title,
                    MB_YESNOCANCEL | MB_SYSTEMMODAL,
                )
            ],
        })
        + "\n",
    )


def dumps(obj: dict[str, Any] | None = None) -> str:
    """Dump JSON data."""
    return json.dumps(ensure_ascii=False, sort_keys=True, indent=2, obj=obj or {})


if __name__ == "__main__":
    run(main())
