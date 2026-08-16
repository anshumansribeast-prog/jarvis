"""URL helpers for HUD routing and public links."""

from __future__ import annotations

from ansux.config import settings


def normalize_path(path: str) -> str:
    """Strip query string and optional base path prefix."""
    path = path.split("?", 1)[0]
    base = settings.BASE_PATH
    if base and path.startswith(base):
        path = path[len(base):] or "/"
    return path


def public_hud_url() -> str:
    return settings.PUBLIC_URL.rstrip("/")


def api_url(path: str) -> str:
    path = path if path.startswith("/") else f"/{path}"
    return f"{settings.BASE_PATH}{path}" if settings.BASE_PATH else path
