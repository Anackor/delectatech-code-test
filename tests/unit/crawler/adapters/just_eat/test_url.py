import unittest

from app.crawler.adapters.just_eat.url import validate_url
from app.crawler.application.errors import CrawlError


class JustEatUrlTest(unittest.TestCase):
    def test_normalizes_a_public_menu_url(self):
        self.assertEqual(validate_url("http://just-eat.es/restaurants-demo/menu/"),
                         "https://www.just-eat.es/restaurants-demo/menu")

    def test_rejects_urls_outside_the_allowed_contract(self):
        for url in [
            "https://www.just-eat.es/restaurants-demo/menu?x=1",
            "https://example.org/restaurants-demo/menu",
            "file:///tmp/menu",
        ]:
            with self.subTest(url=url), self.assertRaises(CrawlError):
                validate_url(url)
