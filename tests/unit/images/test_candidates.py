import unittest

from app.images.domain.candidates import extract_candidates
from tests.sources.images import line


class CandidateExtractionTest(unittest.TestCase):
    def test_keeps_the_name_evidence_confidence_and_position(self):
        candidates = extract_candidates([line("Pizza margarita: tomato and mozzarella 9.50", 92.4)])

        self.assertEqual(candidates[0].name, "Pizza margarita")
        self.assertEqual(candidates[0].normalized_name, "pizza margarita")
        self.assertEqual(candidates[0].evidence, "Pizza margarita: tomato and mozzarella 9.50")
        self.assertEqual(candidates[0].ocr_confidence, 92.4)
        self.assertEqual(candidates[0].bounding_box, (10, 20, 100, 30))

    def test_discards_headers_and_prices(self):
        candidates = extract_candidates([line("Pizzas"), line("12.50")])

        self.assertEqual(candidates, ())
