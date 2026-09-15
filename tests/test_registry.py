import pytest

from scrapers.base import BaseScraper
from scrapers.registry import ScraperRegistry


class FakeScraper(BaseScraper):
    def search(self, query, location):
        return None

    def scrape(self):
        return []


class AnotherFakeScraper(BaseScraper):
    def search(self, query, location):
        return None

    def scrape(self):
        return []


class NotAScraper:
    pass


class FakeBrowserManager:
    pass


def test_registry_starts_empty():
    registry = ScraperRegistry()

    assert registry.sources() == ()


def test_registry_registers_scraper():
    registry = ScraperRegistry()

    registry.register(
        "fake",
        FakeScraper,
    )

    assert registry.sources() == ("fake",)


def test_registry_get_returns_registered_scraper():
    registry = ScraperRegistry()

    registry.register(
        "fake",
        FakeScraper,
    )

    scraper_class = registry.get("fake")

    assert scraper_class is FakeScraper


def test_registry_creates_scraper_instance():
    registry = ScraperRegistry()

    registry.register(
        "fake",
        FakeScraper,
    )

    browser_manager = FakeBrowserManager()

    scraper = registry.create(
        "fake",
        browser_manager=browser_manager,
    )

    assert isinstance(
        scraper,
        FakeScraper,
    )

    assert scraper.browser_manager is browser_manager


def test_registry_has_registered_source():
    registry = ScraperRegistry()

    registry.register(
        "fake",
        FakeScraper,
    )

    assert registry.has("fake") is True
    assert registry.has("unknown") is False


def test_registry_rejects_duplicate_source():
    registry = ScraperRegistry()

    registry.register(
        "fake",
        FakeScraper,
    )

    with pytest.raises(
        ValueError,
        match="already registered",
    ):
        registry.register(
            "fake",
            AnotherFakeScraper,
        )


def test_registry_rejects_unknown_source():
    registry = ScraperRegistry()

    with pytest.raises(
        KeyError,
        match="No scraper registered",
    ):
        registry.get("unknown")


def test_registry_rejects_invalid_scraper_class():
    registry = ScraperRegistry()

    with pytest.raises(
        TypeError,
        match="inherit from BaseScraper",
    ):
        registry.register(
            "invalid",
            NotAScraper,
        )


def test_registry_normalizes_source_name():
    registry = ScraperRegistry()

    registry.register(
        "  google_maps  ",
        FakeScraper,
    )

    assert registry.has("google_maps") is True
    assert registry.get("google_maps") is FakeScraper