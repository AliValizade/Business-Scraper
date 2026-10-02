from scrapers.google_maps import GoogleMapsScraper
from scrapers.neshan import NeshanScraper
from scrapers.registry import ScraperRegistry


def create_default_registry():
    """Create and configure the default scraper registry."""
    registry = ScraperRegistry()

    registry.register(
        "google_maps",
        GoogleMapsScraper,
    )

    registry.register(
        "neshan",
        NeshanScraper,
    )

    return registry