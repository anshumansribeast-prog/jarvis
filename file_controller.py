"""File and folder operations — browsing known folders, creating,
finding, reading, renaming, moving, and deleting. Deletion is the one
destructive operation here; jarvis.py is responsible for confirming with
the user before ever calling delete().
"""

import os
import shutil

HOME = os.path.expanduser("~")

KNOWN_FOLDERS = {
    "downloads": os.path.join(HOME, "Downloads"),
    "documents": os.path.join(HOME, "Documents"),
    "desktop": os.path.join(HOME, "Desktop"),
    "pictures": os.path.join(HOME, "Pictures"),
}

# New folders/files Jarvis creates land on the desktop by default — visible
# immediately, rather than buried in the home directory.
DEFAULT_CREATE_DIR = KNOWN_FOLDERS["desktop"]

# Skipped while searching: huge, irrelevant, or slow to walk (venvs,
# node_modules, caches) — keeps find() fast and its results relevant.
_SKIP_DIRS = {"node_modules", ".git", "venv", "__pycache__", "AppData", ".cache"}


def open_known_folder(name):
    """Open one of the standard folders (Downloads, Documents, Desktop,
    Pictures) in File Explorer. Returns False if `name` isn't one of
    them, so the caller can fall back to something else."""
    path = KNOWN_FOLDERS.get(name.lower().strip())
    if not path:
        return False
    os.startfile(path)
    return True


def create_folder(name, base=None):
    if base is None:
        base = DEFAULT_CREATE_DIR
    path = os.path.join(base, name.strip())
    os.makedirs(path, exist_ok=True)
    return path


def create_file(name, base=None):
    if base is None:
        base = DEFAULT_CREATE_DIR
    name = name.strip()
    if "." not in name:
        name += ".txt"
    path = os.path.join(base, name)
    with open(path, "a", encoding="utf-8"):
        pass  # create if missing, leave untouched if it already exists
    return path


def find(name, root=None, limit=5):
    """Search under `root` for files/folders whose name contains `name`
    (case-insensitive substring). Returns up to `limit` matches, shortest
    path first (closest to root, usually the most relevant)."""
    if root is None:
        root = HOME
    name = name.lower().strip()
    matches = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in _SKIP_DIRS and not d.startswith(".")]
        for entry in dirnames + filenames:
            if name in entry.lower():
                matches.append(os.path.join(dirpath, entry))
        if len(matches) >= limit * 4:
            break
    matches.sort(key=len)
    return matches[:limit]


def open_path(path):
    os.startfile(path)


def read_text_file(path, max_chars=800):
    """Read up to `max_chars` of a text file. Returns (content, truncated) —
    truncated is True if the file had more than max_chars, so the caller
    can say so rather than silently cutting it off."""
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read(max_chars + 1)
    truncated = len(content) > max_chars
    return content[:max_chars], truncated


def rename(path, new_name):
    new_path = os.path.join(os.path.dirname(path), new_name.strip())
    os.rename(path, new_path)
    return new_path


def move(path, dest_folder_key):
    """Move `path` into one of the known folders. Returns the new path,
    or None if dest_folder_key isn't a recognized folder."""
    dest_dir = KNOWN_FOLDERS.get(dest_folder_key.lower().strip())
    if not dest_dir:
        return None
    new_path = os.path.join(dest_dir, os.path.basename(path))
    shutil.move(path, new_path)
    return new_path


def delete(path):
    """Permanently delete a file or folder. Callers must confirm with
    the user first — this function does not ask."""
    if os.path.isdir(path):
        shutil.rmtree(path)
    else:
        os.remove(path)
