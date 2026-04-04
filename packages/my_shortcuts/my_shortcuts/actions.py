"""Actions."""

import os
from contextlib import contextmanager, suppress
from json import dumps, loads
from os import getpid
from pathlib import Path
from signal import SIGTERM
from time import sleep

import keyboard
import mouse
from cappa import Output

from my_shortcuts.models import Position

WAIT = 0.1


def play_clicks(dry: bool, verbose: bool, output: Output):
    output("Playing back clicks...")
    positions: list[Position] = loads(POSITIONS.read_text(encoding="utf-8"))
    with killable(), suppress(KeyboardInterrupt):
        for pos in positions:
            wait()
            if verbose:
                output(f"Moving to {pos}...")
            mouse.move(*pos)
            wait()
            if dry:
                output(f"Would click at {pos}")
                mouse.wait(target_types=mouse.UP)
                continue
            if verbose:
                output(f"Clicking at {pos}...")
            mouse.click()
    output("Finished playing back clicks.")


def record_clicks(verbose: bool, output: Output):
    positions: list[Position] = []
    output("Recording clicks...")
    with killable(), suppress(KeyboardInterrupt):
        while True:
            mouse.wait(target_types=mouse.DOWN)
            pos = mouse.get_position()
            if verbose:
                output(f"{pos}")
            positions.append(pos)
            wait()
    POSITIONS.write_text(encoding="utf-8", data=dumps(positions))
    output("Clicks recorded.")


POSITIONS = Path("data/positions.json")


@contextmanager
def killable(key: str = "q"):
    hotkeys = [
        f"alt+{key}",
        f"alt+shift+{key}",
        f"ctrl+alt+{key}",
        f"ctrl+alt+shift+{key}",
        f"ctrl+{key}",
        f"ctrl+shift+{key}",
    ]
    for hotkey in hotkeys:
        keyboard.add_hotkey(hotkey, kill)
    yield


def wait():
    sleep(WAIT)


def kill():
    os.kill(getpid(), SIGTERM)
