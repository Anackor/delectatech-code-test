from app.images.domain.models import ImageInput, OcrLine


def image(cid: str = "cid-1", path: str = "google_images/cid-1/menu.jpg") -> ImageInput:
    return ImageInput(cid, path)


def line(text: str = "Pizza margarita: tomato and mozzarella 9.50", confidence: float = 92.0) -> OcrLine:
    return OcrLine(text, confidence, (10, 20, 100, 30))
