import json
import os
from pathlib import Path
import tempfile

from app.images.domain.models import ImageResult


def write_results(path: Path, results: list[ImageResult]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=".images-", suffix=".tmp", delete=False) as stream:
            temporary = Path(stream.name)
            json.dump([_as_dict(result) for result in results], stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary:
            temporary.unlink(missing_ok=True)


def _as_dict(result: ImageResult) -> dict:
    return {"cid": result.image.cid, "image": result.image.path, "status": result.status,
            "durationMs": result.duration_ms, "text": result.text, "error": result.error,
            "ocrLines": [_line_as_dict(line) for line in result.ocr_lines],
            "candidates": [_candidate_as_dict(item) for item in result.candidates],
            "reviewCandidates": [_candidate_as_dict(item) for item in result.review_candidates]}


def _line_as_dict(line) -> dict:
    return {"text": line.text, "ocrConfidence": round(line.confidence, 1),
            "boundingBox": line.bounding_box}


def _candidate_as_dict(candidate) -> dict:
    return {"name": candidate.name, "normalizedName": candidate.normalized_name,
            "evidence": candidate.evidence, "ocrConfidence": candidate.ocr_confidence,
            "boundingBox": candidate.bounding_box}
