from pathlib import Path
import unittest

from app.images.adapters.archive import SAMPLE_IMAGES, read_from_zip
from app.images.adapters.tesseract import read_text


SOURCE_ZIP = Path("source/google_images.zip")


@unittest.skipUnless(SOURCE_ZIP.is_file(), "requires the locally provided google_images.zip")
class OcrSmokeTest(unittest.TestCase):
    def test_reads_text_from_the_fixed_pizza_menu(self):
        image = SAMPLE_IMAGES[1]

        lines = read_text(read_from_zip(SOURCE_ZIP, image))

        self.assertTrue(lines)
        self.assertTrue(any("Margarita" in line.text for line in lines))
