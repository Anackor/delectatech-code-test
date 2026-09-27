from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from app.images.domain.models import ImageInput


SAMPLE_IMAGES = (
    ImageInput("12353399953336620223", "google_images/12353399953336620223/a8c3a678c184ef488d25f9774c20128d.jpg"),
    ImageInput("1326306244314649407", "google_images/1326306244314649407/80ada8490cd0992945a911e96597d8e4.jpg"),
    ImageInput("9944003937257840785", "google_images/9944003937257840785/3cbb7ebc3d0c8378482b5a96a94e5278.jpg"),
    ImageInput("13704801545575264378", "google_images/13704801545575264378/594bd6c734095e01b002c63e7e48614b.jpg"),
)
MAX_IMAGE_BYTES = 25_000_000


def read_from_zip(path: Path, image: ImageInput) -> bytes:
    # ponytail: entrada local para la POC. En produccion delegar la obtencion en un
    # adaptador de almacenamiento que entregue bytes, metadatos y una URL firmada;
    # el caso de uso no debe conocer ZIP, rutas de Google ni el proveedor de imagenes.
    expected_prefix = f"google_images/{image.cid}/"
    if not image.path.startswith(expected_prefix):
        raise ValueError(f"La imagen no corresponde al CID {image.cid}")
    with ZipFile(path) as archive:
        info = archive.getinfo(image.path)
        if info.file_size > MAX_IMAGE_BYTES:
            raise ValueError(f"La imagen supera el límite de {MAX_IMAGE_BYTES} bytes: {image.path}")
        return archive.read(info)


def image_reader(path: Path):
    return lambda image: read_from_zip(path, image)
