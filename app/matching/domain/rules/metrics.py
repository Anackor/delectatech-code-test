import math
import re
import unicodedata

from app.matching.domain.models import Venue


def normalize(value: object) -> str:
    if not isinstance(value, str):
        return ""
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    without_accents = "".join(char for char in decomposed if not unicodedata.combining(char))
    return " ".join(re.sub(r"[^a-z0-9]+", " ", without_accents).split())


def distance_meters(left: Venue, right: Venue) -> float | None:
    if None in (left.latitude, left.longitude, right.latitude, right.longitude):
        return None
    latitude_1, longitude_1, latitude_2, longitude_2 = map(math.radians, (left.latitude, left.longitude, right.latitude, right.longitude))
    arc = math.sin((latitude_2 - latitude_1) / 2) ** 2 + math.cos(latitude_1) * math.cos(latitude_2) * math.sin((longitude_2 - longitude_1) / 2) ** 2
    return 6_371_000 * 2 * math.asin(math.sqrt(arc))
