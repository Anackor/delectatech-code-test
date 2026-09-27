import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from app.images.adapters.json_output import write_results
from app.images.domain.models import Candidate, ImageResult
from tests.sources.images import image


class ImageJsonOutputTest(unittest.TestCase):
    def test_writes_evidence_and_candidate_position(self):
        result = ImageResult(
            image(), "candidates", "Pizza margarita 9.50", (),
            (Candidate("Pizza margarita", "pizza margarita", "Pizza margarita 9.50", 92.0, (10, 20, 100, 30)),), (), 12,
        )
        with TemporaryDirectory() as directory:
            path = Path(directory) / "candidates.json"
            write_results(path, [result])
            exported = json.loads(path.read_text(encoding="utf-8"))[0]

        self.assertEqual(exported["cid"], "cid-1")
        self.assertEqual(exported["ocrLines"], [])
        self.assertEqual(exported["candidates"][0]["boundingBox"], [10, 20, 100, 30])
        self.assertEqual(exported["candidates"][0]["normalizedName"], "pizza margarita")
