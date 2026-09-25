import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from app.classification.adapters.json_output import write_sample
from app.classification.domain.models import Classification
from tests.sources.classification import category, dish


class ClassificationJsonOutputTest(unittest.TestCase):
    def test_writes_restaurant_dish_and_category_evidence(self):
        classification = Classification(dish("Pizza marinara"), "classified", category("pizza"), "alias_name", "pizza")

        with TemporaryDirectory() as directory:
            path = Path(directory) / "classified.json"
            write_sample(path, [classification], {"je-1": "google-1"})
            exported = json.loads(path.read_text(encoding="utf-8"))[0]

        self.assertEqual(exported["restaurant"], {"justEatId": "je-1", "googlePlaceId": "google-1"})
        self.assertEqual(exported["dish"]["name"], "Pizza marinara")
        self.assertEqual(exported["classification"]["category"]["name"], "pizza")
