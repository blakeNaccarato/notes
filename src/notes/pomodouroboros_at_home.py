"""Hasty implementation of Glyph's Pomodouroboros.

https://github.com/glyph/Pomodouroboros

Kid: I want Pomodouroboros, but it doesn't support Windows!
Parent: We have Pomodouroboros at home!
Pomodouroboros at home...
"""

import json
import subprocess
from datetime import UTC, date, datetime, time, timedelta
from json import loads
from pathlib import Path
from time import sleep
from typing import Any, Literal, TypeAlias

from notes.times import current_tz

DATA = Path("data/local/vaults/personal/_data/pomodouroboros.json")
END_OF_DAY = datetime.combine(date.today(), time(hour=16, minute=0, tzinfo=current_tz))
# ? Should match Toggl's Pomodoro settings
WORK_PERIOD = timedelta(hours=1, minutes=10)
BREAK_PERIOD = timedelta(minutes=20)


def main():  # noqa: D103
    mode = "start"
    begin = get_now() - POM_PERIOD
    while (begin := begin + POM_PERIOD) + POM_PERIOD < END_OF_DAY:
        print(BEGIN_MSG)  # noqa: T201
        record_period(begin, begin)
        set_toggl_pomodoro(mode)
        mode = "continue"
        break_period = BREAK_PERIOD
        try:
            sleep(WORK_PERIOD.total_seconds())
        except KeyboardInterrupt:
            print(EARLY_BREAK_MSG)  # noqa: T201
            break_period = BREAK_PERIOD + WORK_PERIOD - (get_now() - begin)
            set_toggl_pomodoro("break")
        print(get_break_msg(break_period))  # noqa: T201
        record_period(begin, get_now())
        try:
            sleep(break_period.total_seconds())
        except KeyboardInterrupt:
            break
    print("Done for the day!")  # noqa: T201
    set_toggl_pomodoro("end")


POM_PERIOD = WORK_PERIOD + BREAK_PERIOD
BEGIN_MSG = f"Please set an intent and focus for {WORK_PERIOD.total_seconds() // 60:.0f} minutes."
EARLY_BREAK_MSG = "Taking early break..."


def get_break_msg(period: timedelta) -> str:
    """Get break message."""
    return f"Please take a break for {period.total_seconds() // 60:.0f} minutes!"


def record_period(start: datetime, end: datetime | None = None):
    """Record period."""
    if not DATA.exists():
        DATA.write_text(encoding="utf-8", data=dumps())
    DATA.write_text(
        encoding="utf-8",
        data=dumps({
            **loads(DATA.read_text(encoding="utf-8")),
            ser_datetime(start): ser_datetime(end or start),
        })
        + "\n",
    )


def ser_datetime(value: datetime):
    """Serialize datetime."""
    return value.astimezone(current_tz).isoformat(timespec="seconds")


Mode: TypeAlias = Literal["start", "break", "end", "continue"]


def set_toggl_pomodoro(mode: Mode):
    """Set the Toggl Pomodoro."""
    if mode == "continue":
        return
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
                *[f"{CLICK} {MODES[mode]};"] * 2,
                f"{CLICK} {CONFIRM};",
            ]),
        ],
    )


CLICK = "Invoke-AU3MouseClick"
CONFIRM = "-X -1320 -Y 270"
MODES: dict[Mode, str] = {
    "continue": "",
    "start": "-X -1240 -Y 350",
    "break": "-X -1240 -Y 350",
    "end": "-X -1240 -Y 380",
}


def dumps(obj: dict[str, Any] | None = None) -> str:
    """Dump JSON data."""
    return json.dumps(ensure_ascii=False, sort_keys=True, indent=2, obj=obj or {})


def get_now() -> datetime:
    """Get current `datetime` in UTC."""
    return datetime.now(UTC)


if __name__ == "__main__":
    main()
