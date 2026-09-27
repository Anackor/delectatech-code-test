"""Entrada CLI para procesar un pack reproducible de matching."""

import argparse
import json
import os
from pathlib import Path

from app.matching.adapters.json_sources import iter_google, iter_just_eat
from app.matching.adapters.json_output import write_sample
from app.matching.adapters.postgres import save_decisions
from app.matching.application.match_pack import match_pack
from app.matching.application.pack import select_pack
from app.executions.application.runs import fail_execution, finish_execution, output_path, start_execution


def run(size: int, seed: int | None, just_eat: Path, google: Path) -> dict:
    execution = start_execution("matching", {"justEat": just_eat, "google": google}, {"size": size, "seed": seed})
    output = output_path(execution, "match-results.json")
    try:
        pack, total = select_pack(iter_just_eat(just_eat), size, seed)
        decisions = match_pack(pack, iter_google(google))
        save_decisions(pack, decisions)
        write_sample(output, pack, decisions)
        summary = {status: sum(decision.status == status for decision in decisions)
                   for status in ("matched", "ambiguous", "unmatched")}
        metrics = {"processed": len(decisions), "new": 0 if execution.repeated_input else len(decisions),
                   "unchanged": len(decisions) if execution.repeated_input else 0, **summary}
        finish_execution(execution, output, metrics)
        return {"status": "ok", "executionId": execution.identifier, "population": total,
                "packSize": len(pack), "seed": seed, "summary": summary, "output": str(output)}
    except Exception as exc:
        fail_execution(execution, exc)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Enlazar un pack de locales Just Eat con Google.")
    parser.add_argument("--size", type=int, default=int(os.environ.get("MATCH_PACK_SIZE", "50")))
    parser.add_argument("--seed", type=int, default=os.environ.get("MATCH_SEED"))
    parser.add_argument("--just-eat", type=Path, default=Path("source/just_eat_venues.json"))
    parser.add_argument("--google", type=Path, default=Path("source/google_venues.json"))
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.size, args.seed, args.just_eat, args.google), ensure_ascii=False))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False))
        return 1
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
