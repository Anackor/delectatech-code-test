from dataclasses import dataclass


@dataclass(frozen=True)
class CrawlCapture:
    """Resultado canónico de un proveedor, independiente de su formato de origen."""

    url: str
    menu_version: str | None
    venue: dict
