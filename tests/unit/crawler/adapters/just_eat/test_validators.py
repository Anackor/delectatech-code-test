from decimal import Decimal
import unittest

from app.crawler.adapters.just_eat.validators import index, list_of, price, text


class JustEatValidatorsTest(unittest.TestCase):
    def test_accepts_valid_provider_fields(self):
        self.assertEqual(text("Pizza", "name"), "Pizza")
        self.assertEqual(list_of(["delivery"], "serviceTypes"), ["delivery"])
        self.assertEqual(price("4.50"), Decimal("4.50"))
        self.assertEqual(index([{"id": "dish-1"}]), {"dish-1": {"id": "dish-1"}})

    def test_rejects_invalid_provider_fields(self):
        for validator, value in [(text, ""), (list_of, {}), (price, -1)]:
            with self.subTest(validator=validator.__name__), self.assertRaises(ValueError):
                validator(value, "field") if validator is not price else validator(value)
        with self.assertRaisesRegex(ValueError, "ID duplicado"):
            index([{"id": "dish-1"}, {"id": "dish-1"}])
