"""Minimize/maximize/restore/switch windows using the real Windows APIs
(via pywin32) rather than simulating keystrokes.
"""

import win32api
import win32con
import win32gui
import pywintypes


def _foreground_window():
    return win32gui.GetForegroundWindow()


def minimize_active_window():
    win32gui.ShowWindow(_foreground_window(), win32con.SW_MINIMIZE)


def maximize_active_window():
    win32gui.ShowWindow(_foreground_window(), win32con.SW_MAXIMIZE)


def restore_active_window():
    win32gui.ShowWindow(_foreground_window(), win32con.SW_RESTORE)


def show_desktop():
    """Minimize every visible top-level window — same effect as Win+D."""
    def _minimize_if_visible(hwnd, _):
        if win32gui.IsWindowVisible(hwnd) and win32gui.GetWindowText(hwnd):
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
    win32gui.EnumWindows(_minimize_if_visible, None)


def switch_to(name):
    """Bring the first visible window whose title contains `name` to the
    front. Returns True if a matching window was found, False otherwise
    — note this can still silently fail to actually focus the window if
    Windows' foreground-lock blocks it (it only lets the currently
    active app hand off focus voluntarily); the window is at least
    un-minimized either way.
    """
    name = name.lower().strip()
    match = []

    def _check(hwnd, _):
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd)
            if title and name in title.lower():
                match.append(hwnd)

    win32gui.EnumWindows(_check, None)
    if not match:
        return False

    hwnd = match[0]
    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
    _force_foreground(hwnd)
    return True


def _force_foreground(hwnd):
    """SetForegroundWindow refuses to steal focus from whatever the user
    is actively using — Windows' anti-annoyance guard against apps
    randomly popping to the front. Jarvis is always a background process
    while it's listening, so without a workaround every "switch to"
    would raise instead of switching. Briefly tapping Alt satisfies
    Windows' "the user just did something" check — the standard trick
    for this exact situation. Never lets the call crash Jarvis even if
    this still gets refused.
    """
    win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
    try:
        win32gui.SetForegroundWindow(hwnd)
    except pywintypes.error:
        pass
    finally:
        win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)
