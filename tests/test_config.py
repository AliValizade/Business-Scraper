import config


def test_retry_configuration_exists():
    assert hasattr(config, "RETRY_COUNT")
    assert hasattr(config, "RETRY_DELAY")


def test_retry_configuration_values_are_valid():
    assert isinstance(config.RETRY_COUNT, int)
    assert config.RETRY_COUNT >= 0

    assert isinstance(config.RETRY_DELAY, (int, float))
    assert config.RETRY_DELAY >= 0


def test_scraper_uses_retry_configuration():
    from unittest.mock import patch

    from scrapers.google_maps import GoogleMapsScraper

    class FakeBrowserManager:
        def __init__(self):
            from unittest.mock import Mock

            self.page = Mock()

    scraper = GoogleMapsScraper(FakeBrowserManager())

    with patch("scrapers.google_maps.retry") as retry_mock:
        scraper.search(
            query="پیتزا",
            location="مشهد",
        )

        kwargs = retry_mock.call_args.kwargs

        assert kwargs["retries"] == config.RETRY_COUNT
        assert kwargs["delay"] == config.RETRY_DELAY