"""Windows."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import IntEnum
from functools import partial
from typing import Any, Self

import win32con
import win32gui
import win32process
from psutil import Process
from win32con import MB_OK


def get_windows() -> dict[str, WindowInfo]:
    """Get windows."""
    win32gui.EnumWindows(
        partial(enum_window_callback, child=False, windows=(windows := {})), None
    )
    return windows


@dataclass
class WindowInfo:
    """Window info."""

    enabled: bool
    exists: bool
    handle: int
    parent: int
    pid: tuple[int, int]
    placement: WindowPlacement
    process: Process
    rect: tuple[int, int, int, int]
    text: str
    thread: int
    visible: bool

    @classmethod
    def from_handle(cls, handle: int) -> WindowInfo:
        """Get window info for a window handle."""
        (thread, process_handle) = win32process.GetWindowThreadProcessId(handle)
        return cls(
            enabled=bool(win32gui.IsWindowEnabled(handle)),
            exists=bool(win32gui.IsWindow(handle)),
            handle=handle,
            parent=win32gui.GetParent(handle),
            pid=win32process.GetWindowThreadProcessId(handle),
            placement=WindowPlacement.from_handle(handle),
            process=Process(process_handle),
            rect=win32gui.GetWindowRect(handle),
            text=win32gui.GetWindowText(handle),
            thread=thread,
            visible=bool(win32gui.IsWindowVisible(handle)),
        )


def enum_window_callback(handle: int, _extra: Any, child: bool, windows: Any) -> bool:
    """Low-level callback used when enumerating windows."""
    info = WindowInfo.from_handle(handle)
    if (
        not handle
        or not info.exists
        or not info.enabled
        or not info.visible
        or not info.text
    ):
        return True
    windows[info.text] = info
    if not child:
        win32gui.EnumChildWindows(
            handle, partial(enum_window_callback, child=True, windows=windows), None
        )
    return True


@dataclass
class WindowPlacement:
    """Window placement ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-windowplacement
    """

    length: int
    """Length ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-windowplacement#:~:text=length,-Type
    """
    cmd_show: CmdShow
    """Show window command ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-windowplacement#:~:text=showCmd,-Type
    """
    pt_min_position: tuple[int, int]
    """Upper-left window coordinate when minimized ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-windowplacement#:~:text=ptMinPosition,-Type
    """
    pt_max_position: tuple[int, int]
    """Upper-left window coordinate when maximized ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-windowplacement#:~:text=ptMaxPosition,-Type
    """
    rc_normal_position: tuple[int, int, int, int]
    """Restored window coordinates ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/ns-winuser-windowplacement#:~:text=rcNormalPosition,-Type
    """

    @classmethod
    def from_handle(cls: type[Self], hwnd: int) -> Self:
        """Create `WindowPlacement` from window handle."""
        placement = win32gui.GetWindowPlacement(hwnd)
        return cls(placement[0], CmdShow(placement[1]), *placement[2:])


class CmdShow(IntEnum):
    """Window show commands ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow#:~:text=%5Bin%5D%20nCmdShow
    """

    HIDE = win32con.SW_HIDE
    """Hide ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow#:~:text=SW_HIDE
    """
    SHOWNORMAL = win32con.SW_SHOWNORMAL
    """Activate and show ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow#:~:text=SW_SHOWNORMAL
    """
    SHOWMINIMIZED = win32con.SW_SHOWMINIMIZED
    """Show minimized ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow#:~:text=SW_SHOWMINIMIZED
    """
    SHOWMAXIMIZED = win32con.SW_SHOWMAXIMIZED
    """Show maximized ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow#:~:text=SW_SHOWMAXIMIZED
    """
    SHOWNOACTIVATE = win32con.SW_SHOWNOACTIVATE
    """Show without activating ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow#:~:text=SW_SHOWNOACTIVATE
    """
    SHOW = win32con.SW_SHOW
    """Show ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow#:~:text=SW_SHOW
    """
    MINIMIZE = win32con.SW_MINIMIZE
    """Minimize ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow#:~:text=SW_MINIMIZE
    """
    SHOWMINNOACTIVE = win32con.SW_SHOWMINNOACTIVE
    """Minimize without activating ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow#:~:text=SW_SHOWMINNOACTIVE
    """
    SHOWNA = win32con.SW_SHOWNA
    """Show without activating ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow#:~:text=SW_SHOWNA
    """
    RESTORE = win32con.SW_RESTORE
    """Restore ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow#:~:text=SW_RESTORE
    """
    SHOWDEFAULT = win32con.SW_SHOWDEFAULT
    """Default control ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow#:~:text=SW_SHOWDEFAULT
    """
    FORCEMINIMIZE = win32con.SW_FORCEMINIMIZE
    """Force minimize ([docs]).

    [docs]: https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow#:~:text=SW_FORCEMINIMIZE
    """


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
