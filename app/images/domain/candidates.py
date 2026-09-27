import re
import unicodedata
from collections.abc import Iterable

from .models import Candidate, OcrLine


PRICE = re.compile("\\s+(?:\\d+[,.]\\d{1,2}|\\d+)\\s*(?:EUR|\\N{EURO SIGN})?\\s*$", re.IGNORECASE)
PRICE_ONLY = re.compile("^(?:\\d+[,.]\\d{1,2}|\\d+)\\s*(?:EUR|\\N{EURO SIGN})?$", re.IGNORECASE)
HEADERS = {"menu", "carta", "ofertas", "complementos", "pizzas", "ensaladas", "bebidas", "drinks"}
MAX_CANDIDATE_LENGTH = 180
NUMBERED_TITLE = re.compile(r"^\s*\d+\s*[.)-]?\s*(.+?)\s*:")
TITLE_WITH_DESCRIPTION = re.compile(r"^\s*(.+?)\s*:")


def extract_candidates(lines: Iterable[OcrLine]) -> tuple[Candidate, ...]:
    # ponytail: estas heuristicas solo separan titulos de OCR legible. En produccion
    # se delegaria la interpretacion en un extractor estructurado: OCR con posicion
    # mas un modelo de lenguaje que devuelva JSON validado (nombre, descripcion,
    # precio e ingredientes), siempre enlazando cada campo a sus lineas de evidencia.
    candidates = []
    for line in lines:
        text = " ".join(line.text.split())
        name = _candidate_name(text)
        if _is_candidate(name):
            candidates.append(Candidate(name, normalize_name(name), text, round(line.confidence, 1), line.bounding_box))
    return tuple(candidates)


def _candidate_name(text: str) -> str:
    without_price = PRICE.sub("", text).strip(" -:.")
    match = NUMBERED_TITLE.match(without_price) or TITLE_WITH_DESCRIPTION.match(without_price)
    if match:
        return match.group(1).strip(" -:.")
    if _is_short_uppercase_title(without_price):
        return without_price
    return ""


def _is_candidate(value: str) -> bool:
    normalized = value.casefold()
    letters = sum(character.isalpha() for character in value)
    return bool(value and len(value) <= MAX_CANDIDATE_LENGTH and letters >= 4
                and not PRICE_ONLY.fullmatch(value) and normalized not in HEADERS)


def _is_short_uppercase_title(value: str) -> bool:
    letters = [character for character in value if character.isalpha()]
    return bool(letters and len(value) <= 60 and len(value.split()) <= 7
                and sum(character.isupper() for character in letters) / len(letters) >= 0.7)


def is_reliable_candidate(candidate: Candidate) -> bool:
    words = re.findall(r"[^\W\d_]+", candidate.normalized_name, flags=re.UNICODE)
    return bool(words and any(len(word) >= 3 for word in words)
                and all(len(word) >= 3 or word == "a" for word in words))


def normalize_name(value: str) -> str:
    # ponytail: normalizacion mecanica para comparar sin reemplazar el original.
    # La correccion de errores OCR debe usar un catalogo del restaurante y reglas de
    # aceptacion; un LLM sin ese contexto podria inventar platos o ingredientes.
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    return " ".join("".join(character for character in decomposed
                               if not unicodedata.combining(character)).split())
