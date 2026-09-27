"""Entrada CLI de la POC OCR sobre una muestra fija de imágenes."""

import argparse
import json
from pathlib import Path
import time

from app.images.adapters.archive import SAMPLE_IMAGES, image_reader
from app.images.adapters.json_output import write_results
from app.images.adapters.tesseract import read_text
from app.images.application.process_images import process_images


def main() -> int:
    parser = argparse.ArgumentParser(description="Extraer candidatos a platos mediante OCR.")
    parser.add_argument("--images", type=Path, default=Path("source/google_images.zip"))
    parser.add_argument("--output", type=Path, default=Path("output/image-candidates.json"))
    args = parser.parse_args()
    try:
        started_at = time.monotonic()
        results = process_images(SAMPLE_IMAGES, image_reader(args.images), read_text)
        write_results(args.output, results)
        summary = {status: sum(item.status == status for item in results)
                   for status in ("candidates", "no_text_readable", "inconclusive", "error")}
        print(json.dumps({"status": "ok", "images": len(results), "summary": summary,
                          "durationMs": round((time.monotonic() - started_at) * 1_000),
                          "output": str(args.output)}, ensure_ascii=False))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
