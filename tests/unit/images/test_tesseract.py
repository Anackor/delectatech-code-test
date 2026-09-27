import unittest

from app.images.adapters.tesseract import _lines


class TesseractOutputTest(unittest.TestCase):
    def test_groups_words_in_a_tsv_line_and_preserves_its_bounds(self):
        lines = _lines(
            "level\tpage_num\tblock_num\tpar_num\tline_num\tleft\ttop\twidth\theight\tconf\ttext\n"
            "5\t1\t1\t1\t1\t10\t20\t20\t10\t90\tPizza\n"
            "5\t1\t1\t1\t1\t35\t20\t40\t10\t80\tMargarita\n"
        )

        self.assertEqual(lines[0].text, "Pizza Margarita")
        self.assertEqual(lines[0].confidence, 85.0)
        self.assertEqual(lines[0].bounding_box, (10, 20, 65, 10))
