from app.classification.domain.models import Classification, Dish, Taxonomy

from .alias import AliasRule
from .cuisine import RestaurantCuisineRule
from .generic import GenericSectionRule
from .section import SectionRule
from .strategy import ClassificationRule


RULES: tuple[ClassificationRule, ...] = (
    AliasRule("name"),
    SectionRule(),
    RestaurantCuisineRule(),
    AliasRule("description"),
    GenericSectionRule(),
)


def classify(dish: Dish, taxonomy: Taxonomy) -> Classification:
    for rule in RULES:
        if result := rule.classify(dish, taxonomy):
            category, evidence = result
            return Classification(dish, "classified", category, rule.__class__.__name__, evidence)
    return Classification(dish, "review", None, "insufficient_evidence", "")
