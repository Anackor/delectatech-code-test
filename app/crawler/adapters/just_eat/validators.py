from decimal import Decimal


def text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field}: texto obligatorio ausente")
    return value


def list_of(value: object, field: str) -> list:
    if not isinstance(value, list):
        raise ValueError(f"{field}: se esperaba una lista")
    return value


def price(value: object) -> Decimal:
    if isinstance(value, bool) or not isinstance(value, (int, float, str)):
        raise ValueError("Precio ausente o no numérico")
    parsed = Decimal(str(value))
    if not parsed.is_finite() or parsed < 0:
        raise ValueError("Precio negativo o no finito")
    return parsed


def index(records: list) -> dict:
    result = {}
    for record in records:
        key = text(record["id"], "id")
        if key in result:
            raise ValueError(f"ID duplicado: {key}")
        result[key] = record
    return result
