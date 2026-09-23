from dataclasses import dataclass


@dataclass(frozen=True)
class MenuSource:
    url: str
    cdn: dict
    details: dict
