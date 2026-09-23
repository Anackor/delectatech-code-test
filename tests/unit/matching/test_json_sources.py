from decimal import Decimal
import unittest

from app.matching.adapters.json_sources import _coordinate


class JsonSourcesTest(unittest.TestCase):
    def test_keeps_decimal_coordinates_returned_by_ijson(self):
        self.assertEqual(_coordinate(Decimal("41.391999")), 41.391999)

    def test_rejects_non_numeric_coordinates(self):
        self.assertIsNone(_coordinate("41.391999"))
