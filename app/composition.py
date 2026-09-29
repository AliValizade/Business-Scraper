from core.pipeline import ScrapePipeline
from scrapers.default_registry import create_default_registry
from scrapers.factory import ScraperFactory
from exporters.csv_exporter import CSVExporter
from exporters.excel_exporter import ExcelExporter
from exporters.json_exporter import JSONExporter
from exporters.service import ExportService
from app.application import Application
from services.business_service import BusinessService
from services.export_service import ExportService as ApplicationExportService
from services.run_service import RunService
from services.scrape_service import ScrapeService


def create_application(
    session_factory,
    browser_manager,
    source="google_maps",
    scraper_kwargs=None,
):
    """Create the fully composed application."""

    if session_factory is None:
        raise ValueError(
            "session_factory is required."
        )

    if browser_manager is None:
        raise ValueError(
            "browser_manager is required."
        )

    if not isinstance(source, str):
        raise TypeError(
            "source must be a string."
        )

    source = source.strip()

    if not source:
        raise ValueError(
            "source cannot be empty."
        )

    registry = create_default_registry()

    factory = ScraperFactory(
        registry=registry,
    )

    export_service = ExportService(
        exporters={
            "csv": CSVExporter(),
            "json": JSONExporter(),
            "excel": ExcelExporter(),
        }
    )

    final_scraper_kwargs = dict(
        scraper_kwargs or {}
    )

    final_scraper_kwargs.setdefault(
        "browser_manager",
        browser_manager,
    )

    pipeline = ScrapePipeline(
        factory=factory,
        source=source,
        session_factory=session_factory,
        scraper_kwargs=final_scraper_kwargs,
    )

    run_service = RunService(session_factory=session_factory)
    business_service = BusinessService(session_factory=session_factory)
    scrape_service = ScrapeService(pipeline=pipeline)
    application_export_service = ApplicationExportService(
        export_service=export_service,
        run_service=run_service,
    )

    return Application(
        pipeline=pipeline,
        registry=registry,
        factory=factory,
        export_service=export_service,
        session_factory=session_factory,
        scrape_service=scrape_service,
        run_service=run_service,
        business_service=business_service,
        application_export_service=application_export_service,
    )

