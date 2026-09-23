from collections.abc import Sequence

from app.matching.domain.models import Candidate, Decision, Venue
from .metrics import distance_meters


class ExactPhoneRule:
    def evaluate(self, source: Venue, candidates: Sequence[Venue]) -> Decision | None:
        matches = [candidate for candidate in candidates if source.telephone and source.telephone == candidate.telephone]
        if len(matches) != 1:
            return None
        candidate = Candidate(matches[0], distance_meters(source, matches[0]), 100.0, 100.0, 100.0, 100.0)
        return Decision(source.identifier, "matched", candidate, None, "exact_phone")
