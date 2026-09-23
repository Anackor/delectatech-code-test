import os
import unittest

from app.db import connect


class DatabaseConnectionTest(unittest.TestCase):
    def test_connects_to_configured_database(self):
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("SELECT current_database()")
                self.assertEqual(cursor.fetchone()[0], os.environ["DB_NAME"])
