import json

import pytest

from core.states import ScraperState
from scrapers.neshan import NeshanAPIError, NeshanScraper
from scrapers.default_registry import create_default_registry


def make_http_get(responses):
    calls = []

    def http_get(url):
        calls.append(url)
        response = responses[len(calls) - 1]
        if isinstance(response, Exception):
            raise response
        return 200, json.dumps(response, ensure_ascii=False)

    http_get.calls = calls
    return http_get


def test_neshan_requires_api_key(monkeypatch):
    monkeypatch.delenv("NESHAN_API_KEY", raising=False)

    scraper = NeshanScraper(mode="api")

    with pytest.raises(ValueError, match="API key"):
        scraper.search("رستوران", "مشهد")


def test_neshan_search_builds_v3_query_and_maps_coordinates():
    responses = [
        {
            "items": [
                {
                    "location": {
                        "latitude": 36.297,
                        "longitude": 59.606,
                    }
                }
            ]
        },
        {
            "count": 1,
            "items": [
                {
                    "title": "رستوران نمونه",
                    "address": "مشهد، خیابان نمونه",
                    "category": "place",
                    "type": "restaurant",
                    "region": "مشهد، خراسان رضوی",
                    "neighbourhood": "نمونه",
                    "location": {
                        "x": 59.61,
                        "y": 36.29,
                    },
                    "poiHash": "hash-1",
                }
            ],
        },
        {
            "name": "رستوران نمونه",
            "address": "مشهد، خیابان نمونه، پلاک ۱",
            "phoneNumber": "05112345678",
            "website": "example.com",
            "layer": {"title": "رستوران"},
            "location": {"x": 59.61, "y": 36.29},
            "socialNetworks": [],
        },
    ]

    http_get = make_http_get(responses)

    scraper = NeshanScraper(
        api_key="test-key",
        http_get=http_get,
    mode="api",
    )

    scraper.search("رستوران", "مشهد")
    businesses = scraper.scrape()

    assert len(businesses) == 1
    assert businesses[0]["name"] == "رستوران نمونه"
    assert businesses[0]["source"] == "neshan"
    assert businesses[0]["source_id"] == "hash-1"
    assert businesses[0]["latitude"] == 36.29
    assert businesses[0]["longitude"] == 59.61
    assert businesses[0]["phone"] == "05112345678"
    assert businesses[0]["website"] == "example.com"

    query = json.loads(
        __import__("urllib.parse", fromlist=["urlparse"])
        .parse_qs(
            __import__("urllib.parse", fromlist=["urlparse"])
            .urlparse(http_get.calls[1]).query
        )["q"][0]
    )

    assert query["term"] == "رستوران"
    assert query["center"] == {
        "latitude": 36.297,
        "longitude": 59.606,
    }


def test_neshan_limits_results_to_thirty():
    items = [
        {
            "title": f"Business {index}",
            "address": "Address",
            "location": {"x": 51.0, "y": 35.0},
        }
        for index in range(50)
    ]

    http_get = make_http_get(
        [
            {
                "items": [
                    {
                        "location": {
                            "latitude": 35.0,
                            "longitude": 51.0,
                        }
                    }
                ]
            },
            {"count": 50, "items": items},
        ]
    )

    scraper = NeshanScraper(
        api_key="test-key",
        http_get=http_get,
    mode="api",
    )

    scraper.search("کافه", "تهران")

    assert len(scraper._businesses) == 30


def test_neshan_keeps_result_when_poi_enrichment_fails():
    responses = [
        {
            "items": [
                {
                    "location": {
                        "latitude": 35.7,
                        "longitude": 51.4,
                    }
                }
            ]
        },
        {
            "items": [
                {
                    "title": "کسب و کار",
                    "address": "تهران",
                    "location": {"x": 51.4, "y": 35.7},
                    "poiHash": "hash-1",
                }
            ]
        },
        NeshanAPIError(481, "limit exceeded"),
    ]

    http_get = make_http_get(responses)

    scraper = NeshanScraper(
        api_key="test-key",
        http_get=http_get,
    mode="api",
    )

    scraper.search("کسب و کار", "تهران")
    businesses = scraper.scrape()

    assert len(businesses) == 1
    assert businesses[0]["name"] == "کسب و کار"
    assert businesses[0]["phone"] is None


