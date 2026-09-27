import json

from app.db import connect


SCHEMA = """
CREATE TABLE IF NOT EXISTS analysis_executions (
    execution_id UUID PRIMARY KEY,
    use_case TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('running', 'succeeded', 'failed')),
    input_fingerprint TEXT NOT NULL,
    inputs JSONB NOT NULL,
    parameters JSONB NOT NULL,
    started_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMPTZ,
    error TEXT
);
CREATE TABLE IF NOT EXISTS execution_metrics (
    execution_id UUID NOT NULL REFERENCES analysis_executions(execution_id),
    name TEXT NOT NULL,
    value NUMERIC NOT NULL,
    PRIMARY KEY (execution_id, name)
);
CREATE TABLE IF NOT EXISTS execution_artifacts (
    execution_id UUID NOT NULL REFERENCES analysis_executions(execution_id),
    name TEXT NOT NULL,
    path TEXT NOT NULL,
    sha256 TEXT NOT NULL,
    size_bytes BIGINT NOT NULL,
    PRIMARY KEY (execution_id, name)
);
"""


def start(identifier: str, use_case: str, fingerprint: str, inputs: dict, parameters: dict) -> bool:
    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute(SCHEMA)
            cursor.execute("""SELECT EXISTS(
                               SELECT 1 FROM analysis_executions
                               WHERE use_case = %s AND input_fingerprint = %s AND status = 'succeeded'
                           )""", (use_case, fingerprint))
            repeated = cursor.fetchone()[0]
            cursor.execute("""INSERT INTO analysis_executions
                              (execution_id, use_case, status, input_fingerprint, inputs, parameters)
                              VALUES (%s, %s, 'running', %s, %s::jsonb, %s::jsonb)""",
                           (identifier, use_case, fingerprint, json.dumps(inputs), json.dumps(parameters)))
    return repeated


def succeed(identifier: str, metrics: dict[str, int], artifact: tuple[str, str, int]) -> None:
    name, checksum, size = artifact
    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.executemany("INSERT INTO execution_metrics (execution_id, name, value) VALUES (%s, %s, %s)",
                               [(identifier, name, value) for name, value in metrics.items()])
            cursor.execute("""INSERT INTO execution_artifacts (execution_id, name, path, sha256, size_bytes)
                              VALUES (%s, %s, %s, %s, %s)""",
                           (identifier, name, f"output/runs/{identifier}/{name}", checksum, size))
            cursor.execute("UPDATE analysis_executions SET status = 'succeeded', finished_at = NOW() WHERE execution_id = %s",
                           (identifier,))


def fail(identifier: str, error: str) -> None:
    with connect() as connection:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE analysis_executions SET status = 'failed', finished_at = NOW(), error = %s WHERE execution_id = %s",
                           (error, identifier))
