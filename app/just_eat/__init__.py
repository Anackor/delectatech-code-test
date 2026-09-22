"""Reglas y contrato de Just Eat independientes de infraestructura."""

from .errors import CrawlError
from .mapper import to_venue
from .source import MenuSource
from .url import validate_url

__all__ = ["CrawlError", "MenuSource", "to_venue", "validate_url"]
