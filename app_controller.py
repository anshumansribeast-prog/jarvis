"""Launch and close apps by name, driven by config/apps.json — adding a
new app means editing that file, not this code.
"""

import json
import os
import subprocess

_CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config", "apps.json")

with open(_CONFIG_PATH, "r", encoding="utf-8") as f:
    _APPS = json.load(f)


def resolve_app(name):
    """Match a spoken app name ("vs code", "chrome") to a registry entry.
    Exact key match first, then a loose substring match either way so
    "open code" still finds the "vs code" entry. Returns None if nothing
    in the registry looks like what was asked for.
    """
    name = name.lower().strip()
    if name in _APPS:
        return _APPS[name]
    for key, entry in _APPS.items():
        if name in key or key in name:
            return entry
    return None


def launch_app(name):
    """Launch the app registered under `name`. Returns True if launched,
    False if the name isn't in the registry."""
    entry = resolve_app(name)
    if not entry:
        return False
    if entry.get("shell"):
        subprocess.Popen(entry["launch"], shell=True)
    else:
        subprocess.Popen([entry["launch"]])
    return True


def close_app(name):
    """Ask Windows to close every running process matching this app's
    process name. Returns True if a close was attempted, False if the
    name isn't in the registry — does not report whether the process was
    actually running, taskkill handles that silently either way."""
    entry = resolve_app(name)
    if not entry:
        return False
    subprocess.run(
        ["taskkill", "/IM", entry["process_name"], "/F"],
        capture_output=True,
    )
    return True
