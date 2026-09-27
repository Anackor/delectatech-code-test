"""Application service that keeps OCR failures isolated to one image."""

from collections.abc import Callable, Iterable
import subprocess
import time

from app.images.domain.candidates import extract_candidates, is_reliable_candidate
from app.images.domain.models import ImageInput, ImageResult, OcrLine


ReadImage = Callable[[ImageInput], bytes]
ReadText = Callable[[bytes], tuple[OcrLine, ...]]
MIN_CANDIDATE_CONFIDENCE = 65.0


def process_images(
    images: Iterable[ImageInput], read_image: ReadImage, read_text: ReadText
) -> list[ImageResult]:
    # ponytail: el flujo actual trata todas las imagenes como posibles cartas. En
    # produccion, un clasificador visual decidiria primero si hay carta o comida;
    # solo las cartas irian a OCR y las fotos de platos a un modelo de vision que
    # proponga etiquetas para revision, nunca como datos confirmados.
    results = []
    for image in images:
        started_at = time.monotonic()
        try:
            lines = read_text(read_image(image))
            candidates = extract_candidates(lines)
            confident_candidates = tuple(candidate for candidate in candidates if _is_accepted(candidate))
            review_candidates = tuple(candidate for candidate in candidates if candidate not in confident_candidates)
            results.append(ImageResult(
                image=image,
                status=_status(lines, confident_candidates),
                text="\n".join(line.text for line in lines),
                ocr_lines=lines,
                candidates=confident_candidates,
                review_candidates=review_candidates,
                duration_ms=_duration(started_at),
            ))
        except (OSError, ValueError, subprocess.SubprocessError) as exc:
            results.append(ImageResult(
                image=image,
                status="error",
                text="",
                ocr_lines=(),
                candidates=(),
                review_candidates=(),
                duration_ms=_duration(started_at),
                error=str(exc),
            ))
    return results


def _status(lines: tuple[OcrLine, ...], candidates: tuple) -> str:
    if candidates:
        return "candidates"
    if not lines:
        return "no_text_readable"
    return "inconclusive"


def _is_accepted(candidate) -> bool:
    # ponytail: confianza OCR y forma textual no prueban que exista el plato. La
    # aceptacion futura debe contrastar el candidato con el menu del restaurante,
    # precio y seccion; el resto debe permanecer en revision humana.
    return candidate.ocr_confidence >= MIN_CANDIDATE_CONFIDENCE and is_reliable_candidate(candidate)


def _duration(started_at: float) -> int:
    return round((time.monotonic() - started_at) * 1_000)
