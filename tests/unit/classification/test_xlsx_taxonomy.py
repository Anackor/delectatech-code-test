from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from openpyxl import Workbook

from app.classification.adapters.xlsx_taxonomy import HEADERS, read_categories, read_taxonomy


class XlsxTaxonomyTest(unittest.TestCase):
    def test_reads_boolean_values_without_treating_false_as_true(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "categories.xlsx"
            _workbook(path, [HEADERS, ("category-1", "food", "pizza", "pizza", "false")])

            categories = read_categories(path)

        self.assertFalse(categories[0].is_generic_or_other)

    def test_rejects_duplicate_identifiers(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "categories.xlsx"
            _workbook(path, [HEADERS, ("category-1", "food", "pizza", "pizza", False),
                             ("category-1", "food", "burger", "fast food", False)])

            with self.assertRaisesRegex(ValueError, "duplicados"):
                read_categories(path)

    def test_rejects_duplicate_category_names(self):
        with TemporaryDirectory() as directory:
            path = Path(directory) / "categories.xlsx"
            _workbook(path, [HEADERS, ("category-1", "food", "pizza", "pizza", False),
                             ("category-2", "food", "pizza", "fast food", False)])

            with self.assertRaisesRegex(ValueError, "nombres de categoría duplicados"):
                read_taxonomy(path)


def _workbook(path: Path, rows: list[tuple]) -> None:
    workbook = Workbook()
    sheet = workbook.active
    for row in rows:
        sheet.append(row)
    workbook.save(path)
    workbook.close()
