"""Entrada CLI para clasificar platos de restaurantes enlazados."""

import argparse
import json
from pathlib import Path

from app.classification.adapters.json_dishes import iter_dishes
from app.classification.adapters.json_output import write_sample
from app.classification.adapters.postgres import matched_restaurants, save_classifications
from app.classification.adapters.xlsx_taxonomy import read_taxonomy
from app.classification.application.classify_dishes import classify_dishes


def main() -> int:
    parser = argparse.ArgumentParser(description="Clasificar platos de restaurantes enlazados.")
    parser.add_argument("--categories", type=Path, default=Path("source/food_categories.xlsx"))
    parser.add_argument("--just-eat", type=Path, default=Path("source/just_eat_venues.json"))
    parser.add_argument("--output", type=Path, default=Path("output/classified-dishes.json"))
    args = parser.parse_args()
    try:
        taxonomy = read_taxonomy(args.categories)
        matches = matched_restaurants()
        classifications = classify_dishes(iter_dishes(args.just_eat, matches), taxonomy)
        save_classifications(taxonomy.categories, classifications, matches)
        write_sample(args.output, classifications, matches)
        summary = {
            "classified": sum(item.status == "classified" for item in classifications),
            "review": sum(item.status == "review" for item in classifications),
            "generic": sum(bool(item.category and item.category.is_generic_or_other) for item in classifications),
        }
        print(json.dumps({"status": "ok", "matched_restaurants": len(matches), "dishes": len(classifications),
                          "summary": summary, "output": str(args.output)}, ensure_ascii=False))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
