from datetime import datetime, timezone

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.models import Base, ScrapeRun
from core.pipeline import ScrapePipeline
from core.request import ScrapeRequest


class FakeScraper:
    def __init__(self, businesses=None):
        self.businesses = businesses or []
        self.search_calls = []

    def search(self, query, location):
        self.search_calls.append((query, location))

    def scrape(self):
        return self.businesses


class FakeFactory:
    def __init__(self):
        self.calls = []
        self.scraper = FakeScraper([])

    def create(self, source, **kwargs):
        self.calls.append((source, kwargs))
        return self.scraper


def session_factory():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


def test_pipeline_creates_scraper_from_request_source_and_mode():
    factory = FakeFactory()
    pipeline = ScrapePipeline(
        factory=factory,
        session_factory=session_factory(),
        source="google_maps",
    )

    request = ScrapeRequest(
        location="مشهد",
        keywords=["پیتزا"],
        source="neshan",
        access_mode="api",
        api_key="secret",
    )

    result = pipeline.run(request=request)

    assert result.source == "neshan"
    assert result.access_mode == "api"
    assert factory.calls[-1] == (
        "neshan",
        {"access_mode": "api", "api_key": "secret"},
    )

    session = pipeline.session_factory()
    run = session.query(ScrapeRun).one()
    assert run.source == "neshan"
    assert run.access_mode == "api"
    session.close()