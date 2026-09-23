from app.matching.domain.models import Venue
from app.matching.domain.rules import normalize


def venue(identifier: str, name: str, latitude: float | None = 41.4, longitude: float | None = 2.1,
          address: str = "Calle Uno 1", postal_code: str = "08001", source: str = "just_eat") -> Venue:
    return Venue(source, identifier, name, normalize(name), address, normalize(address), postal_code, latitude, longitude)