def test_neshan_maps_instagram_when_explicitly_identified():
    item = {
        "title": "Test",
        "address": "Address",
        "location": {"x": 51.4, "y": 35.7},
    }

    details = {
        "socialNetworks": [
            {
                "name": "instagram",
                "url": "https://instagram.com/example",
            }
        ]
    }

    scraper = NeshanScraper(api_key="test-key", mode="api")

    business = scraper._map_business(item, details)

    assert business["instagram"] == "https://instagram.com/example"


def test_neshan_registry_contains_source():
    registry = create_default_registry()

    assert registry.has("google_maps")
    assert registry.has("neshan")
    assert registry.get("neshan") is NeshanScraper


def test_neshan_invalid_http_status_raises():
    def http_get(_url):
        return 480, "{}"

    scraper = NeshanScraper(
        api_key="test-key",
        http_get=http_get,
    mode="api",
    )

    with pytest.raises(NeshanAPIError) as error:
        scraper._get_json("/v3/search", {"q": "{}"})

    assert error.value.status_code == 480


def test_neshan_search_failure_sets_failed_state():
    def http_get(_url):
        raise NeshanAPIError(482, "rate exceeded")

    scraper = NeshanScraper(
        api_key="test-key",
        http_get=http_get,
    mode="api",
    )

    with pytest.raises(NeshanAPIError):
        scraper.search("کافه", "تهران")

    assert scraper.state is ScraperState.FAILED

    
def test_neshan_defaults_to_web_mode():
    scraper = NeshanScraper()
    assert scraper.mode == "web"


def test_neshan_api_mode_requires_key(monkeypatch):
    monkeypatch.delenv("NESHAN_API_KEY", raising=False)
    scraper = NeshanScraper(mode="api")

    with pytest.raises(ValueError, match="API key"):
        scraper.search("رستوران", "مشهد")


def test_neshan_web_mode_combines_query_and_location():
    class FakeLocator:
        def __init__(self):
            self.filled = None
            self.pressed = None

        @property
        def first(self):
            return self

        def count(self):
            return 1

        def wait_for(self, **_kwargs):
            return None

        def fill(self, value):
            self.filled = value

        def press(self, value):
            self.pressed = value

    class FakePage:
        def __init__(self):
            self.url = ""
            self.input = FakeLocator()
            self.results = FakeLocator()

        def goto(self, url, **_kwargs):
            self.url = url

        def locator(self, selector):
            if selector == "input.AZLBjuP":
                return self.input
            return self.results

    class FakeBrowser:
        def __init__(self):
            self.page = FakePage()

    scraper = NeshanScraper(
        browser_manager=FakeBrowser(),
        mode="web",
    )

    scraper.search("فست فود", "مشهد")

    assert scraper.page.url == "https://neshan.org/maps/search"
    assert scraper.page.input.filled == "فست فود مشهد"
    assert scraper.page.input.pressed == "Enter"
    assert scraper.state is ScraperState.LOADING

def test_neshan_web_waits_for_client_rendered_search_input():
    class DelayedLocator:
        @property
        def first(self):
            return self

        def count(self):
            return 0

        def wait_for(self, **_kwargs):
            return None

        def fill(self, value):
            self.filled = value

        def press(self, value):
            self.pressed = value

    class FakePage:
        def __init__(self):
            self.url = ""
            self.input = DelayedLocator()
            self.results = DelayedLocator()

        def goto(self, url, **_kwargs):
            self.url = url

        def locator(self, selector):
            if selector == "input.AZLBjuP":
                return self.input
            return self.results

    class FakeBrowser:
        def __init__(self):
            self.page = FakePage()

    scraper = NeshanScraper(
        browser_manager=FakeBrowser(),
        mode="web",
    )

    scraper.search("فست فود", "تبریز")

    assert scraper.page.input.filled == "فست فود تبریز"
    assert scraper.page.input.pressed == "Enter"
    assert scraper.state is ScraperState.LOADING
