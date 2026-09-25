import json
import os
from pathlib import Path
import tempfile

from app.classification.domain.models import Classification


def write_sample(path: Path, classifications: list[Classification], matches: dict[str, str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".classification-", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump([_as_dict(item, matches[item.dish.just_eat_id]) for item in classifications], stream,
                      ensure_ascii=False, indent=2, default=str)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary:
            temporary.unlink(missing_ok=True)


def _as_dict(classification: Classification, google_place_id: str) -> dict:
    dish, category = classification.dish, classification.category
    return {
        "restaurant": {"justEatId": dish.just_eat_id, "googlePlaceId": google_place_id},
        "dish": {"menuId": dish.menu_id, "sectionId": dish.section_id, "itemId": dish.item_id,
                 "name": dish.name, "description": dish.description, "section": dish.section_name,
                 "price": dish.price},
        "classification": {"status": classification.status, "rule": classification.rule,
                           "evidence": classification.evidence,
                           "category": None if category is None else {"uidentifier": category.uidentifier,
                           "name": category.name, "parent": category.parent, "family": category.family}},
    }
