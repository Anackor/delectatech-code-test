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


def main() -> int:
    parser = argparse.ArgumentParser(description="Enlazar un pack de locales Just Eat con Google.")
    parser.add_argument("--size", type=int, default=int(os.environ.get("MATCH_PACK_SIZE", "50")))
    parser.add_argument("--seed", type=int, default=os.environ.get("MATCH_SEED"))
    parser.add_argument("--just-eat", type=Path, default=Path("source/just_eat_venues.json"))
    parser.add_argument("--google", type=Path, default=Path("source/google_venues.json"))
    parser.add_argument("--output", type=Path, default=Path("output/match-pack.json"))
    args = parser.parse_args()
    try:
        pack, total = select_pack(iter_just_eat(args.just_eat), args.size, args.seed)
        decisions = match_pack(pack, iter_google(args.google))
        save_decisions(pack, decisions)
        write_sample(args.output, pack, decisions)
        summary = {status: sum(decision.status == status for decision in decisions)
                   for status in ("matched", "ambiguous", "unmatched")}
        print(json.dumps({"status": "ok", "population": total, "pack_size": len(pack), "seed": args.seed,
                          "decisions": summary, "output": str(args.output)}, ensure_ascii=False))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
