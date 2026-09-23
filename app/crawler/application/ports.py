from collections.abc import Callable
from pathlib import Path

from .models import CrawlCapture

FetchVenue = Callable[[str], CrawlCapture]
SaveVenue = Callable[[Path, dict], None]
