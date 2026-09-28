from uuid import uuid4
import unittest

from app.classification.adapters.postgres import SCHEMA as CLASSIFICATION_SCHEMA
from app.dashboard.adapters.insights import classification_summary, matching_summary
from app.db import connect
from app.matching.adapters.postgres import SCHEMA as MATCHING_SCHEMA


class DashboardInsightsTest(unittest.TestCase):
    def test_calculates_matching_and_classification_indicators(self):
        suffix = uuid4().hex
        matched_id, unmatched_id = f"dashboard-matched-{suffix}", f"dashboard-unmatched-{suffix}"
        google_id, category_id, category_name = f"google-{suffix}", f"category-{suffix}", f"Dashboard {suffix}"
        baseline = matching_summary() or {"total": 0, "matched": 0}
        classification_baseline = classification_summary() or {"total": 0, "classified": 0, "review": 0}
        try:
            self._insert_fixture(matched_id, unmatched_id, google_id, category_id, category_name)

            matching = matching_summary()
            self.assertEqual(matching["total"], baseline["total"] + 2)
            self.assertEqual(matching["matched"], baseline["matched"] + 1)
            classification = classification_summary()
            self.assertEqual(classification["total"], classification_baseline["total"] + 2)
            self.assertEqual(classification["classified"], classification_baseline["classified"] + 1)
            self.assertEqual(classification["review"], classification_baseline["review"] + 1)
            self.assertLessEqual(len(classification["categories"]), 10)
        finally:
            self._delete_fixture(matched_id, unmatched_id, google_id, category_id)

    def _insert_fixture(self, matched_id: str, unmatched_id: str, google_id: str,
                        category_id: str, category_name: str) -> None:
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute(MATCHING_SCHEMA)
                cursor.execute(CLASSIFICATION_SCHEMA)
                cursor.executemany("INSERT INTO just_eat_venues (just_eat_id, name) VALUES (%s, %s)",
                                   [(matched_id, "Matched"), (unmatched_id, "Unmatched")])
                cursor.execute("INSERT INTO google_venues (google_place_id, name) VALUES (%s, %s)",
                               (google_id, "Google"))
                cursor.executemany("""INSERT INTO restaurant_matches
                                      (just_eat_id, google_place_id, status, score)
                                      VALUES (%s, %s, %s, %s)""",
                                   [(matched_id, google_id, "matched", 90),
                                    (unmatched_id, None, "unmatched", 40)])
                cursor.execute("""INSERT INTO food_categories
                                  (uidentifier, family, name, parent, is_generic_or_other)
                                  VALUES (%s, 'food', %s, %s, false)""",
                               (category_id, category_name, category_name))
                cursor.executemany("""INSERT INTO dish_classifications
                                      (just_eat_id, menu_id, section_id, item_id, item_name, item_description,
                                       section_name, status, category_uidentifier, rule, evidence)
                                      VALUES (%s, 'menu', 'section', %s, %s, '', '', %s, %s, 'test', 'test')""",
                                   [(matched_id, "classified", "Pizza", "classified", category_id),
                                    (matched_id, "review", "Unknown", "review", None)])

    def _delete_fixture(self, matched_id: str, unmatched_id: str, google_id: str, category_id: str) -> None:
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM dish_classifications WHERE just_eat_id IN (%s, %s)",
                               (matched_id, unmatched_id))
                cursor.execute("DELETE FROM restaurant_matches WHERE just_eat_id IN (%s, %s)",
                               (matched_id, unmatched_id))
                cursor.execute("DELETE FROM food_categories WHERE uidentifier = %s", (category_id,))
                cursor.execute("DELETE FROM just_eat_venues WHERE just_eat_id IN (%s, %s)",
                               (matched_id, unmatched_id))
                cursor.execute("DELETE FROM google_venues WHERE google_place_id = %s", (google_id,))
