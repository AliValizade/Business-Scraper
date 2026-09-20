from datetime import datetime, timezone

import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.models import Base, Business, ScrapeRun
from core.pipeline import ScrapePipeline
from core.request import ScrapeRequest
from core.result import ScrapeResult

from utils.progress import ProgressReporter

from scrapers.registry import ScraperRegistry
from scrapers.base import BaseScraper


class FakeFactory:
    def __init__(self, scraper):
        self.scraper = scraper
        self.created_source = None
        self.created_kwargs = None

    def create(self, source, **kwargs):
        self.created_source = source
        self.created_kwargs = kwargs
        return self.scraper


class FakeScraper:
    def __init__(self, businesses):
        self.businesses = businesses
        self.search_calls = []

    def search(self, query, location):
        self.search_calls.append(
            {
                "query": query,
                "location": location,
            }
        )

    def scrape(self):
        return self.businesses


def create_test_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={
            "check_same_thread": False,
        },
    )

    Base.metadata.create_all(
        bind=engine
    )

    return sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
    )


def make_business(
    name="Pizza Sara",
    address="Mashhad",
    phone="+989123456789",
):
    return {
        "name": name,
        "category": "Restaurant",
        "address": address,
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


def test_pipeline_inserts_new_businesses():
    session_factory = create_test_session()

    businesses = [
        make_business(
            name="Pizza Sara",
            phone="+989123456789",
        ),
        make_business(
            name="Ace Burger",
            phone="+989111111111",
        ),
    ]

    scraper = FakeScraper(businesses)

    pipeline = ScrapePipeline(
        scraper=scraper,
        session_factory=session_factory,
    )

    result = pipeline.run(
        query="فست فود",
        location="مشهد",
    )
    
    assert result.status == "COMPLETED"
    assert result.total_found == 2
    assert result.total_new == 2
    assert result.total_updated == 0
    assert result.total_duplicates == 0
    assert result.total_errors == 0

    session = session_factory()

    assert session.query(Business).count() == 2
    assert session.query(ScrapeRun).count() == 1

    session.close()


def test_pipeline_returns_scrape_result():
    session_factory = create_test_session()

    scraper = FakeScraper(
        [
            make_business(
                name="Pizza Sara",
                phone="+989123456789",
            )
        ]
    )

    pipeline = ScrapePipeline(
        scraper=scraper,
        session_factory=session_factory,
        source="google_maps",
    )

    result = pipeline.run(
        query="فست فود",
        location="مشهد",
    )

    assert isinstance(result, ScrapeResult)

    assert result.status == "COMPLETED"
    assert result.source == "google_maps"
    assert result.location == "مشهد"
    assert result.keywords == ("فست فود",)

    assert result.total_found == 1
    assert result.total_new == 1
    assert result.total_updated == 0
    assert result.total_duplicates == 0
    assert result.total_errors == 0

    assert result.error_message is None


def test_pipeline_detects_duplicate_business():
    session_factory = create_test_session()

    first_business = make_business()

    first_scraper = FakeScraper(
        [first_business]
    )

    first_pipeline = ScrapePipeline(
        scraper=first_scraper,
        session_factory=session_factory,
    )

    first_result = first_pipeline.run(
        query="فست فود",
        location="مشهد",
    )

    assert first_result.total_new == 1

    second_business = make_business()

    second_scraper = FakeScraper(
        [second_business]
    )

    second_pipeline = ScrapePipeline(
        scraper=second_scraper,
        session_factory=session_factory,
    )

    second_result = second_pipeline.run(
        query="فست فود",
        location="مشهد",
    )

    assert second_result.total_found == 1
    assert second_result.total_new == 0
    assert second_result.total_updated == 0
    assert second_result.total_duplicates == 1
    assert second_result.total_errors == 0

    session = session_factory()

    assert session.query(Business).count() == 1

    session.close()


def test_pipeline_updates_existing_business():
    session_factory = create_test_session()

    first_business = make_business(
        name="Pizza Sara",
        phone="+989123456789",
    )

    first_pipeline = ScrapePipeline(
        scraper=FakeScraper([first_business]),
        session_factory=session_factory,
    )

    first_pipeline.run(
        query="فست فود",
        location="مشهد",
    )

    updated_business = make_business(
        name="Pizza Sara",
        phone="+989123456789",
    )

    updated_business["rating"] = 4.5
    updated_business["reviews_count"] = 250

    second_pipeline = ScrapePipeline(
        scraper=FakeScraper([updated_business]),
        session_factory=session_factory,
    )

    result = second_pipeline.run(
        query="فست فود",
        location="مشهد",
    )

    assert result.total_found == 1
    assert result.total_new == 0
    assert result.total_updated == 1
    assert result.total_duplicates == 0
    assert result.total_errors == 0

    session = session_factory()

    business = session.query(Business).one()

    assert business.rating == 4.5
    assert business.reviews_count == 250

    session.close()


def test_pipeline_searches_with_correct_query_and_location():
    session_factory = create_test_session()

    scraper = FakeScraper(
        [make_business()]
    )

    pipeline = ScrapePipeline(
        scraper=scraper,
        session_factory=session_factory,
    )

    pipeline.run(
        query="پیتزا",
        location="مشهد",
    )

    assert scraper.search_calls == [
        {
            "query": "پیتزا",
            "location": "مشهد",
        }
    ]


def test_pipeline_isolates_business_processing_errors():
    session_factory = create_test_session()

    valid_business_1 = make_business(
        name="Pizza Sara",
        phone="+989123456789",
    )

    invalid_business = None

    valid_business_2 = make_business(
        name="Ace Burger",
        phone="+989111111111",
    )

    scraper = FakeScraper(
        [
            valid_business_1,
            invalid_business,
            valid_business_2,
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
    assert result.total_found == 3
    assert result.total_new == 2
    assert result.total_updated == 0
    assert result.total_duplicates == 0
    assert result.total_errors == 1

    session = session_factory()

    businesses = session.query(Business).all()

    assert len(businesses) == 2

    names = {business.name for business in businesses}

    assert names == {
        "Pizza Sara",
        "Ace Burger",
    }

    session.close()


def test_pipeline_reports_progress():
    session_factory = create_test_session()

    businesses = [
        make_business(
            name="Pizza Sara",
            phone="+989123456789",
        ),
        make_business(
            name="Ace Burger",
            phone="+989111111111",
        ),
    ]

    scraper = FakeScraper(businesses)

    progress_reporter = ProgressReporter()

    pipeline = ScrapePipeline(
        scraper=scraper,
        session_factory=session_factory,
        progress_reporter=progress_reporter,
    )

    result = pipeline.run(
        query="فست فود",
        location="مشهد",
    )

    snapshot = progress_reporter.get_snapshot()

    assert result.total_found == 2

    assert snapshot.total == 2
    assert snapshot.processed == 2
    assert snapshot.new == 2
    assert snapshot.updated == 0
    assert snapshot.duplicates == 0
    assert snapshot.errors == 0

    assert progress_reporter.get_percentage() == 100.0


def test_pipeline_supports_multiple_keywords():
    session_factory = create_test_session()

    first_business = make_business(
        name="Pizza Sara",
        phone="+989123456789",
    )

    second_business = make_business(
        name="Ace Burger",
        phone="+989111111111",
    )

    scraper = FakeScraper(
        [
            first_business,
            second_business,
        ]
    )

    request = ScrapeRequest(
        location="مشهد",
        keywords=[
            "فست فود",
            "پیتزا",
        ],
    )

    pipeline = ScrapePipeline(
        scraper=scraper,
        session_factory=session_factory,
    )

    result = pipeline.run(request=request)

    assert result.status == "COMPLETED"
    assert result.total_found == 4
    assert result.total_new == 2
    assert result.total_duplicates == 2
    assert result.total_errors == 0

    assert scraper.search_calls == [
        {
            "query": "فست فود",
            "location": "مشهد",
        },
        {
            "query": "پیتزا",
            "location": "مشهد",
        },
    ]

    session = session_factory()

    assert session.query(Business).count() == 2

    session.close()


def test_pipeline_isolates_keyword_errors():
    session_factory = create_test_session()

    class KeywordFailingScraper(FakeScraper):
        def search(self, query, location):
            self.search_calls.append(
                {
                    "query": query,
                    "location": location,
                }
            )

            if query == "پیتزا":
                raise TimeoutError(
                    "temporary keyword failure"
                )

            self.current_query = query

        def scrape(self):
            if self.current_query == "فست فود":
                return [
                    make_business(
                        name="Fast Food Sara",
                        phone="+989123456789",
                    )
                ]

            if self.current_query == "پروتئینی":
                return [
                    make_business(
                        name="Protein Center",
                        phone="+989111111111",
                    )
                ]

            return []

    scraper = KeywordFailingScraper([])
    scraper.current_query = None

    request = ScrapeRequest(
        location="مشهد",
        keywords=[
            "فست فود",
            "پیتزا",
            "پروتئینی",
        ],
    )

    pipeline = ScrapePipeline(
        scraper=scraper,
        session_factory=session_factory,
    )

    result = pipeline.run(request=request)

    assert result.status == "COMPLETED"
    assert result.total_found == 2
    assert result.total_new == 2
    assert result.total_errors == 1
    assert result.total_duplicates == 0
    assert scraper.search_calls == [
        {
            "query": "فست فود",
            "location": "مشهد",
        },
        {
            "query": "پیتزا",
            "location": "مشهد",
        },
        {
            "query": "پروتئینی",
            "location": "مشهد",
        },
    ]
    assert result.error_message is None


def test_pipeline_reports_keyword_progress():
    session_factory = create_test_session()

    first_business = make_business(
        name="Fast Food Sara",
        phone="+989123456789",
    )

    second_business = make_business(
        name="Pizza Center",
        phone="+989111111111",
    )

    scraper = FakeScraper(
        [
            first_business,
            second_business,
        ]
    )

    reporter = ProgressReporter()

    request = ScrapeRequest(
        location="مشهد",
        keywords=[
            "فست فود",
            "پیتزا",
        ],
    )

    pipeline = ScrapePipeline(
        scraper=scraper,
        session_factory=session_factory,
        progress_reporter=reporter,
    )

    result = pipeline.run(request=request)

    assert result.status == "COMPLETED"

    snapshot = reporter.get_snapshot()

    assert snapshot.current_keyword == "پیتزا"
    assert snapshot.keyword_index == 2
    assert snapshot.total_keywords == 2


def test_pipeline_can_create_scraper_from_registry():
    session_factory = create_test_session()

    scraper = FakeScraper(
        [
            make_business(
                name="Pizza Sara",
                phone="+989123456789",
            )
        ]
    )

    class FakeRegistryScraper(BaseScraper):
        def __init__(self, **kwargs):
            super().__init__(
                browser_manager=kwargs["browser_manager"]
            )

        def search(self, query, location):
            scraper.search(query, location)

        def scrape(self):
            return scraper.scrape()

    registry = ScraperRegistry()

    registry.register(
        "fake",
        FakeRegistryScraper,
    )

    pipeline = ScrapePipeline(
        registry=registry,
        source="fake",
        session_factory=session_factory,
        scraper_kwargs={
            "browser_manager": "fake-browser",
        },
    )

    request = ScrapeRequest(
        location="مشهد",
        keywords=["پیتزا"],
    )

    result = pipeline.run(
        request=request,
    )

    assert result.status == "COMPLETED"
    assert result.total_found == 1
    assert result.total_new == 1


def test_pipeline_uses_registry_source():
    session_factory = create_test_session()

    scraper = FakeScraper(
        [
            make_business(
                name="Pizza Sara",
                phone="+989123456789",
            )
        ]
    )

    class FakeRegistryScraper(BaseScraper):
        def __init__(self, **kwargs):
            super().__init__(
                browser_manager=kwargs.get(
                    "browser_manager"
                )
            )

        def search(self, query, location):
            scraper.search(query, location)

        def scrape(self):
            return scraper.scrape()

    registry = ScraperRegistry()

    registry.register(
        "fake",
        FakeRegistryScraper,
    )

    pipeline = ScrapePipeline(
        registry=registry,
        source="fake",
        session_factory=session_factory,
    )

    request = ScrapeRequest(
        location="مشهد",
        keywords=["پیتزا"],
    )

    result = pipeline.run(
        request=request,
    )

    assert result.status == "COMPLETED"

    session = session_factory()

    scrape_run = (
        session.query(ScrapeRun)
        .first()
    )

    assert scrape_run.source == "fake"

    session.close()


def test_pipeline_rejects_unknown_registry_source():
    session_factory = create_test_session()

    registry = ScraperRegistry()

    with pytest.raises(
        KeyError,
        match="No scraper registered",
    ):
        ScrapePipeline(
            registry=registry,
            source="unknown",
            session_factory=session_factory,
        )


def test_pipeline_can_create_scraper_from_factory():
    session_factory = create_test_session()

    scraper = FakeScraper(
        [
            make_business(
                name="Pizza Sara",
                phone="+989123456789",
            )
        ]
    )

    factory = FakeFactory(scraper)

    pipeline = ScrapePipeline(
        factory=factory,
        source="fake",
        session_factory=session_factory,
        scraper_kwargs={
            "browser_manager": "fake-browser",
        },
    )

    assert pipeline.scraper is scraper

    assert factory.created_source == "fake"

    assert factory.created_kwargs == {
        "browser_manager": "fake-browser",
    }


def test_pipeline_uses_factory_source():
    session_factory = create_test_session()

    scraper = FakeScraper([])

    factory = FakeFactory(scraper)

    pipeline = ScrapePipeline(
        factory=factory,
        source="fake",
        session_factory=session_factory,
    )

    assert factory.created_source == "fake"

    assert pipeline.scraper is scraper


def test_pipeline_passes_scraper_kwargs_to_factory():
    session_factory = create_test_session()

    scraper = FakeScraper([])

    factory = FakeFactory(scraper)

    pipeline = ScrapePipeline(
        factory=factory,
        source="fake",
        session_factory=session_factory,
        scraper_kwargs={
            "browser_manager": "browser",
        },
    )

    assert pipeline.scraper is scraper

    assert factory.created_kwargs == {
        "browser_manager": "browser",
    }


def test_pipeline_prefers_explicit_scraper_over_factory():
    session_factory = create_test_session()

    explicit_scraper = FakeScraper([])

    factory_scraper = FakeScraper([])

    factory = FakeFactory(factory_scraper)

    pipeline = ScrapePipeline(
        scraper=explicit_scraper,
        factory=factory,
        source="fake",
        session_factory=session_factory,
    )

    assert pipeline.scraper is explicit_scraper
    assert factory.created_source is None


def test_pipeline_requires_scraper_factory_or_registry():
    session_factory = create_test_session()

    with pytest.raises(
        ValueError,
        match=(
            "Either scraper, factory, or registry "
            "must be provided."
        ),
    ):
        ScrapePipeline(
            session_factory=session_factory,
        )


def test_pipeline_respects_max_results_across_keywords():
    session_factory = create_test_session()

    first_businesses = [
        make_business(
            name="Pizza Sara",
            phone="+989123456789",
        ),
        make_business(
            name="Pizza Center",
            phone="+989111111111",
        ),
        make_business(
            name="Pizza House",
            phone="+989122222222",
        ),
    ]

    second_businesses = [
        make_business(
            name="Fast Food Sara",
            phone="+989133333333",
        ),
        make_business(
            name="Fast Food Center",
            phone="+989144444444",
        ),
    ]

    third_businesses = [
        make_business(
            name="Burger House",
            phone="+989155555555",
        ),
    ]

    class LimitedFakeScraper(FakeScraper):
        def search(self, query, location):
            self.current_query = query
            super().search(query, location)
            
        def scrape(self):
            if self.current_query == "پیتزا":
                return first_businesses

            if self.current_query == "فست فود":
                return second_businesses

            if self.current_query == "برگر":
                return third_businesses

            return []

    scraper = LimitedFakeScraper([])

    request = ScrapeRequest(
        location="مشهد",
        keywords=[
            "پیتزا",
            "فست فود",
            "برگر",
        ],
        max_results=5,
    )

    pipeline = ScrapePipeline(
        scraper=scraper,
        session_factory=session_factory,
    )

    result = pipeline.run(request=request)

    assert result.status == "COMPLETED"
    assert result.total_found == 5

    assert scraper.search_calls == [
        {
            "query": "پیتزا",
            "location": "مشهد",
        },
        {
            "query": "فست فود",
            "location": "مشهد",
        },
    ]

    session = session_factory()

    assert session.query(Business).count() == 5

    session.close()


def test_pipeline_returns_failed_result_on_run_level_error():
    session_factory = create_test_session()

    scraper = FakeScraper(
        [
            make_business(
                name="Pizza Sara",
                phone="+989123456789",
            )
        ]
    )

    class FailingProgressReporter:
        def start(self, total, total_keywords):
            raise RuntimeError("progress reporter failure")

    pipeline = ScrapePipeline(
        scraper=scraper,
        session_factory=session_factory,
        progress_reporter=FailingProgressReporter(),
    )

    result = pipeline.run(
        query="فست فود",
        location="مشهد",
    )

    assert isinstance(result, ScrapeResult)

    assert result.status == "FAILED"
    assert result.source == "google_maps"
    assert result.location == "مشهد"
    assert result.keywords == ("فست فود",)

    assert result.error_message == "progress reporter failure"
    assert result.total_errors == 1

    session = session_factory()

    scrape_run = session.query(ScrapeRun).one()

    assert scrape_run.status == "FAILED"
    assert scrape_run.error_message == "progress reporter failure"
    assert scrape_run.finished_at is not None
    assert scrape_run.total_errors == 1

    session.close()


def test_pipeline_returns_failed_result_when_progress_update_fails():
    session_factory = create_test_session()

    scraper = FakeScraper(
        [
            make_business(
                name="Pizza Sara",
                phone="+989123456789",
            )
        ]
    )

    class FailingProgressReporter:
        def start(self, total, total_keywords):
            pass

        def set_keyword(
            self,
            keyword,
            keyword_index,
            total_keywords,
        ):
            pass

        def update(self, total):
            raise RuntimeError("progress update failure")

    pipeline = ScrapePipeline(
        scraper=scraper,
        session_factory=session_factory,
        progress_reporter=FailingProgressReporter(),
    )

    result = pipeline.run(
        query="فست فود",
        location="مشهد",
    )

    assert result.status == "FAILED"
    assert result.error_message == "progress update failure"

    session = session_factory()

    scrape_run = session.query(ScrapeRun).one()

    assert scrape_run.status == "FAILED"
    assert scrape_run.error_message == "progress update failure"

    session.close()




