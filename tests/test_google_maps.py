from unittest.mock import Mock, patch

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

from scrapers.google_maps import GoogleMapsScraper


class FakeBrowserManager:
    def __init__(self):
        self.page = Mock()


def test_search_retries_on_playwright_timeout():
    browser_manager = FakeBrowserManager()
    scraper = GoogleMapsScraper(browser_manager)

    browser_manager.page.goto.side_effect = [
        PlaywrightTimeoutError("temporary timeout"),
        Mock(),
    ]

    with patch("scrapers.google_maps.retry") as retry_mock:
        scraper.search(
            query="پیتزا",
            location="مشهد",
        )

        retry_mock.assert_called_once()

    assert scraper.search_keyword == "پیتزا"
    assert scraper.search_location == "مشهد"


def test_search_passes_timeout_exceptions_to_retry():
    browser_manager = FakeBrowserManager()
    scraper = GoogleMapsScraper(browser_manager)

    with patch("scrapers.google_maps.retry") as retry_mock:
        scraper.search(
            query="فست فود",
            location="مشهد",
        )

        kwargs = retry_mock.call_args.kwargs

        assert kwargs["retries"] == 2
        assert kwargs["delay"] == 2
        assert PlaywrightTimeoutError in kwargs["exceptions"]
        assert TimeoutError in kwargs["exceptions"]