from psycopg.errors import UndefinedTable

from app.db import connect


def matching_summary() -> dict | None:
    try:
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT COUNT(*),
                                          COUNT(*) FILTER (WHERE status = 'matched'),
                                          COUNT(*) FILTER (WHERE status = 'ambiguous'),
                                          COUNT(*) FILTER (WHERE status = 'unmatched'),
                                          AVG(score) FILTER (WHERE score IS NOT NULL)
                                   FROM restaurant_matches""")
                total, matched, ambiguous, unmatched, average_score = cursor.fetchone()
        return {"total": total, "matched": matched, "ambiguous": ambiguous, "unmatched": unmatched,
                "averageScore": float(average_score) if average_score is not None else None}
    except UndefinedTable:
        return None


def classification_summary() -> dict | None:
    try:
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("""SELECT COUNT(*),
                                          COUNT(*) FILTER (WHERE dish.status = 'classified'),
                                          COUNT(*) FILTER (WHERE dish.status = 'review'),
                                          COUNT(*) FILTER (WHERE category.is_generic_or_other)
                                   FROM dish_classifications dish
                                   LEFT JOIN food_categories category
                                     ON category.uidentifier = dish.category_uidentifier""")
                total, classified, review, generic = cursor.fetchone()
                cursor.execute("""SELECT category.name, COUNT(*)
                                   FROM dish_classifications dish
                                   JOIN food_categories category
                                     ON category.uidentifier = dish.category_uidentifier
                                   WHERE dish.status = 'classified'
                                   GROUP BY category.name
                                   ORDER BY COUNT(*) DESC, category.name
                                   LIMIT 10""")
                categories = [{"category": name, "dishes": count} for name, count in cursor.fetchall()]
        return {"total": total, "classified": classified, "review": review, "generic": generic,
                "categories": categories}
    except UndefinedTable:
        return None
