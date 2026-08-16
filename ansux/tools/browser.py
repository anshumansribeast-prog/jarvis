"""Browser and URL tools."""

from __future__ import annotations

import webbrowser

from ansux.config import settings


def open_url(url: str) -> None:
    webbrowser.open(url)


def open_site(key: str) -> bool:
    url = settings.SITES.get(key.lower())
    if not url:
        return False
    webbrowser.open(url)
    return True


def search_web(query: str) -> None:
    webbrowser.open(f"https://www.google.com/search?q={query}")
