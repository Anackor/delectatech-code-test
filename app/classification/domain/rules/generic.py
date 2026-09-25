from app.classification.domain.models import Dish, Taxonomy

from .strategy import ClassificationRule
from .text import contains


PARENT_SIGNALS = {
    "bebida": "other drink", "drink": "other drink", "entrante": "entrees", "tapa": "entrees",
    "pasta": "pasta", "arroz": "rice", "postre": "sweets", "postres": "sweets", "dulce": "sweets", "helado": "ice cream",
    "pescado": "fish & seafood", "marisco": "fish & seafood", "carne": "meat", "verdura": "vegetables",
}


class GenericSectionRule(ClassificationRule):
    def classify(self, dish: Dish, taxonomy: Taxonomy):
        for signal, parent in PARENT_SIGNALS.items():
            category = taxonomy.generic_for_parent(parent)
            if category and contains(dish.section_name, signal):
                return category, signal
        return None
