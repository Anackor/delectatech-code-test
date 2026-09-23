import random
from collections.abc import Iterable

from app.matching.domain.models import Venue


def select_pack(venues: Iterable[Venue], size: int, seed: int | None) -> tuple[list[Venue], int]:
    if size < 1:
        raise ValueError("El tamaño del pack debe ser mayor que cero.")
    generator = random.Random(seed)
    pack: list[Venue] = []
    total = 0
    for total, venue in enumerate(venues, start=1):
        if len(pack) < size:
            pack.append(venue)
        else:
            replacement = generator.randrange(total)
            if replacement < size:
                pack[replacement] = venue
    return pack, total
