from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.models import Base, ScrapeRun
from core.pipeline import ScrapePipeline


class LifecycleBrowser:
    def __init__(self, fail_on_start=False):
        self.fail_on_start = fail_on_start
        self.events = []

    def start(self):
        self.events.append("start")
        if self.fail_on_start:
            raise RuntimeError("browser start failure")

    def close(self):
        self.events.append("close")


class FakeScraper:
    def __init__(self, browser_manager):
        self.browser_manager = browser_manager

    def search(self, query, location):
        pass

    def scrape(self):
        return []


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


def test_pipeline_starts_and_closes_browser_manager():
    session_factory = create_test_session()
    browser = LifecycleBrowser()
    scraper = FakeScraper(browser)

    pipeline = ScrapePipeline(
        scraper=scraper,
        session_factory=session_factory,
    )

    result = pipeline.run(
        query="فست فود",
        location="مشهد",
    )

    assert result.status == "COMPLETED"
    assert browser.events == ["start", "close"]


def test_pipeline_closes_browser_after_keyword_error():
    session_factory = create_test_session()
    browser = LifecycleBrowser()

    class FailingScraper(FakeScraper):
        def search(self, query, location):
            raise RuntimeError("keyword failure")

    pipeline = ScrapePipeline(
        scraper=FailingScraper(browser),
        session_factory=session_factory,
    )

    result = pipeline.run(
        query="فست فود",
        location="مشهد",
    )

    assert result.status == "COMPLETED"
    assert result.total_errors == 1
    assert browser.events == ["start", "close"]


def test_pipeline_returns_failed_result_when_browser_start_fails():
    session_factory = create_test_session()
    browser = LifecycleBrowser(fail_on_start=True)
    scraper = FakeScraper(browser)

    pipeline = ScrapePipeline(
        scraper=scraper,
        session_factory=session_factory,
    )

    result = pipeline.run(
        query="فست فود",
        location="مشهد",
    )

    assert result.status == "FAILED"
    assert result.error_message == "browser start failure"
    assert result.total_errors == 1
    assert browser.events == ["start"]

    session = session_factory()
    scrape_run = session.query(ScrapeRun).one()

    assert scrape_run.status == "FAILED"
    assert scrape_run.error_message == "browser start failure"
    assert scrape_run.finished_at is not None

    session.close()


def test_pipeline_does_not_require_browser_lifecycle_for_plain_scraper():
    session_factory = create_test_session()

    class PlainScraper:
        def search(self, query, location):
            pass

        def scrape(self):
            return []

    pipeline = ScrapePipeline(
        scraper=PlainScraper(),
        session_factory=session_factory,
    )

    result = pipeline.run(
        query="فست فود",
        location="مشهد",
    )

    assert result.status == "COMPLETED"
