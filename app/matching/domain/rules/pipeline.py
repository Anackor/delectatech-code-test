from collections.abc import Sequence

from app.matching.domain.models import Decision, Venue
from .delivery_url import DeliveryUrlRule
from .exact_phone import ExactPhoneRule
from .strategy import MatchRule
from .weighted_score import WeightedScoreRule


RULES: tuple[MatchRule, ...] = (ExactPhoneRule(), DeliveryUrlRule(), WeightedScoreRule())


def evaluate(source: Venue, candidates: Sequence[Venue]) -> Decision:
    for rule in RULES:
        decision = rule.evaluate(source, candidates)
        if decision is not None:
            return decision
    raise RuntimeError("La estrategia final debe producir una decisión.")
