"""Caso de uso: obtener, convertir y publicar un restaurante."""

from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from time import monotonic

from app.just_eat import MenuSource, to_venue, validate_url

MenuFetcher = Callable[[str], MenuSource]
VenueWriter = Callable[[Path, dict], None]


def crawl(url: str, output: Path, fetch: MenuFetcher, write: VenueWriter) -> dict:
    started = monotonic()
    source = fetch(validate_url(url))
    venue = to_venue(source)
    write(output, venue)
    menus = venue["menus"].values()
    return {
        "status": "ok", "url": source.url, "output": str(output),
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "menu_version": source.cdn["restaurant"].get("menuVersion"),
        "menus": len(venue["menus"]), "sections": sum(len(menu["sections"]) for menu in menus),
        "item_appearances": sum(len(section["items"]) for menu in menus for section in menu["sections"]),
        "elapsed_seconds": round(monotonic() - started, 3),
    }
