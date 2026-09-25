from decimal import Decimal

from app.classification.domain.models import Category, Dish, Taxonomy


def category(name: str, *, generic: bool = False, parent: str = "parent") -> Category:
    return Category(f"id-{name}", "food", name, parent, generic)


def dish(name: str, *, description: str = "", section: str = "", price: Decimal | None = None,
         cuisines: tuple[str, ...] = ()) -> Dish:
    return Dish("je-1", "menu-1", "section-1", "item-1", name, description, section, price, cuisines)


def taxonomy(*categories: Category) -> Taxonomy:
    return Taxonomy(categories)
