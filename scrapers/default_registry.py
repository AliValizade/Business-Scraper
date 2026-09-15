from scrapers.google_maps import GoogleMapsScraper
from scrapers.registry import ScraperRegistry


def create_default_registry():
    """Create and configure the default scraper registry."""
    registry = ScraperRegistry()

    registry.register(
        "google_maps",
        GoogleMapsScraper,
    )

    return registry