import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from app.adapters.json_file import write_json
from app.application.crawl_venue import crawl
from app.just_eat import CrawlError, MenuSource, to_venue, validate_url


def source() -> MenuSource:
    return MenuSource(
        url="https://www.just-eat.es/restaurants-demo/menu",
        details={"id": "42", "rating": {"votes": 3, "score": 4.5}, "restaurantPhoneNumber": "600000000"},
        cdn={
            "restaurant": {
                "httpStatusCode": 200, "countryCode": "es", "restaurantId": "42", "menuVersion": "v1",
                "restaurantInfo": {
                    "name": "Demo", "seoName": "demo", "description": "Carta de prueba", "logoUrl": None,
                    "isTestRestaurant": False, "cuisineTypes": [{"seoName": "pizza"}],
                    "location": {"city": "Barcelona", "address": "Calle Uno, 1", "postCode": "08001", "longitude": 2.1, "latitude": 41.3},
                    "restaurantOpeningTimes": [], "storeFrontType": "Restaurant",
                },
                "menus": [{
                    "menuGroupId": "delivery", "serviceTypes": ["delivery"], "description": "",
                    "categories": [{"id": "starters", "name": "Entrantes", "description": "", "itemIds": ["dish-1", "dish-2"]}],
                }],
            },
            "items": {
                "dish-1": {
                    "id": "dish-1", "name": "Patatas", "description": "", "imageSources": [],
                    "variations": [{"id": "dish-1", "name": "", "basePrice": 3.5, "menuGroupIds": ["delivery"], "modifierGroupsIds": ["extras"], "dealGroupsIds": None}],
                },
                "dish-2": {
                    "id": "dish-2", "name": "Pizza", "description": "Con queso",
                    "imageSources": [{"path": "https://image/{transformations}/pizza", "source": "Cloudinaryv2"}],
                    "variations": [
                        {"id": "small", "name": "Pequeña", "basePrice": 8, "menuGroupIds": ["delivery"], "modifierGroupsIds": [], "dealGroupsIds": None},
                        {"id": "large", "name": "Grande", "basePrice": 10, "menuGroupIds": ["delivery"], "modifierGroupsIds": [], "dealGroupsIds": None},
                    ],
                },
            },
            "modifierGroups": [{"id": "extras", "name": "Extras", "minChoices": 0, "maxChoices": 2, "modifiers": ["extra-1"]}],
            "modifierSets": [{"id": "extra-1", "modifier": {"name": "Salsa", "additionPrice": 0.5}}],
        },
    )


class JustEatTransformationTest(unittest.TestCase):
    def test_converts_catalogue_to_example_contract(self):
        venue = to_venue(source())

        self.assertEqual(venue["address"]["location"]["coordinates"], [2.1, 41.3])
        self.assertEqual(venue["menus"]["delivery"]["type"], ["delivery"])
        potatoes, pizza = venue["menus"]["delivery"]["sections"][0]["items"]
        self.assertEqual(potatoes["subSelections"][0]["options"], [{"id": "extra-1", "name": "Salsa", "price": 0.5}])
        self.assertEqual(pizza["price"], 8.0)
        self.assertEqual(pizza["subSelections"][0]["options"][1]["price"], 2.0)
        self.assertIn("ar_4:3", pizza["image"])

    def test_rejects_missing_referenced_item(self):
        broken = source()
        broken.cdn["restaurant"]["menus"][0]["categories"][0]["itemIds"].append("missing")

        with self.assertRaisesRegex(CrawlError, "Plato referenciado ausente") as raised:
            to_venue(broken)
        self.assertEqual(raised.exception.code, "invalid_menu")

    def test_allows_only_public_spanish_menu_urls(self):
        self.assertEqual(validate_url("http://just-eat.es/restaurants-demo/menu/"), "https://www.just-eat.es/restaurants-demo/menu")
        for url in ["https://www.just-eat.es/restaurants-demo/menu?x=1", "https://example.org/restaurants-demo/menu", "file:///tmp/menu"]:
            with self.assertRaises(CrawlError):
                validate_url(url)


class CrawlUseCaseTest(unittest.TestCase):
    def test_keeps_previous_output_when_fetch_fails(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "venue.json"
            output.write_text('{"previous": true}\n', encoding="utf-8")

            def fail(_: str):
                raise CrawlError("access_denied", "Bloqueado")

            with self.assertRaises(CrawlError):
                crawl(source().url, output, fail, write_json)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), {"previous": True})

    def test_writes_complete_json_and_reports_counts(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "venue.json"
            report = crawl(source().url, output, lambda _: source(), write_json)

            self.assertEqual(report["status"], "ok")
            self.assertEqual(report["menus"], 1)
            self.assertEqual(report["item_appearances"], 2)
            self.assertEqual(json.loads(output.read_text(encoding="utf-8"))["name"], "Demo")
