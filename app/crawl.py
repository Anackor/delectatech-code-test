"""Adaptador CLI y composición del crawler."""

import argparse
import json
import os
from pathlib import Path
import sys

from app.adapters.json_file import write_json
from app.application.crawl_venue import crawl
from app.just_eat import CrawlError, validate_url


def main() -> int:
    parser = argparse.ArgumentParser(description="Extraer un menú de Just Eat España a JSON.")
    parser.add_argument("url", nargs="?", default=os.environ.get("CRAWL_URL"))
    parser.add_argument("--output", type=Path)
    parser.add_argument("--timeout", type=int, default=30, help="Timeout en segundos por operación (1–120).")
    args = parser.parse_args()
    try:
        if not args.url:
            raise CrawlError("invalid_url", "Indica la URL del restaurante.")
        if not 1 <= args.timeout <= 120:
            raise CrawlError("invalid_config", "El timeout debe estar entre 1 y 120 segundos.")
        url = validate_url(args.url)
        output = args.output or Path("output") / (url.split("/")[-2] + ".json")
        from app.adapters.just_eat_browser import fetch_menu

        report = crawl(url, output, lambda target: fetch_menu(target, args.timeout * 1000), write_json)
        print(json.dumps(report, ensure_ascii=False))
        return 0
    except CrawlError as exc:
        print(json.dumps({"status": "error", "code": exc.code, "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    except OSError:
        print(json.dumps({"status": "error", "code": "write_failed", "message": "No se pudo escribir la salida."}), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
