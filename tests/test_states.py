from core.states import ScraperState
from scrapers.base import BaseScraper


class FakeScraper(BaseScraper):
    def search(self, query, location):
        self.set_state(ScraperState.SEARCHING)

    def scrape(self):
        self.set_state(ScraperState.EXTRACTING)
        self.set_state(ScraperState.COMPLETED)
        return []


def test_scraper_state_values():
    assert ScraperState.INITIALIZING.value == "INITIALIZING"
    assert ScraperState.SEARCHING.value == "SEARCHING"
    assert ScraperState.LOADING.value == "LOADING"
    assert ScraperState.SCROLLING.value == "SCROLLING"
    assert ScraperState.EXTRACTING.value == "EXTRACTING"
    assert ScraperState.PROCESSING.value == "PROCESSING"
    assert ScraperState.COMPLETED.value == "COMPLETED"
    assert ScraperState.FAILED.value == "FAILED"


def test_base_scraper_starts_in_initializing_state():
    scraper = FakeScraper(browser_manager=None)

    assert scraper.state == ScraperState.INITIALIZING


def test_scraper_state_can_change():
    scraper = FakeScraper(browser_manager=None)

    scraper.set_state(ScraperState.SEARCHING)

    assert scraper.state == ScraperState.SEARCHING


def test_invalid_scraper_state_is_rejected():
    scraper = FakeScraper(browser_manager=None)

    try:
        scraper.set_state("SEARCHING")
    except ValueError:
        return

    assert False, "Expected ValueError"