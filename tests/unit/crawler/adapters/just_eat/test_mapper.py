import unittest

from app.crawler.adapters.just_eat.mapper import to_venue
from app.crawler.application.errors import CrawlError
from tests.sources.crawler.just_eat import menu_source


class JustEatMapperTest(unittest.TestCase):
    def test_converts_catalogue_to_example_contract(self):
        venue = to_venue(menu_source())

        self.assertEqual(venue["address"]["location"]["coordinates"], [2.1, 41.3])
        potatoes, pizza = venue["menus"]["delivery"]["sections"][0]["items"]
        self.assertEqual(potatoes["subSelections"][0]["options"], [{"id": "extra-1", "name": "Salsa", "price": 0.5}])
        self.assertEqual(pizza["price"], 8.0)
        self.assertEqual(pizza["subSelections"][0]["options"][1]["price"], 2.0)

    def test_rejects_missing_referenced_item(self):
        source = menu_source()
        source.cdn["restaurant"]["menus"][0]["categories"][0]["itemIds"].append("missing")

        with self.assertRaisesRegex(CrawlError, "Plato referenciado ausente") as raised:
            to_venue(source)
        self.assertEqual(raised.exception.code, "invalid_menu")

    def test_rejects_conditional_variations(self):
        source = menu_source()
        source.cdn["items"]["dish-2"]["variations"][1]["modifierGroupsIds"] = ["extras"]

        with self.assertRaisesRegex(CrawlError, "Opciones condicionadas") as raised:
            to_venue(source)
        self.assertEqual(raised.exception.code, "unsupported_menu")
