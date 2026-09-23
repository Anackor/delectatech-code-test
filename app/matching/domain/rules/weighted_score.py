from collections.abc import Sequence

from rapidfuzz.fuzz import token_set_ratio

from app.matching.domain.models import Candidate, Decision, Venue
from .metrics import distance_meters


class WeightedScoreRule:
    def evaluate(self, source: Venue, candidates: Sequence[Venue]) -> Decision:
        ranked = sorted((self._score(source, candidate) for candidate in candidates),
                        key=lambda candidate: (-candidate.score, candidate.venue.identifier))
        if not ranked:
            return Decision(source.identifier, "unmatched", None, None, "no_geographic_or_postal_candidate", ())
        best, runner_up = ranked[0], ranked[1] if len(ranked) > 1 else None
        if best.score >= 80:
            status, reason = "matched", "weighted_score"
        elif best.score >= 70:
            status, reason = "ambiguous", "insufficient_score_gap"
        else:
            status, reason = "unmatched", "insufficient_weighted_score"
        return Decision(source.identifier, status, best, runner_up, reason, tuple(ranked))

    def _score(self, source: Venue, candidate: Venue) -> Candidate:
        distance = distance_meters(source, candidate)
        name = float(token_set_ratio(source.normalized_name, candidate.normalized_name))
        address = float(token_set_ratio(source.normalized_address, candidate.normalized_address))
        distance_score = None if distance is None else max(0, 100 * (1 - distance / 1_000))
        signals = [name, address] + ([distance_score] if distance_score is not None else [])
        score = round(sum(signals) / len(signals), 2)
        return Candidate(candidate, None if distance is None else round(distance, 1),
                         None if distance_score is None else round(distance_score, 2),
                         round(name, 2), round(address, 2), score)
