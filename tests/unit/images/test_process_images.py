import unittest

from app.images.application.process_images import process_images
from tests.sources.images import image, line


class ProcessImagesTest(unittest.TestCase):
    def test_extracts_candidates_for_each_image(self):
        result = process_images([image()], lambda _image: b"image", lambda _bytes: (line(),))

        self.assertEqual(result[0].status, "candidates")
        self.assertEqual(result[0].candidates[0].name, "Pizza margarita")

    def test_keeps_processing_when_one_image_cannot_be_read(self):
        images = [image("bad", "google_images/bad/menu.jpg"), image("good", "google_images/good/menu.jpg")]

        def read_image(value):
            if value.cid == "bad":
                raise OSError("broken image")
            return b"image"

        result = process_images(images, read_image, lambda _bytes: (line(),))

        self.assertEqual([item.status for item in result], ["error", "candidates"])
        self.assertEqual(result[0].error, "broken image")

    def test_marks_low_confidence_text_as_inconclusive(self):
        result = process_images([image()], lambda _image: b"image", lambda _bytes: (line(confidence=50),))

        self.assertEqual(result[0].status, "inconclusive")
        self.assertEqual(result[0].candidates, ())
        self.assertEqual(result[0].review_candidates[0].name, "Pizza margarita")

    def test_sends_short_ocr_fragments_to_review(self):
        result = process_images([image()], lambda _image: b"image", lambda _bytes: (line("Es ca: ruido", 92),))

        self.assertEqual(result[0].status, "inconclusive")
        self.assertEqual(result[0].review_candidates[0].name, "Es ca")
