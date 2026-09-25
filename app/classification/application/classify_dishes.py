from collections.abc import Iterable

from app.classification.domain.models import Classification, Dish, Taxonomy
from app.classification.domain.rules import classify


def classify_dishes(dishes: Iterable[Dish], taxonomy: Taxonomy) -> list[Classification]:
    return [classify(dish, taxonomy) for dish in dishes]
