from pathlib import Path
import re

import ijson

from app.matching.domain.models import Venue
from app.matching.domain.rules import normalize


def iter_just_eat(path: Path):
    with path.open("rb") as stream:
        for identifier, raw in ijson.kvitems(stream, ""):
            address = raw.get("address") or {}
            location = address.get("location") or {}
            coordinates = location.get("coordinates")
            longitude, latitude = coordinates if isinstance(coordinates, list) and len(coordinates) == 2 else (None, None)
            yield Venue("just_eat", str(identifier), raw.get("name") or "", normalize(raw.get("name")),
                        address.get("firstLine"), normalize(address.get("firstLine")), address.get("postalCode"),
                        _coordinate(latitude), _coordinate(longitude), _phone(raw.get("telephone")),
                        _url(raw.get("url")), tuple(normalize(value) for value in raw.get("cuisines", []) if normalize(value)))


def iter_google(path: Path):
    with path.open("rb") as stream:
        for raw in ijson.items(stream, "item"):
            address = raw.get("rawAddress")
            yield Venue("google", _google_identifier(raw), raw.get("name") or "", normalize(raw.get("name")),
                        address, normalize(address), _postal_code(address), _coordinate(raw.get("latitude")),
                        _coordinate(raw.get("longitude")), _phone(raw.get("telephone")),
                        _delivery_url(raw.get("deliveryUrlsJson")), _google_cuisines(raw.get("tagsRestaurantGoogle")))


def _coordinate(value: object) -> float | None:
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None


def _google_identifier(raw: dict) -> str:
    identifier = raw.get("googlePlaceId")
    if isinstance(identifier, str) and identifier:
        return identifier
    match = re.search(r"[?&]cid=(\d+)", raw.get("googleMapsUrl") or "")
    if match:
        return match.group(1)
    raise ValueError("Local de Google sin googlePlaceId ni CID")


def _postal_code(address: object) -> str | None:
    match = re.search(r"\b\d{5}\b", address) if isinstance(address, str) else None
    return match.group(0) if match else None


def _phone(value: object) -> str | None:
    digits = re.sub(r"\D", "", value) if isinstance(value, str) else ""
    return digits or None


def _url(value: object) -> str | None:
    return value.rstrip("/").casefold() if isinstance(value, str) else None


def _delivery_url(value: object) -> str | None:
    urls = value if isinstance(value, list) else []
    just_eat = next((url for url in urls if isinstance(url, str) and "just-eat.es" in url), None)
    return _url(just_eat)


def _google_cuisines(value: object) -> tuple[str, ...]:
    return tuple(normalize(item.get("name")) for item in value if isinstance(item, dict) and normalize(item.get("name"))) if isinstance(value, list) else ()
