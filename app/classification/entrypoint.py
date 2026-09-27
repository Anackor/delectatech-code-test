"""Entrada CLI para clasificar platos de restaurantes enlazados."""

import argparse
import json
from pathlib import Path

from app.classification.adapters.json_dishes import iter_dishes
from app.classification.adapters.json_output import write_sample
from app.classification.adapters.postgres import matched_restaurants, save_classifications
from app.classification.adapters.xlsx_taxonomy import read_taxonomy
from app.classification.application.classify_dishes import classify_dishes
from app.executions.application.runs import fail_execution, finish_execution, output_path, start_execution


def run(categories: Path, just_eat: Path) -> dict:
    execution = start_execution("classification", {"categories": categories, "justEat": just_eat}, {})
    output = output_path(execution, "classified-dishes.json")
    try:
        taxonomy = read_taxonomy(categories)
        matches = matched_restaurants()
        classifications = classify_dishes(iter_dishes(just_eat, matches), taxonomy)
        save_classifications(taxonomy.categories, classifications, matches)
        write_sample(output, classifications, matches)
        summary = {
            "classified": sum(item.status == "classified" for item in classifications),
            "review": sum(item.status == "review" for item in classifications),
            "generic": sum(bool(item.category and item.category.is_generic_or_other) for item in classifications),
        }
        metrics = {"processed": len(classifications), "new": 0 if execution.repeated_input else len(classifications),
                   "unchanged": len(classifications) if execution.repeated_input else 0, **summary}
        finish_execution(execution, output, metrics)
        return {"status": "ok", "executionId": execution.identifier, "matchedRestaurants": len(matches),
                "dishes": len(classifications), "summary": summary, "output": str(output)}
    except Exception as exc:
        fail_execution(execution, exc)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Clasificar platos de restaurantes enlazados.")
    parser.add_argument("--categories", type=Path, default=Path("source/food_categories.xlsx"))
    parser.add_argument("--just-eat", type=Path, default=Path("source/just_eat_venues.json"))
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.categories, args.just_eat), ensure_ascii=False))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False))
        return 1
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
