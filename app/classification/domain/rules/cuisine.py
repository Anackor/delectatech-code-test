from app.classification.domain.models import Dish, Taxonomy

from .strategy import ClassificationRule
from .text import contains


CUISINE_SIGNALS = (
    (("japonesa", "sushi", "asiatica"), "sushi", ("maki", "nigiri", "sashimi", "uramaki", "temaki")),
    (("italiana", "pasta"), "pasta varieties", ("carbonara", "bolognesa", "pesto", "ravioli", "gnocchi")),
    (("china", "asiatica"), "noodles", ("chow mein", "yakisoba", "wok")),
)


class RestaurantCuisineRule(ClassificationRule):
    def classify(self, dish: Dish, taxonomy: Taxonomy):
        text = " ".join((dish.name, dish.section_name))
        for cuisines, category_name, signals in CUISINE_SIGNALS:
            cuisine = next((value for value in dish.restaurant_cuisines if any(contains(value, expected) for expected in cuisines)), None)
            signal = next((value for value in signals if contains(text, value)), None)
            category = taxonomy.category(category_name)
            if cuisine and signal and category:
                return category, f"{cuisine}:{signal}"
        return None
