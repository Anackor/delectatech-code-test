from app.classification.domain.models import Dish, Taxonomy

from .aliases import ALIASES
from .strategy import ClassificationRule
from .text import contains


class AliasRule(ClassificationRule):
    def __init__(self, field: str):
        self.field = field

    def classify(self, dish: Dish, taxonomy: Taxonomy):
        text = getattr(dish, self.field)
        for category_name, aliases in ALIASES.items():
            category = taxonomy.category(category_name)
            if category:
                alias = next((value for value in aliases if contains(text, value)), None)
                if alias:
                    return category, alias
        return None
