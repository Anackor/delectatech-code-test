import os
import unittest

from app.db import connect


class DatabaseTest(unittest.TestCase):
    def test_app_connects_to_postgres(self):
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT current_database()")
                self.assertEqual(cursor.fetchone()[0], os.environ["DB_NAME"])
