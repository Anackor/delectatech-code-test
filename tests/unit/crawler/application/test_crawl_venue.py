from pathlib import Path
import unittest

from app.crawler.application.crawl_venue import crawl
from app.crawler.application.errors import CrawlError
from tests.sources.crawler.just_eat import crawl_capture


class CrawlVenueTest(unittest.TestCase):
    def test_writes_capture_and_reports_counts(self):
        saved = []
        report = crawl(crawl_capture().url, Path("output/venue.json"), lambda _: crawl_capture(),
                       lambda path, venue: saved.append((path, venue)))

        self.assertEqual(saved[0][0], Path("output/venue.json"))
        self.assertEqual(saved[0][1]["name"], "Demo")
        self.assertEqual(report["menus"], 1)
        self.assertEqual(report["item_appearances"], 2)

    def test_does_not_save_when_fetch_fails(self):
        saved = []

        def fail(_: str):
            raise CrawlError("access_denied", "Bloqueado")

        with self.assertRaisesRegex(CrawlError, "Bloqueado"):
            crawl("https://www.just-eat.es/restaurants-demo/menu", Path("output/venue.json"), fail,
                  lambda path, venue: saved.append((path, venue)))
        self.assertEqual(saved, [])

    def test_propagates_save_failure(self):
        def fail_save(_: Path, __: dict):
            raise OSError("disco lleno")

        with self.assertRaises(OSError):
            crawl(crawl_capture().url, Path("output/venue.json"), lambda _: crawl_capture(), fail_save)
