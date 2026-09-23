import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from app.matching.adapters.json_output import write_sample
from app.matching.domain.models import Candidate, Decision
from tests.sources.matching import venue


class MatchingJsonOutputTest(unittest.TestCase):
    def test_writes_source_decision_and_pairwise_proposals(self):
        source = venue("je-1", "Edo")
        google = venue("google-1", "Edo Sushi", source="google")
        proposal = Candidate(google, 18.2, 98.18, 90, 80, 85.4)
        decision = Decision("je-1", "matched", proposal, None, "weighted_score", (proposal,))

        with TemporaryDirectory() as directory:
            output = Path(directory) / "matches.json"
            write_sample(output, [source], [decision])
            exported = json.loads(output.read_text(encoding="utf-8"))[0]

        self.assertEqual(exported["source"], {"provider": "just_eat", "id": "je-1", "name": "Edo"})
        self.assertEqual(exported["decision"]["selectedGooglePlaceId"], "google-1")
        self.assertEqual(exported["proposals"][0]["venue"]["name"], "Edo Sushi")
        self.assertEqual(exported["proposals"][0]["evidence"]["score"], 85.4)
        self.assertEqual(exported["proposals"][0]["evidence"]["distanceScore"], 98.18)
        self.assertNotIn("cuisineScore", exported["proposals"][0]["evidence"])
