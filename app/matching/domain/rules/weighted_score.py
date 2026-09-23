from collections.abc import Sequence

from rapidfuzz.fuzz import token_set_ratio

from app.matching.domain.models import Candidate, Decision, Venue
from .metrics import distance_meters


class WeightedScoreRule:
    def evaluate(self, source: Venue, candidates: Sequence[Venue]) -> Decision:
        ranked = sorted((self._score(source, candidate) for candidate in candidates),
                        key=lambda candidate: (-candidate.score, candidate.venue.identifier))
        if not ranked:
            return Decision(source.identifier, "unmatched", None, None, "no_geographic_or_postal_candidate")
        best, runner_up = ranked[0], ranked[1] if len(ranked) > 1 else None
        gap = best.score - runner_up.score if runner_up else float("inf")
        if best.score >= 80 and (best.distance_meters is None or best.distance_meters <= 500) and gap >= 8:
            status, reason = "matched", "weighted_score"
        elif best.score >= 70:
            status, reason = "ambiguous", "insufficient_score_gap"
        else:
            status, reason = "unmatched", "insufficient_weighted_score"
        return Decision(source.identifier, status, best, runner_up, reason)

    def _score(self, source: Venue, candidate: Venue) -> Candidate:
        distance = distance_meters(source, candidate)
        name = float(token_set_ratio(source.normalized_name, candidate.normalized_name))
        address = float(token_set_ratio(source.normalized_address, candidate.normalized_address))
        cuisine = self._cuisine(source, candidate)
        distance_score = 0 if distance is None else max(0, 100 * (1 - distance / 1_000))
        score = round(0.55 * name + 0.25 * address + 0.15 * distance_score + 0.05 * cuisine, 2)
        return Candidate(candidate, None if distance is None else round(distance, 1), round(name, 2), round(address, 2), round(cuisine, 2), score)

    @staticmethod
    def _cuisine(source: Venue, candidate: Venue) -> float:
        if not source.cuisines or not candidate.cuisines:
            return 0.0
        return 100.0 * len(set(source.cuisines) & set(candidate.cuisines)) / len(set(source.cuisines) | set(candidate.cuisines))
