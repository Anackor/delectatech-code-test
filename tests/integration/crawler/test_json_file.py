import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from app.crawler.adapters.json_file import write_json


class JsonFileTest(unittest.TestCase):
    def test_writes_complete_json(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "venue.json"
            write_json(output, {"name": "Demo", "menus": {}})

            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), {"name": "Demo", "menus": {}})

    def test_keeps_previous_output_when_serialization_fails(self):
        with TemporaryDirectory() as directory:
            output = Path(directory) / "venue.json"
            output.write_text('{"previous": true}\n', encoding="utf-8")

            with self.assertRaises(TypeError):
                write_json(output, {"not_serializable": {"set"}})

            self.assertEqual(json.loads(output.read_text(encoding="utf-8")), {"previous": True})
            self.assertEqual(list(Path(directory).glob(".crawl-*.tmp")), [])
