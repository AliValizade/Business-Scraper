import json

import pytest

from scrapers.google_maps import GoogleMapsAPIError, GoogleMapsScraper


def make_http_post(responses):
    calls = []

    def http_post(url, headers, body):
        calls.append((url, headers, body))
        response = responses.pop(0)
        return 200, json.dumps(response)

    http_post.calls = calls
    return http_post


def test_google_maps_api_requires_key():
    scraper = GoogleMapsScraper(access_mode="api")

    with pytest.raises(ValueError, match="API key"):
        scraper.search("رستوران", "مشهد")


def test_google_maps_api_rejects_key_in_web_mode():
    with pytest.raises(ValueError, match="only accepted in API mode"):
        GoogleMapsScraper(access_mode="web", api_key="secret")


def test_google_maps_api_search_maps_places():
    http_post = make_http_post(
        [
            {
                "places": [
                    {
                        "id": "ChIJtest123",
                        "displayName": {"text": "Restaurant Test"},
                        "formattedAddress": "Mashhad, Example St",
                        "location": {
                            "latitude": 36.297,
                            "longitude": 59.606,
                        },
                        "nationalPhoneNumber": "05112345678",
                        "websiteUri": "https://example.com",
                        "rating": 4.6,
                        "userRatingCount": 120,
                        "primaryType": "restaurant",
                        "googleMapsUri": "https://maps.google.com/?cid=123",
                    }
                ]
            }
        ]
    )

    scraper = GoogleMapsScraper(
        access_mode="api",
        api_key="test-key",
        http_post=http_post,
    )

    result = scraper.search("رستوران", "مشهد")

    assert result[0]["name"] == "Restaurant Test"
    assert result[0]["source"] == "google_maps"
    assert result[0]["source_id"] == "ChIJtest123"
    assert result[0]["phone"] == "05112345678"
    assert result[0]["rating"] == 4.6
    assert result[0]["reviews_count"] == 120

    url, headers, body = http_post.calls[0]
    assert url == GoogleMapsScraper.PLACES_API_URL
    assert headers["X-Goog-Api-Key"] == "test-key"
    assert "places.id" in headers["X-Goog-FieldMask"]
    assert body["textQuery"] == "رستوران مشهد"
    assert body["pageSize"] == 20


def test_google_maps_api_paginates_up_to_thirty_results():
    first_page = {
        "places": [
            {
                "id": f"id-{index}",
                "displayName": {"text": f"Business {index}"},
            }
            for index in range(20)
        ],
        "nextPageToken": "next-token",
    }
    second_page = {
        "places": [
            {
                "id": f"id-{index}",
                "displayName": {"text": f"Business {index}"},
            }
            for index in range(20, 40)
        ]
    }

    http_post = make_http_post([first_page, second_page])

    scraper = GoogleMapsScraper(
        access_mode="api",
        api_key="test-key",
        http_post=http_post,
    )

    result = scraper.search("رستوران", "مشهد")

    assert len(result) == 30
    assert http_post.calls[1][2]["pageToken"] == "next-token"


def test_google_maps_api_invalid_status_raises():
    def http_post(_url, _headers, _body):
        return 403, "{}"

    scraper = GoogleMapsScraper(
        access_mode="api",
        api_key="test-key",
        http_post=http_post,
    )

    with pytest.raises(GoogleMapsAPIError) as exc_info:
        scraper.search("رستوران", "مشهد")

    assert exc_info.value.status_code == 403
    assert scraper.state.value == "FAILED"
