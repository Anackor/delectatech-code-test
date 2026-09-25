from app.classification.domain.models import Dish, Taxonomy

from .strategy import ClassificationRule
from .text import contains


SECTION_CATEGORIES = {
    "pizza": ("pizza", "pizzas"),
    "tapas": ("tapa", "tapas"),
    "soft drinks": ("refresco", "refrescos", "soft drink", "soft drinks"),
    "beer": ("cerveza", "cervezas", "beer", "beers"),
    "sandwich": ("sandwich", "sandwiches", "bocadillo", "bocadillos"),
    "tintos": ("vino tinto", "vinos tintos", "red wine", "red wines"),
    "blancos": ("vino blanco", "vinos blancos", "white wine", "white wines"),
    "rosados": ("vino rosado", "vinos rosados", "rose wine", "rosé wine"),
    "espumosos": ("cava", "champagne", "champan", "sparkling wine"),
    "ice cream": ("helado", "helados", "gelat", "gelats", "ice cream"),
    "toasts": ("tostada", "tostadas", "torrada", "torradas", "toast", "toasts"),
    "kebab": ("durum", "durums"),
    "pastries": ("bolleria", "bakery"),
}

SECTION_PARENTS = {
    "other drink": ("bebida", "bebidas", "beguda", "begudes", "drink", "drinks"),
    "entrees": ("entrante", "entrantes", "entrant", "entrants", "starter", "starters", "appetizer", "appetizers"),
    "fish & seafood": ("pescado", "pescados", "fish", "marisco", "mariscos", "seafood"),
    "vegetables": ("verdura", "verduras", "verdures", "vegetable", "vegetables"),
    "sweets": ("postre", "postres", "dolç", "dolcos", "dessert", "desserts"),
    "wines": ("vino", "vinos", "wine", "wines"),
}


class SectionRule(ClassificationRule):
    def classify(self, dish: Dish, taxonomy: Taxonomy):
        for category_name, aliases in SECTION_CATEGORIES.items():
            if category := taxonomy.category(category_name):
                alias = next((value for value in aliases if contains(dish.section_name, value)), None)
                if alias:
                    return category, alias
        for parent, aliases in SECTION_PARENTS.items():
            if category := taxonomy.generic_for_parent(parent):
                alias = next((value for value in aliases if contains(dish.section_name, value)), None)
                if alias:
                    return category, alias
        return None
