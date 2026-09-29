from app.composition import create_application
from services.business_service import BusinessService
from services.export_service import ExportService
from services.run_service import RunService
from services.scrape_service import ScrapeService


def create_test_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from core.models import Base

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
    )

    Base.metadata.create_all(engine)

    return sessionmaker(bind=engine)


def test_application_exposes_service_boundaries():
    application = create_application(
        session_factory=create_test_session(),
        browser_manager="fake-browser",
    )

    assert isinstance(application.scrape_service, ScrapeService)
    assert isinstance(application.run_service, RunService)
    assert isinstance(application.business_service, BusinessService)
    assert isinstance(
        application.application_export_service,
        ExportService,
    )


def test_scrape_service_uses_existing_pipeline():
    application = create_application(
        session_factory=create_test_session(),
        browser_manager="fake-browser",
    )

    assert application.scrape_service.pipeline is application.pipeline


def test_run_and_business_services_use_existing_session_factory():
    session_factory = create_test_session()

    application = create_application(
        session_factory=session_factory,
        browser_manager="fake-browser",
    )

    assert application.run_service.session_factory is session_factory
    assert application.business_service.session_factory is session_factory


def test_application_facade_delegates_run_operations():
    application = create_application(
        session_factory=create_test_session(),
        browser_manager="fake-browser",
    )

    class FakeResult:
        status = "COMPLETED"

    class FakeScrapeService:
        def start_scrape(self, location, keywords, max_results=None):
            return location, keywords, max_results

    application.scrape_service = FakeScrapeService()

    result = application.run(
        location="مشهد",
        keywords=["فست فود"],
        max_results=5,
    )

    assert result == (
        "مشهد",
        ["فست فود"],
        5,
    )


def test_application_facade_delegates_run_queries():
    application = create_application(
        session_factory=create_test_session(),
        browser_manager="fake-browser",
    )

    class FakeRunService:
        def list_runs(self, limit=20):
            return [limit]

        def get_run(self, run_id):
            return [run_id]

        def get_run_businesses(self, run_id):
            return [run_id]

    class FakeBusinessService:
        def list_businesses(self):
            return ["business"]

    application.run_service = FakeRunService()
    application.business_service = FakeBusinessService()

    assert application.list_runs(7) == [7]
    assert application.get_run(3) == [3]
    assert application.get_run_businesses(3) == [3]
    assert application.get_businesses() == ["business"]
