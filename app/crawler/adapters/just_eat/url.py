import re
from urllib.parse import urlsplit

from app.crawler.application.errors import CrawlError


def validate_url(url: str) -> str:
    """Aceptar únicamente páginas de menú públicas de Just Eat España."""
    try:
        parsed = urlsplit(url)
        valid = (
            parsed.scheme in {"http", "https"}
            and parsed.hostname in {"just-eat.es", "www.just-eat.es"}
            and parsed.port is None
            and parsed.username is None
            and parsed.password is None
            and not parsed.query
            and not parsed.fragment
            and re.fullmatch(r"/restaurants-[a-z0-9-]+/menu/?", parsed.path)
        )
    except ValueError:
        valid = False
    if not valid:
        raise CrawlError("invalid_url", "Se requiere una URL de menú de www.just-eat.es sin parámetros.")
    return "https://www.just-eat.es" + parsed.path.rstrip("/")
