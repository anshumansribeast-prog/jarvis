"""Volume and screenshots. Volume uses the same virtual key codes as the
laptop's physical volume keys — Windows handles the actual mixer, so this
can't set a wrong output device or bypass anything a real key press
couldn't do.
"""

import ctypes
import os
import subprocess
from datetime import datetime

import win32api
import win32con
from PIL import ImageGrab

_VK_VOLUME_MUTE = 0xAD
_VK_VOLUME_DOWN = 0xAE
_VK_VOLUME_UP = 0xAF

_SCREENSHOT_DIR = os.path.join(os.path.dirname(__file__), "screenshots")


def _press_key(vk_code):
    win32api.keybd_event(vk_code, 0, 0, 0)
    win32api.keybd_event(vk_code, 0, win32con.KEYEVENTF_KEYUP, 0)


def volume_up(steps=2):
    for _ in range(steps):
        _press_key(_VK_VOLUME_UP)


def volume_down(steps=2):
    for _ in range(steps):
        _press_key(_VK_VOLUME_DOWN)


def mute():
    _press_key(_VK_VOLUME_MUTE)


def take_screenshot():
    """Grab the whole screen and save it with a timestamped filename.
    Returns the saved path."""
    os.makedirs(_SCREENSHOT_DIR, exist_ok=True)
    filename = datetime.now().strftime("screenshot_%Y%m%d_%H%M%S.png")
    path = os.path.join(_SCREENSHOT_DIR, filename)
    ImageGrab.grab().save(path)
    return path


def lock():
    """Lock the workstation — instant, reversible (just log back in), so
    unlike shutdown/restart this doesn't need a confirmation prompt.
    pywin32 doesn't expose this one, so call the real Win32 API directly
    (this is the standard, documented way to do it from Python)."""
    ctypes.windll.user32.LockWorkStation()


def sleep():
    """Suspend the laptop. The 3 args to SetSuspendState are (hibernate,
    forceCritical, disableWakeEvent) — hibernate=0 means sleep, not
    hibernate; forceCritical=1 skips apps that would otherwise block
    the request; disableWakeEvent=0 leaves the keyboard/lid able to
    wake it back up, same as pressing the sleep button normally would.
    """
    subprocess.run(
        ["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"],
        capture_output=True,
    )


def shutdown():
    """Shut the computer down. Callers must confirm with the user
    first — this function does not ask, same convention as
    file_controller.delete()."""
    subprocess.run(["shutdown", "/s", "/t", "0"], capture_output=True)


def restart():
    """Restart the computer. Callers must confirm with the user first —
    same convention as shutdown() and file_controller.delete()."""
    subprocess.run(["shutdown", "/r", "/t", "0"], capture_output=True)
