import re
import unicodedata


def normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    return " ".join("".join(character for character in decomposed if not unicodedata.combining(character)).split())


def contains(text: str, value: str) -> bool:
    normalized_value = normalize(value)
    return bool(normalized_value and re.search(rf"(?<!\w){re.escape(normalized_value)}(?!\w)", normalize(text)))
