from collections.abc import Iterable, Iterator
from decimal import Decimal
from pathlib import Path

import ijson

from app.classification.domain.models import Dish


def iter_dishes(path: Path, accepted_restaurants: Iterable[str]) -> Iterator[Dish]:
    accepted = set(accepted_restaurants)
    with path.open("rb") as stream:
        for restaurant_id, venue in ijson.kvitems(stream, ""):
            if restaurant_id not in accepted:
                continue
            for menu_id, menu in (venue.get("menus") or {}).items():
                for section in menu.get("sections") or []:
                    for item in section.get("items") or []:
                        yield Dish(str(restaurant_id), str(menu_id), str(section.get("id") or ""),
                                   str(item.get("id") or ""), _text(item.get("name")), _text(item.get("description")),
                                   _text(section.get("name")), _price(item.get("price")),
                                   tuple(_text(cuisine) for cuisine in venue.get("cuisines", []) if _text(cuisine)))


def _text(value: object) -> str:
    return value.strip() if isinstance(value, str) else ""


def _price(value: object) -> Decimal | None:
    return value if isinstance(value, Decimal) else None
