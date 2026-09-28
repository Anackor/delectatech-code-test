from io import BytesIO
import unittest

from PIL import Image

from app.images.adapters.uploads import prepare_uploads, uploaded_image_reader


class UploadedImagesTest(unittest.TestCase):
    def test_prepares_multiple_images_and_removes_client_paths(self):
        first, second = self._image("JPEG"), self._image("PNG")
        images, payloads = prepare_uploads(((r"C:\fake\menu.jpg", first), ("dish.png", second)))

        self.assertEqual([image.path for image in images], ["uploads/1-menu.jpg", "uploads/2-dish.png"])
        self.assertEqual(uploaded_image_reader(payloads)(images[1]), second)

    def test_rejects_archives(self):
        with self.assertRaisesRegex(ValueError, "Formato no permitido"):
            prepare_uploads((("menus.zip", b"zip"),))

    def test_rejects_a_non_image_with_an_image_extension(self):
        with self.assertRaisesRegex(ValueError, "no contiene una imagen valida"):
            prepare_uploads((("fake.jpg", b"not an image"),))

    @staticmethod
    def _image(image_format: str) -> bytes:
        output = BytesIO()
        Image.new("RGB", (2, 2), "white").save(output, format=image_format)
        return output.getvalue()
