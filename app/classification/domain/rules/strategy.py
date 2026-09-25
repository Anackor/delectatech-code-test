from typing import Protocol

from app.classification.domain.models import Category, Dish, Taxonomy


class ClassificationRule(Protocol):
    def classify(self, dish: Dish, taxonomy: Taxonomy) -> tuple[Category, str] | None: ...
