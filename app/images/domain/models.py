from dataclasses import dataclass


@dataclass(frozen=True)
class ImageInput:
    cid: str
    path: str


@dataclass(frozen=True)
class OcrLine:
    text: str
    confidence: float
    bounding_box: tuple[int, int, int, int] | None = None


@dataclass(frozen=True)
class Candidate:
    name: str
    normalized_name: str
    evidence: str
    ocr_confidence: float
    bounding_box: tuple[int, int, int, int] | None = None


@dataclass(frozen=True)
class ImageResult:
    image: ImageInput
    status: str
    text: str
    ocr_lines: tuple[OcrLine, ...]
    candidates: tuple[Candidate, ...]
    review_candidates: tuple[Candidate, ...]
    duration_ms: int
    error: str | None = None
