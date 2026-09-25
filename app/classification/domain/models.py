from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Category:
    uidentifier: str
    family: str
    name: str
    parent: str
    is_generic_or_other: bool


@dataclass(frozen=True)
class Dish:
    just_eat_id: str
    menu_id: str
    section_id: str
    item_id: str
    name: str
    description: str
    section_name: str
    price: Decimal | None
    restaurant_cuisines: tuple[str, ...] = ()


@dataclass(frozen=True)
class Taxonomy:
    categories: tuple[Category, ...]

    def __post_init__(self):
        names = [category.name for category in self.categories]
        if len(names) != len(set(names)):
            raise ValueError("La taxonomía contiene nombres de categoría duplicados")

    def category(self, name: str) -> Category | None:
        return next((category for category in self.categories if category.name == name), None)

    def generic_for_parent(self, parent: str) -> Category | None:
        categories = tuple(category for category in self.categories
                           if category.parent == parent and category.is_generic_or_other)
        return next((category for category in categories if category.name == f"generic {parent}"),
                    categories[0] if categories else None)


@dataclass(frozen=True)
class Classification:
    dish: Dish
    status: str
    category: Category | None
    rule: str
    evidence: str
