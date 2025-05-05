"""Manage a bullet journal."""

from __future__ import annotations

from asyncio import Lock, TaskGroup, run, sleep
from pathlib import Path
from typing import Annotated

from playwright.async_api import Locator, ViewportSize, async_playwright
from pydantic import BaseModel, BeforeValidator

DEBUG = False
DEBUG_CLICKS = False
PATH = Path("data/local/bullet_export.csv")

BASE_URL = "https://journal.bulletjournal.app/"
BASE = ""
SETTINGS = "settings"


async def export_data(path: Path):  # noqa: D103
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=False)
        ctx = await browser.new_context(
            viewport=ViewportSize(width=WIDTH, height=HEIGHT), base_url=BASE_URL
        )
        loc, lock = (await ctx.new_page()).locator("*"), Lock()
        async with TaskGroup() as tg:
            tg.create_task(_lock_and_export_data(loc, lock, path))
        await loc.page.close()
        await ctx.close()
        await browser.close()


async def _lock_and_export_data(loc: Locator, lock: Lock, path: Path):
    """Hold the lock."""
    async with lock:
        await _export_data(loc, path)


async def _export_data(loc: Locator, path: Path):
    """Hold the lock."""
    await loc.page.goto(BASE)
    await sleep(1)
    if DEBUG:
        await add_cursor_hover(loc)
    for pos in [
        CONTINUE_AS_GUEST,
        GET_STARTED,
        *[CONTINUE] * 4,
        *[DECLINE_PREMIUM] * 2,
    ]:
        await click(loc, pos)
    await loc.page.goto(SETTINGS)
    async with loc.page.expect_download() as downloader:
        for pos in [EXPORT, EXPORT_CSV]:
            await click(loc, pos)
    await (await downloader.value).save_as(path)
    if DEBUG:
        await loc.page.pause()


async def add_cursor_hover(loc: Locator):
    """Add relative position hover tooltip to cursor.

    The bullet list is a Flutter app so Playwright locators can't be used.
    Inspect and hardcode some constant pixel locations for desired button
    clicks by fixing the window resolution and setting up a hover tooltip
    with mouse coordinates.
    """
    await loc.page.evaluate(f"""\
        document.onmousemove = (e) => {{ if (e) {{
            x = (e.pageX/{WIDTH}).toFixed(2)
            y = (e.pageY/{HEIGHT}).toFixed(2)
            e.target.title = `Position{{x=${{x}}, y=${{y}}}}`
        }} }}""")


async def click(loc: Locator, pos: Position):
    """Click on position."""
    if DEBUG_CLICKS:
        await loc.page.pause()
    await sleep(WAIT)
    await loc.page.mouse.move(x=pos.x, y=pos.y)
    await sleep(WAIT)
    await loc.page.mouse.down()
    await sleep(WAIT)
    await loc.page.mouse.up()
    await sleep(WAIT)
    await loc.page.mouse.move(x=-pos.x, y=-pos.y)


WAIT = 0.25
WIDTH = 1280
HEIGHT = 720


class Position(BaseModel):
    """Page position."""

    x: Annotated[float, BeforeValidator(lambda v: v * WIDTH)]
    y: Annotated[float, BeforeValidator(lambda v: v * HEIGHT)]


CONTINUE_AS_GUEST = Position(x=0.50, y=0.83)
GET_STARTED = Position(x=0.50, y=0.94)
CONTINUE = GET_STARTED
DECLINE_PREMIUM = Position(x=0.66, y=0.10)
EXPORT = Position(x=0.60, y=0.41)
EXPORT_CSV = Position(x=0.60, y=0.35)


if __name__ == "__main__":
    run(export_data(PATH))
