from dataclasses import dataclass


@dataclass(frozen=True)
class Venue:
    source: str
    identifier: str
    name: str
    normalized_name: str
    address: str | None
    normalized_address: str
    postal_code: str | None
    latitude: float | None
    longitude: float | None
    telephone: str | None = None
    provider_url: str | None = None
    cuisines: tuple[str, ...] = ()


@dataclass(frozen=True)
class Candidate:
    venue: Venue
    distance_meters: float | None
    distance_score: float | None
    name_score: float
    address_score: float
    score: float


@dataclass(frozen=True)
class Decision:
    just_eat_id: str
    status: str
    candidate: Candidate | None
    runner_up: Candidate | None
    reason: str
    proposals: tuple[Candidate, ...] = ()
