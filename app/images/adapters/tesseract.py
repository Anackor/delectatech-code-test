import csv
from collections import defaultdict
from io import BytesIO, StringIO
import subprocess

from PIL import Image, ImageOps

from app.images.domain.models import OcrLine


MAX_PIXELS = 4_000_000
TIMEOUT_SECONDS = 20


def read_text(image_bytes: bytes) -> tuple[OcrLine, ...]:
    # ponytail: un unico OCR local es suficiente para la POC. En produccion, una
    # etapa previa clasificaria la imagen (carta, plato, exterior o ilegible) y
    # delegaria cartas dificiles a OCR especializado con correccion de perspectiva,
    # deteccion de columnas y seleccion de idioma.
    image = _preprocess(image_bytes)
    result = subprocess.run(
        ("tesseract", "stdin", "stdout", "-l", "spa+eng", "--psm", "6", "tsv"),
        input=image, capture_output=True, check=True, timeout=TIMEOUT_SECONDS,
    )
    return _lines(result.stdout.decode("utf-8", errors="replace"))


def _preprocess(image_bytes: bytes) -> bytes:
    # ponytail: solo se aplica orientacion, escala y contraste. Una version madura
    # elegiria el preprocesado segun metricas de borrosidad, inclinacion, resolucion
    # y tipo de carta, registrando la variante que produjo cada lectura.
    with Image.open(BytesIO(image_bytes)) as source:
        image = ImageOps.exif_transpose(source).convert("L")
        if image.width * image.height > MAX_PIXELS:
            image.thumbnail((2_000, 2_000))
        image = ImageOps.autocontrast(image)
        output = BytesIO()
        image.save(output, format="PNG")
        return output.getvalue()


def _lines(tsv: str) -> tuple[OcrLine, ...]:
    words = defaultdict(list)
    for row in csv.DictReader(StringIO(tsv), delimiter="\t"):
        if row.get("level") != "5":
            continue
        text = (row.get("text") or "").strip()
        confidence = float(row.get("conf") or -1)
        if text and confidence >= 0:
            key = tuple(row[field] for field in ("page_num", "block_num", "par_num", "line_num"))
            words[key].append((text, confidence, _bounding_box(row)))
    return tuple(OcrLine(
        " ".join(text for text, _, _ in values),
        sum(confidence for _, confidence, _ in values) / len(values),
        _merge_bounding_boxes(box for _, _, box in values),
    ) for values in words.values())


def _bounding_box(row: dict[str, str]) -> tuple[int, int, int, int]:
    return tuple(int(row[field]) for field in ("left", "top", "width", "height"))


def _merge_bounding_boxes(boxes) -> tuple[int, int, int, int]:
    boxes = tuple(boxes)
    left = min(box[0] for box in boxes)
    top = min(box[1] for box in boxes)
    right = max(box[0] + box[2] for box in boxes)
    bottom = max(box[1] + box[3] for box in boxes)
    return left, top, right - left, bottom - top
