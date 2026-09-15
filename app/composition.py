from dataclasses import dataclass

from core.pipeline import ScrapePipeline
from scrapers.default_registry import create_default_registry
from scrapers.factory import ScraperFactory


@dataclass
class Application:
    """Application dependencies composed at the application boundary."""

    registry: object
    factory: ScraperFactory
    pipeline: ScrapePipeline


def create_application(
    session_factory,
    browser_manager,
    source="google_maps",
    scraper_kwargs=None,
):
    """
    Create the application composition root.

    The composition root is responsible for wiring:
        Registry -> Factory -> Pipeline

    External infrastructure dependencies such as the database
    session factory and browser manager are supplied to this function.
    """

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
        registry=registry,
        factory=factory,
        pipeline=pipeline,
    )