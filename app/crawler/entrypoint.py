"""Adaptador CLI y composición del crawler."""

import argparse
import json
import os
import sys

from app.crawler.adapters.json_file import write_json
from app.crawler.adapters.just_eat.browser import fetch_venue
from app.crawler.adapters.just_eat.url import validate_url
from app.crawler.application.crawl_venue import crawl
from app.crawler.application.errors import CrawlError
from app.executions.application.runs import fail_execution, finish_execution, output_path, start_execution


def run(url: str, timeout: int) -> dict:
    execution = start_execution("crawler", {"url": url}, {"timeoutSeconds": timeout})
    try:
        target = validate_url(url)
        output = output_path(execution, "venue.json")
        report = crawl(target, output, lambda value: fetch_venue(value, timeout * 1000), write_json)
        finish_execution(execution, output, {"processed": 1, "new": 0 if execution.repeated_input else 1,
                                              "unchanged": 1 if execution.repeated_input else 0})
        return {**report, "executionId": execution.identifier, "output": str(output)}
    except Exception as exc:
        fail_execution(execution, exc)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Extraer un menú de Just Eat España a JSON.")
    parser.add_argument("url", nargs="?", default=os.environ.get("CRAWL_URL"))
    parser.add_argument("--timeout", type=int, default=30, help="Timeout en segundos por operación (1–120).")
    args = parser.parse_args()
    try:
        if not args.url:
            raise CrawlError("invalid_url", "Indica la URL del restaurante.")
        if not 1 <= args.timeout <= 120:
            raise CrawlError("invalid_config", "El timeout debe estar entre 1 y 120 segundos.")
        print(json.dumps(run(args.url, args.timeout), ensure_ascii=False))
        return 0
    except CrawlError as exc:
        print(json.dumps({"status": "error", "code": exc.code, "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1
    except OSError:
        print(json.dumps({"status": "error", "code": "write_failed", "message": "No se pudo escribir la salida."}), file=sys.stderr)
        return 1
    except Exception as exc:
        print(json.dumps({"status": "error", "code": "execution_failed", "message": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
