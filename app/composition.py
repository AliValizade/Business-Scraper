from core.pipeline import ScrapePipeline
from scrapers.default_registry import create_default_registry
from scrapers.factory import ScraperFactory
from exporters.csv_exporter import CSVExporter
from exporters.excel_exporter import ExcelExporter
from exporters.json_exporter import JSONExporter
from exporters.service import ExportService
from app.application import Application


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

    return Application(
        pipeline=pipeline,
        registry=registry,
        factory=factory,
        export_service=export_service,
        session_factory=session_factory,
    )

