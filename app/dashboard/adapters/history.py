from app.db import connect
from app.executions.adapters.postgres import SCHEMA


def executions(use_case: str) -> list[dict]:
    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(SCHEMA)
            cursor.execute("""SELECT execution_id::text, status, parameters, started_at, finished_at, error
                              FROM analysis_executions WHERE use_case = %s ORDER BY started_at DESC""", (use_case,))
            rows = cursor.fetchall()
            return [_execution(cursor, row) for row in rows]


def _execution(cursor, row: tuple) -> dict:
    identifier, status, parameters, started_at, finished_at, error = row
    cursor.execute("SELECT name, value FROM execution_metrics WHERE execution_id = %s", (identifier,))
    metrics = dict(cursor.fetchall())
    cursor.execute("SELECT name, path FROM execution_artifacts WHERE execution_id = %s", (identifier,))
    artifact = cursor.fetchone()
    return {"id": identifier, "status": status, "parameters": parameters, "startedAt": started_at,
            "finishedAt": finished_at, "error": error, "metrics": metrics,
            "artifact": {"name": artifact[0], "path": artifact[1]} if artifact else None}
