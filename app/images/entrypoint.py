"""Entrada CLI de la POC OCR sobre una muestra fija de imágenes."""

import argparse
from collections.abc import Iterable
import json
from pathlib import Path
import time

from app.images.adapters.archive import SAMPLE_IMAGES, image_reader
from app.images.adapters.json_output import write_results
from app.images.adapters.tesseract import read_text
from app.images.adapters.uploads import prepare_uploads, uploaded_image_reader
from app.images.application.process_images import process_images
from app.executions.application.runs import fail_execution, finish_execution, output_path, start_execution


def run(images: Path) -> dict:
    execution = start_execution("images", {"images": images}, {})
    return _execute(execution, SAMPLE_IMAGES, image_reader(images))


def run_uploads(files: Iterable[tuple[str, bytes]]) -> dict:
    files = list(files)
    images, payloads = prepare_uploads(files)
    execution = start_execution("images", {f"image-{index}": content
                                             for index, (_, content) in enumerate(files, start=1)},
                                {"source": "dashboard", "files": [image.path for image in images]})
    return _execute(execution, images, uploaded_image_reader(payloads))


def _execute(execution, images, read_image) -> dict:
    output = output_path(execution, "image-candidates.json")
    try:
        started_at = time.monotonic()
        results = process_images(images, read_image, read_text)
        write_results(output, results)
        summary = {status: sum(item.status == status for item in results)
                   for status in ("candidates", "no_text_readable", "inconclusive", "error")}
        metrics = {"processed": len(results), "new": 0 if execution.repeated_input else len(results),
                   "unchanged": len(results) if execution.repeated_input else 0, **summary}
        finish_execution(execution, output, metrics)
        return {"status": "ok", "executionId": execution.identifier, "images": len(results),
                "summary": summary, "durationMs": round((time.monotonic() - started_at) * 1_000),
                "output": str(output)}
    except Exception as exc:
        fail_execution(execution, exc)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Extraer candidatos a platos mediante OCR.")
    parser.add_argument("--images", type=Path, default=Path("source/google_images.zip"))
    args = parser.parse_args()
    try:
        print(json.dumps(run(args.images), ensure_ascii=False))
        return 0
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False))
        return 1
    except Exception as exc:
        print(json.dumps({"status": "error", "message": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
