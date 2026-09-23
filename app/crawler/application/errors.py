class CrawlError(Exception):
    """Fallo identificable durante la captura de un restaurante."""

    def __init__(self, code: str, message: str):
        super().__init__(message)
        self.code = code
