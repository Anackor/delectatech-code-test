from collections.abc import Iterable

from app.matching.domain.models import Decision, Venue
from app.matching.domain.rules import evaluate
from app.matching.domain.rules.geography import build_index, candidates_for


def match_pack(just_eat_venues: Iterable[Venue], google_venues: Iterable[Venue]) -> list[Decision]:
    grid, postal_codes = build_index(google_venues)
    return [evaluate(venue, candidates_for(venue, grid, postal_codes)) for venue in just_eat_venues]
