import unittest

from app.matching.application.match_pack import match_pack
from tests.sources.matching import venue


class MatchingTest(unittest.TestCase):
    def test_matches_a_nearby_restaurant_with_similar_name(self):
        decisions = match_pack([venue("je-1", "Pizzería Roma")], [
            venue("google-1", "Pizzeria Roma", 41.4002, 2.1002, source="google"),
            venue("google-2", "Pizzería Roma", 41.409, 2.109, source="google"),
        ])

        self.assertEqual(decisions[0].status, "matched")
        self.assertEqual(decisions[0].candidate.venue.identifier, "google-1")

    def test_leaves_a_distant_same_name_unmatched(self):
        decisions = match_pack([venue("je-1", "Pizzería Roma")], [
            venue("google-1", "Pizzeria Roma", 41.45, 2.15, source="google"),
        ])

        self.assertEqual(decisions[0].status, "unmatched")
        self.assertIsNone(decisions[0].candidate)

    def test_stops_at_an_exact_phone_match(self):
        source = venue("je-1", "Nombre distinto", source="just_eat")
        source = source.__class__(**{**source.__dict__, "telephone": "600123123"})
        candidate = venue("google-1", "Otro nombre", 41.4002, 2.1002, source="google")
        candidate = candidate.__class__(**{**candidate.__dict__, "telephone": "600123123"})

        decision = match_pack([source], [candidate])[0]

        self.assertEqual(decision.status, "matched")
        self.assertEqual(decision.reason, "exact_phone")
