from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

from app.db import connect
from app.executions.application.runs import finish_execution, output_path, start_execution


class ExecutionRunTest(unittest.TestCase):
    def test_keeps_a_repeated_input_as_a_new_execution(self):
        use_case = "execution-test"
        executions = []
        try:
            with TemporaryDirectory() as directory:
                source = Path(directory) / "source.json"
                source.write_text('{"venues": ["one"]}', encoding="utf-8")
                first = self._complete(use_case, source)
                second = self._complete(use_case, source)
                executions = [first, second]

            self.assertFalse(first.repeated_input)
            self.assertTrue(second.repeated_input)
            self.assertNotEqual(first.identifier, second.identifier)
            with connect() as connection:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT count(*) FROM analysis_executions WHERE use_case = %s", (use_case,))
                    self.assertEqual(cursor.fetchone()[0], 2)
        finally:
            self._clean(use_case, executions)

    def _complete(self, use_case: str, source: Path):
        execution = start_execution(use_case, {"source": source}, {})
        artifact = output_path(execution, "result.json")
        artifact.write_text("[]\n", encoding="utf-8")
        finish_execution(execution, artifact, {"processed": 1})
        return execution

    def _clean(self, use_case: str, executions) -> None:
        with connect() as connection:
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM execution_artifacts WHERE execution_id IN (SELECT execution_id FROM analysis_executions WHERE use_case = %s)", (use_case,))
                cursor.execute("DELETE FROM execution_metrics WHERE execution_id IN (SELECT execution_id FROM analysis_executions WHERE use_case = %s)", (use_case,))
                cursor.execute("DELETE FROM analysis_executions WHERE use_case = %s", (use_case,))
        for execution in executions:
            shutil.rmtree(execution.output_directory, ignore_errors=True)
