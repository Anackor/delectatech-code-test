import unittest

from app.matching.application.pack import select_pack
from tests.sources.matching import venue


class PackTest(unittest.TestCase):
    def test_selects_a_reproducible_bounded_sample(self):
        venues = [venue(str(number), f"Restaurante {number}") for number in range(100)]

        first, total = select_pack(venues, 5, seed=7)
        second, _ = select_pack(venues, 5, seed=7)

        self.assertEqual(total, 100)
        self.assertEqual([item.identifier for item in first], [item.identifier for item in second])
        self.assertEqual(len(first), 5)

    def test_rejects_an_empty_pack_size(self):
        with self.assertRaises(ValueError):
            select_pack([], 0, seed=1)
