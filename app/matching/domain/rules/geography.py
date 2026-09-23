from collections import defaultdict
from collections.abc import Iterable
import math

from app.matching.domain.models import Venue
from .metrics import distance_meters


CELL_SIZE = 0.01
MAX_DISTANCE_METERS = 1_000


def build_index(venues: Iterable[Venue]) -> tuple[dict, dict]:
    grid, postal_codes = defaultdict(list), defaultdict(list)
    for venue in venues:
        if venue.latitude is not None and venue.longitude is not None:
            grid[_cell(venue.latitude, venue.longitude)].append(venue)
        if venue.postal_code:
            postal_codes[venue.postal_code].append(venue)
    return grid, postal_codes


def candidates_for(source: Venue, grid: dict, postal_codes: dict) -> list[Venue]:
    candidates = _nearby(source, grid) if source.latitude is not None else postal_codes.get(source.postal_code, [])
    return [candidate for candidate in candidates
            if (distance := distance_meters(source, candidate)) is None or distance <= MAX_DISTANCE_METERS]


def _nearby(venue: Venue, grid: dict) -> list[Venue]:
    cell = _cell(venue.latitude, venue.longitude)
    return [candidate for latitude in range(cell[0] - 1, cell[0] + 2)
            for longitude in range(cell[1] - 1, cell[1] + 2)
            for candidate in grid.get((latitude, longitude), [])]


def _cell(latitude: float, longitude: float) -> tuple[int, int]:
    return math.floor(latitude / CELL_SIZE), math.floor(longitude / CELL_SIZE)
