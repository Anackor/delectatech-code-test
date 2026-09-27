import hashlib
import json
from pathlib import Path
from uuid import uuid4

from app.executions.adapters import postgres
from app.executions.domain.models import Execution


def start_execution(use_case: str, inputs: dict[str, str | Path], parameters: dict) -> Execution:
    manifest = {name: _input_manifest(value) for name, value in inputs.items()}
    fingerprint = _hash(json.dumps(manifest, sort_keys=True).encode())
    identifier = str(uuid4())
    repeated = postgres.start(identifier, use_case, fingerprint, manifest, parameters)
    directory = Path("output") / "runs" / identifier
    directory.mkdir(parents=True, exist_ok=False)
    return Execution(identifier, use_case, fingerprint, directory, repeated)


def finish_execution(execution: Execution, output: Path, metrics: dict[str, int]) -> None:
    checksum = _file_hash(output)
    postgres.succeed(execution.identifier, metrics, (output.name, checksum, output.stat().st_size))
    (execution.output_directory / "manifest.json").write_text(json.dumps({
        "executionId": execution.identifier,
        "useCase": execution.use_case,
        "inputFingerprint": execution.input_fingerprint,
        "metrics": metrics,
        "artifact": output.name,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def fail_execution(execution: Execution, error: Exception) -> None:
    postgres.fail(execution.identifier, str(error))


def output_path(execution: Execution, name: str) -> Path:
    return execution.output_directory / name


def _input_manifest(value: str | Path) -> dict:
    if isinstance(value, Path):
        return {"path": str(value), "sha256": _file_hash(value), "sizeBytes": value.stat().st_size}
    return {"value": value, "sha256": _hash(value.encode())}


def _file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1_048_576), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _hash(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()
