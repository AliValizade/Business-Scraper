import pytest

from scrapers.default_registry import create_default_registry
from scrapers.google_maps import GoogleMapsScraper


def test_create_default_registry():
    registry = create_default_registry()

    assert registry is not None


def test_default_registry_has_google_maps():
    registry = create_default_registry()

    assert registry.has("google_maps") is True


def test_default_registry_returns_google_maps_scraper_class():
    registry = create_default_registry()

    scraper_class = registry.get("google_maps")

    assert scraper_class is GoogleMapsScraper


def test_default_registry_can_create_google_maps_scraper():
    registry = create_default_registry()

    browser_manager = object()

    scraper = registry.create(
        "google_maps",
        browser_manager=browser_manager,
    )

    assert isinstance(scraper, GoogleMapsScraper)
    assert scraper.browser_manager is browser_manager


def test_default_registry_sources():
    registry = create_default_registry()

    assert registry.sources() == ("google_maps",)