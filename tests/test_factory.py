import pytest

from scrapers.factory import ScraperFactory
from scrapers.google_maps import GoogleMapsScraper
from scrapers.registry import ScraperRegistry


def test_factory_requires_registry():
    with pytest.raises(TypeError):
        ScraperFactory(None)


def test_factory_stores_registry():
    registry = ScraperRegistry()

    factory = ScraperFactory(registry)

    assert factory.registry is registry


def test_factory_creates_registered_scraper():
    registry = ScraperRegistry()

    registry.register(
        "google_maps",
        GoogleMapsScraper,
    )

    factory = ScraperFactory(registry)

    browser_manager = object()

    scraper = factory.create(
        "google_maps",
        browser_manager=browser_manager,
    )

    assert isinstance(
        scraper,
        GoogleMapsScraper,
    )

    assert scraper.browser_manager is browser_manager


def test_factory_propagates_unknown_source():
    registry = ScraperRegistry()
    factory = ScraperFactory(registry)

    with pytest.raises(KeyError):
        factory.create(
            "unknown",
            browser_manager=object(),
        )


def test_factory_passes_dependencies():
    registry = ScraperRegistry()

    registry.register(
        "google_maps",
        GoogleMapsScraper,
    )

    factory = ScraperFactory(registry)

    browser_manager = object()

    scraper = factory.create(
        "google_maps",
        browser_manager=browser_manager,
    )

    assert scraper.browser_manager is browser_manager