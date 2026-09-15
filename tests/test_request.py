import pytest

from core.request import ScrapeRequest


def test_scrape_request_accepts_multiple_keywords():
    request = ScrapeRequest(
        location="مشهد",
        keywords=[
            "فست فود",
            "پیتزا",
            "پروتئینی",
        ],
    )

    assert request.location == "مشهد"

    assert request.keywords == (
        "فست فود",
        "پیتزا",
        "پروتئینی",
    )


def test_scrape_request_accepts_single_keyword():
    request = ScrapeRequest(
        location="مشهد",
        keywords=["پیتزا"],
    )

    assert request.keywords == ("پیتزا",)


def test_scrape_request_strips_location_and_keywords():
    request = ScrapeRequest(
        location="  مشهد  ",
        keywords=[
            "  پیتزا ",
            " فست فود  ",
        ],
    )

    assert request.location == "مشهد"

    assert request.keywords == (
        "پیتزا",
        "فست فود",
    )


def test_scrape_request_rejects_empty_location():
    with pytest.raises(ValueError):
        ScrapeRequest(
            location="   ",
            keywords=["پیتزا"],
        )


def test_scrape_request_rejects_empty_keywords():
    with pytest.raises(ValueError):
        ScrapeRequest(
            location="مشهد",
            keywords=[],
        )


def test_scrape_request_rejects_string_as_keywords():
    with pytest.raises(TypeError):
        ScrapeRequest(
            location="مشهد",
            keywords="پیتزا",
        )


def test_scrape_request_rejects_empty_keyword():
    with pytest.raises(ValueError):
        ScrapeRequest(
            location="مشهد",
            keywords=[
                "پیتزا",
                "   ",
            ],
        )


def test_scrape_request_is_immutable():
    request = ScrapeRequest(
        location="مشهد",
        keywords=["پیتزا"],
    )

    with pytest.raises(AttributeError):
        request.location = "تهران"


def test_scrape_request_accepts_max_results():
    request = ScrapeRequest(
        location="Mashhad",
        keywords=["pizza"],
        max_results=50,
    )

    assert request.max_results == 50


def test_scrape_request_allows_none_max_results():
    request = ScrapeRequest(
        location="Mashhad",
        keywords=["pizza"],
    )

    assert request.max_results is None


@pytest.mark.parametrize(
    "value",
    [
        0,
        -1,
    ],
)
def test_scrape_request_rejects_non_positive_max_results(value):
    with pytest.raises(ValueError, match="greater than zero"):
        ScrapeRequest(
            location="Mashhad",
            keywords=["pizza"],
            max_results=value,
        )


@pytest.mark.parametrize(
    "value",
    [
        "50",
        5.5,
    ],
)
def test_scrape_request_rejects_invalid_max_results_type(value):
    with pytest.raises(TypeError, match="integer or None"):
        ScrapeRequest(
            location="Mashhad",
            keywords=["pizza"],
            max_results=value,
        )




