from collections.abc import Iterable

from psycopg.errors import UndefinedTable

from app.classification.domain.models import Category, Classification
from app.db import connect


SCHEMA = """
CREATE TABLE IF NOT EXISTS food_categories (
    uidentifier TEXT PRIMARY KEY,
    family TEXT NOT NULL,
    name TEXT NOT NULL,
    parent TEXT NOT NULL,
    is_generic_or_other BOOLEAN NOT NULL
);
CREATE TABLE IF NOT EXISTS dish_classifications (
    just_eat_id TEXT NOT NULL REFERENCES just_eat_venues(just_eat_id),
    menu_id TEXT NOT NULL,
    section_id TEXT NOT NULL,
    item_id TEXT NOT NULL,
    item_name TEXT NOT NULL,
    item_description TEXT NOT NULL,
    section_name TEXT NOT NULL,
    price NUMERIC,
    status TEXT NOT NULL CHECK (status IN ('classified', 'review')),
    category_uidentifier TEXT REFERENCES food_categories(uidentifier),
    rule TEXT NOT NULL,
    evidence TEXT NOT NULL,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (just_eat_id, menu_id, section_id, item_id)
);
"""


def matched_restaurants() -> dict[str, str]:
    try:
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT just_eat_id, google_place_id FROM restaurant_matches WHERE status = 'matched'")
                return dict(cursor.fetchall())
    except UndefinedTable as exc:
        raise ValueError("No hay resultados de matching; ejecuta make match antes de make classify") from exc


def save_classifications(categories: Iterable[Category], classifications: Iterable[Classification], restaurant_ids: Iterable[str]) -> None:
    classifications = list(classifications)
    restaurant_ids = list(restaurant_ids)
    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(SCHEMA)
            cursor.executemany(
                """INSERT INTO food_categories (uidentifier, family, name, parent, is_generic_or_other)
                   VALUES (%s, %s, %s, %s, %s)
                   ON CONFLICT (uidentifier) DO UPDATE SET family = EXCLUDED.family, name = EXCLUDED.name,
                   parent = EXCLUDED.parent, is_generic_or_other = EXCLUDED.is_generic_or_other""",
                [(category.uidentifier, category.family, category.name, category.parent, category.is_generic_or_other)
                 for category in categories],
            )
            cursor.execute("DELETE FROM dish_classifications WHERE just_eat_id = ANY(%s)", (restaurant_ids,))
            cursor.execute("""DELETE FROM dish_classifications classified
                            WHERE NOT EXISTS (SELECT 1 FROM restaurant_matches matched
                                              WHERE matched.just_eat_id = classified.just_eat_id
                                              AND matched.status = 'matched')""")
            cursor.executemany(
                """INSERT INTO dish_classifications
                   (just_eat_id, menu_id, section_id, item_id, item_name, item_description, section_name, price,
                    status, category_uidentifier, rule, evidence)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                [_row(classification) for classification in classifications],
            )


def _row(classification: Classification) -> tuple:
    dish, category = classification.dish, classification.category
    return (dish.just_eat_id, dish.menu_id, dish.section_id, dish.item_id, dish.name, dish.description,
            dish.section_name, dish.price, classification.status,
            category.uidentifier if category else None, classification.rule, classification.evidence)
