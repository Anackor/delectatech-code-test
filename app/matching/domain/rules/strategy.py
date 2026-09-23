from collections.abc import Sequence
from typing import Protocol

from app.matching.domain.models import Decision, Venue


class MatchRule(Protocol):
    def evaluate(self, source: Venue, candidates: Sequence[Venue]) -> Decision | None: ...
