from enum import IntEnum
import pywintypes
import win32api
import win32con
import win32gui
import win32process


# https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-showwindow
class WindowState(IntEnum):
    HIDE = win32con.SW_HIDE
    NORMAL = win32con.SW_NORMAL
    SHOWMINIMIZED = win32con.SW_SHOWMINIMIZED
    MAXIMIZE = win32con.SW_MAXIMIZE
    SHOWNOACTIVATE = win32con.SW_SHOWNOACTIVATE
    SHOW = win32con.SW_SHOW
    MINIMIZE = win32con.SW_MINIMIZE
    SHOWMINNOACTIVE = win32con.SW_SHOWMINNOACTIVE
    SHOWNA = win32con.SW_SHOWNA
    RESTORE = win32con.SW_RESTORE
    SHOWDEFAULT = win32con.SW_SHOWDEFAULT
    FORCEMINIMIZE = win32con.SW_FORCEMINIMIZE


def set_window_state(window_handle: int, state: WindowState) -> None:
    win32gui.ShowWindow(window_handle, state)


def get_window_handle_by_process_file_path_suffix(suffix: str) -> int | None:
    """
    Tries to look up a window handle that belongs to a prcess that has a module
    whose file path ends with suffix.

    Returns:
        Window handle of a matching window or None if no matching window was found.
    """
    extra: list[int] = []
    window_handles: list[int] = []

    def enum_callback(handle: int, extra: list[int]):
        window_handles.append(handle)

    win32gui.EnumWindows(enum_callback, extra)
    for handle in window_handles:
        if (
            # Try to skip windows that aren't visible in taskbar
            not (
                win32gui.GetWindowLong(handle, win32con.GWL_STYLE)
                & win32con.WS_EX_APPWINDOW
            )
            # win32gui.GetParent(handle)
            # or not win32gui.GetWindowText(handle)
        ):
            continue

        try:
            _, process_id = win32process.GetWindowThreadProcessId(handle)
            process_handle = win32api.OpenProcess(
                win32con.PROCESS_QUERY_INFORMATION + win32con.PROCESS_VM_READ,
                False,
                process_id,
            )
            try:
                for module_handle in win32process.EnumProcessModules(process_handle):
                    process_file_path: str = win32process.GetModuleFileNameEx(
                        process_handle, module_handle
                    )
                    if process_file_path.endswith(suffix):
                        return handle
            finally:
                win32api.CloseHandle(process_handle)
        except pywintypes.error:
            pass
        except Exception as exc:
            print("An exception occurred while getting Photoshop's window handle:", exc)
