import json

from app.composition import create_application
from core.models import Base
from scrapers.neshan import NeshanScraper


def create_test_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


def make_http_get(responses):
    calls = []

    def http_get(url):
        calls.append(url)
        response = responses[len(calls) - 1]
        return 200, json.dumps(response, ensure_ascii=False)

    http_get.calls = calls
    return http_get


def test_neshan_runs_through_full_application_pipeline():
    session_factory = create_test_session()

    http_get = make_http_get(
        [
            {
                "items": [
                    {
                        "location": {
                            "latitude": 35.7000,
                            "longitude": 51.4000,
                        }
                    }
                ]
            },
            {
                "count": 1,
                "items": [
                    {
                        "title": "کسب و کار نمونه",
                        "address": "تهران، خیابان نمونه",
                        "category": "business",
                        "location": {
                            "x": 51.4001,
                            "y": 35.7001,
                        },
                        "poiHash": "neshan-001",
                    }
                ],
            },
            {
                "name": "کسب و کار نمونه",
                "address": "تهران، خیابان نمونه",
                "phoneNumber": "02112345678",
                "website": "https://example.com",
                "location": {
                    "x": 51.4001,
                    "y": 35.7001,
                },
                "layer": {
                    "title": "کسب و کار",
                },
            },
        ]
    )

    application = create_application(
        session_factory=session_factory,
        browser_manager="fake-browser",
        source="neshan",
        scraper_kwargs={
            "api_key": "test-key",
            "http_get": http_get,
        },
    )

    assert isinstance(
        application.pipeline.scraper,
        NeshanScraper,
    )

    result = application.run(
        location="تهران",
        keywords=["کسب و کار"],
    )

    assert result.status == "COMPLETED"
    assert result.source == "neshan"
    assert result.total_found == 1
    assert result.total_new == 1
    assert result.total_errors == 0

    businesses = application.get_businesses()

    assert len(businesses) == 1
    assert businesses[0]["source"] == "neshan"
    assert businesses[0]["source_id"] == "neshan-001"
    assert businesses[0]["name"] == "کسب و کار نمونه"
    assert businesses[0]["phone"] == "02112345678"

    runs = application.list_runs()

    assert len(runs) == 1
    assert runs[0]["source"] == "neshan"
    assert runs[0]["status"] == "COMPLETED"


def test_neshan_pipeline_is_source_isolated_from_google_maps():
    session_factory = create_test_session()

    application = create_application(
        session_factory=session_factory,
        browser_manager="fake-browser",
        source="neshan",
        scraper_kwargs={
            "api_key": "test-key",
            "http_get": make_http_get(
                [
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
                                "title": "Neshan Business",
                                "address": "Tehran",
                                "location": {
                                    "x": 51.4,
                                    "y": 35.7,
                                },
                            }
                        ]
                    },
                ]
            ),
        },
    )

    assert application.pipeline.source == "neshan"
    assert application.registry.has("google_maps")
    assert application.registry.has("neshan")
    assert application.registry.get("neshan") is NeshanScraper
