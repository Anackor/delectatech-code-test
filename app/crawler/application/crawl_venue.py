"""Caso de uso: obtener, verificar y publicar un restaurante."""

from datetime import datetime, timezone
from pathlib import Path
from time import monotonic

from .ports import FetchVenue, SaveVenue


def crawl(url: str, output: Path, fetch: FetchVenue, save: SaveVenue) -> dict:
    started = monotonic()
    capture = fetch(url)
    save(output, capture.venue)
    menus = capture.venue["menus"].values()
    return {
        "status": "ok", "url": capture.url, "output": str(output),
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "menu_version": capture.menu_version,
        "menus": len(capture.venue["menus"]), "sections": sum(len(menu["sections"]) for menu in menus),
        "item_appearances": sum(len(section["items"]) for menu in menus for section in menu["sections"]),
        "elapsed_seconds": round(monotonic() - started, 3),
    }
