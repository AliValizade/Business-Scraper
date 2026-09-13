from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.models import Base
from core.pipeline import ScrapePipeline


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

    assert result["status"] == "COMPLETED"
    assert result["total_found"] == 2
    assert result["total_new"] == 2
    assert result["total_updated"] == 0
    assert result["total_duplicates"] == 0
    assert result["total_errors"] == 0

    session = session_factory()

    from core.models import Business, ScrapeRun

    assert session.query(Business).count() == 2
    assert session.query(ScrapeRun).count() == 1

    session.close()


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

    assert first_result["total_new"] == 1

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

    assert second_result["total_found"] == 1
    assert second_result["total_new"] == 0
    assert second_result["total_updated"] == 0
    assert second_result["total_duplicates"] == 1
    assert second_result["total_errors"] == 0

    session = session_factory()

    from core.models import Business

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

    assert result["total_found"] == 1
    assert result["total_new"] == 0
    assert result["total_updated"] == 1
    assert result["total_duplicates"] == 0
    assert result["total_errors"] == 0

    session = session_factory()

    from core.models import Business

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