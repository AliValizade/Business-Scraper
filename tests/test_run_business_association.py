from datetime import datetime, timezone

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.application import Application
from core.errors import RunNotFoundError
from core.models import (
    Base,
    Business,
    ScrapeRunBusiness,
)
from core.pipeline import ScrapePipeline


def create_test_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(bind=engine)

    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )


def make_business(
    name="Pizza Sara",
    phone="+989123456789",
):
    return {
        "name": name,
        "category": "Restaurant",
        "address": "Mashhad",
        "city": "Mashhad",
        "phone": phone,
        "website": None,
        "instagram": None,
        "rating": 4.2,
        "reviews_count": 120,
        "latitude": 36.3,
        "longitude": 59.6,
        "google_maps_url": (
            "https://www.google.com/maps/place/test"
        ),
        "source": "google_maps",
        "source_id": None,
        "search_keyword": "فست فود",
        "source_url": (
            "https://www.google.com/maps/search/"
        ),
        "scraped_at": datetime.now(timezone.utc),
    }


class FakeScraper:
    def __init__(self, businesses):
        self.businesses = businesses

    def search(self, query, location):
        pass

    def scrape(self):
        return self.businesses


def test_pipeline_associates_each_business_with_run():
    session_factory = create_test_session()

    scraper = FakeScraper(
        [
            make_business(
                name="Pizza Sara",
                phone="+989123456789",
            ),
            make_business(
                name="Ace Burger",
                phone="+989111111111",
            ),
        ]
    )

    pipeline = ScrapePipeline(
        scraper=scraper,
        session_factory=session_factory,
    )

    result = pipeline.run(
        query="فست فود",
        location="مشهد",
    )

    assert result.status == "COMPLETED"

    session = session_factory()

    associations = (
        session.query(ScrapeRunBusiness)
        .filter(
            ScrapeRunBusiness.run_id == result.run_id
        )
        .all()
    )

    assert len(associations) == 2

    business_ids = {
        association.business_id
        for association in associations
    }

    assert business_ids == {
        business.id
        for business in session.query(Business).all()
    }

    session.close()


def test_pipeline_does_not_duplicate_association_within_run():
    session_factory = create_test_session()

    business = make_business()

    pipeline = ScrapePipeline(
        scraper=FakeScraper([business, business]),
        session_factory=session_factory,
    )

    result = pipeline.run(
        query="فست فود",
        location="مشهد",
    )

    assert result.status == "COMPLETED"
    assert result.total_new == 1
    assert result.total_duplicates == 1

    session = session_factory()

    associations = (
        session.query(ScrapeRunBusiness)
        .filter(
            ScrapeRunBusiness.run_id == result.run_id
        )
        .all()
    )

    assert len(associations) == 1

    session.close()


def test_business_can_be_associated_with_multiple_runs():
    session_factory = create_test_session()

    business = make_business()

    first_result = ScrapePipeline(
        scraper=FakeScraper([business]),
        session_factory=session_factory,
    ).run(
        query="فست فود",
        location="مشهد",
    )

    second_result = ScrapePipeline(
        scraper=FakeScraper([business]),
        session_factory=session_factory,
    ).run(
        query="فست فود",
        location="مشهد",
    )

    assert first_result.run_id != second_result.run_id

    session = session_factory()

    association_count = (
        session.query(ScrapeRunBusiness)
        .filter(
            ScrapeRunBusiness.business_id
            == session.query(Business.id).scalar()
        )
        .count()
    )

    assert association_count == 2

    session.close()


def test_application_get_run_businesses():
    session_factory = create_test_session()

    result = ScrapePipeline(
        scraper=FakeScraper(
            [
                make_business(
                    name="Pizza Sara",
                    phone="+989123456789",
                ),
                make_business(
                    name="Ace Burger",
                    phone="+989111111111",
                ),
            ]
        ),
        session_factory=session_factory,
    ).run(
        query="فست فود",
        location="مشهد",
    )

    application = Application(
        pipeline=FakeScraper([]),
        session_factory=session_factory,
    )

    businesses = application.get_run_businesses(
        result.run_id
    )

    assert [business["name"] for business in businesses] == [
        "Pizza Sara",
        "Ace Burger",
    ]

    assert all(
        "id" in business
        and "name" in business
        and "source" in business
        for business in businesses
    )


def test_application_get_run_businesses_missing_run():
    session_factory = create_test_session()

    application = Application(
        pipeline=FakeScraper([]),
        session_factory=session_factory,
    )

    with pytest.raises(RunNotFoundError):
        application.get_run_businesses(999)


def test_application_get_run_businesses_validates_run_id():
    session_factory = create_test_session()

    application = Application(
        pipeline=FakeScraper([]),
        session_factory=session_factory,
    )

    with pytest.raises(TypeError):
        application.get_run_businesses("1")

    with pytest.raises(ValueError):
        application.get_run_businesses(0)
