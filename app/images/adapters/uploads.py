from collections.abc import Iterable
from io import BytesIO
from pathlib import PurePosixPath

from PIL import Image, UnidentifiedImageError

from app.images.adapters.archive import MAX_IMAGE_BYTES
from app.images.domain.models import ImageInput


ALLOWED_EXTENSIONS = {".jpeg", ".jpg", ".png", ".webp"}


def prepare_uploads(files: Iterable[tuple[str, bytes]]) -> tuple[tuple[ImageInput, ...], dict[str, bytes]]:
    images, payloads = [], {}
    for index, (raw_name, content) in enumerate(files, start=1):
        name = PurePosixPath(raw_name.replace("\\", "/")).name
        suffix = PurePosixPath(name).suffix.lower()
        if not name or suffix not in ALLOWED_EXTENSIONS:
            raise ValueError(f"Formato no permitido: {raw_name}")
        if len(content) > MAX_IMAGE_BYTES:
            raise ValueError(f"La imagen supera el limite de {MAX_IMAGE_BYTES} bytes: {name}")
        try:
            with Image.open(BytesIO(content)) as image:
                if (image.format or "").lower() not in {"jpeg", "png", "webp"}:
                    raise ValueError
                image.verify()
        except (OSError, UnidentifiedImageError, ValueError) as exc:
            raise ValueError(f"El archivo no contiene una imagen valida: {name}") from exc
        path = f"uploads/{index}-{name}"
        images.append(ImageInput(f"upload-{index}", path))
        payloads[path] = content
    if not images:
        raise ValueError("Selecciona al menos una imagen.")
    return tuple(images), payloads


def uploaded_image_reader(payloads: dict[str, bytes]):
    return lambda image: payloads[image.path]
