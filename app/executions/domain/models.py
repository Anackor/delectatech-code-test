from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Execution:
    identifier: str
    use_case: str
    input_fingerprint: str
    output_directory: Path
    repeated_input: bool
