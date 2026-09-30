from app.composition import create_application
from core.result import ScrapeResult
from services.business_service import BusinessService
from services.dto import BusinessDTO, RunDTO, ScrapeResultDTO
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
    assert isinstance(application.application_export_service, ExportService)


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


def test_application_adapts_scrape_result_dto_to_legacy_result():
    application = create_application(
        session_factory=create_test_session(),
        browser_manager="fake-browser",
    )

    class FakeScrapeService:
        def start_scrape(self, location, keywords, max_results=None):
            return ScrapeResultDTO(
                status="COMPLETED",
                source="google_maps",
                location=location,
                keywords=tuple(keywords),
                run_id=5,
            )

    application.scrape_service = FakeScrapeService()

    result = application.run(
        location="مشهد",
        keywords=["فست فود"],
        max_results=5,
    )

    assert isinstance(result, ScrapeResult)
    assert result.run_id == 5
    assert result.keywords == ("فست فود",)


def test_application_adapts_query_dtos_to_legacy_dicts():
    application = create_application(
        session_factory=create_test_session(),
        browser_manager="fake-browser",
    )

    class FakeRunService:
        def list_runs(self, limit=20):
            return [
                RunDTO(
                    id=3,
                    source="google_maps",
                    city="Mashhad",
                    keyword="Fast Food",
                    started_at=None,
                    finished_at=None,
                    status="COMPLETED",
                    total_found=1,
                    total_new=1,
                    total_updated=0,
                    total_duplicates=0,
                    total_errors=0,
                )
            ]

        def get_run(self, run_id):
            return self.list_runs()[0]

        def get_run_businesses(self, run_id):
            return [
                BusinessDTO(
                    id=1,
                    name="Pizza Sara",
                    source="google_maps",
                )
            ]

    class FakeBusinessService:
        def list_businesses(self):
            return self.get_businesses()

        def get_businesses(self):
            return [
                BusinessDTO(
                    id=1,
                    name="Pizza Sara",
                    source="google_maps",
                )
            ]

    application.run_service = FakeRunService()
    application.business_service = FakeBusinessService()

    assert application.list_runs(7)[0]["id"] == 3
    assert application.get_run(3)["id"] == 3
    assert application.get_run_businesses(3)[0]["name"] == "Pizza Sara"
    assert application.get_businesses()[0]["name"] == "Pizza Sara"


def test_service_dtos_are_frozen_boundary_objects():
    dto = ScrapeResultDTO(
        status="COMPLETED",
        source="google_maps",
        location="Mashhad",
        keywords=("pizza",),
        run_id=1,
    )

    try:
        dto.status = "FAILED"
    except Exception as exc:
        assert isinstance(exc, (AttributeError, TypeError))
    else:
        raise AssertionError("Service DTOs must be immutable.")


def test_service_modules_do_not_expose_core_models():
    import inspect

    for service_class in (
        ScrapeService,
        RunService,
        BusinessService,
        ExportService,
    ):
        source = inspect.getsource(service_class)
        assert "return Business(" not in source
        assert "return ScrapeRun(" not in source
