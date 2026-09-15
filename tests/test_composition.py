from core.pipeline import ScrapePipeline
from scrapers.factory import ScraperFactory
from scrapers.registry import ScraperRegistry
from app.application import Application
from app.composition import (
    Application,
    create_application,
)


def create_test_session():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from core.models import Base

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={
            "check_same_thread": False,
        },
    )

    Base.metadata.create_all(
        engine
    )

    return sessionmaker(
        bind=engine
    )


def test_create_application_returns_application():
    session_factory = create_test_session()

    application = create_application(
        session_factory=session_factory,
        browser_manager="fake-browser",
    )

    assert isinstance(
        application,
        Application,
    )


def test_application_creates_default_registry():
    session_factory = create_test_session()

    application = create_application(
        session_factory=session_factory,
        browser_manager="fake-browser",
    )

    assert isinstance(
        application.registry,
        ScraperRegistry,
    )

    assert application.registry.has(
        "google_maps"
    )


def test_application_creates_factory_from_registry():
    session_factory = create_test_session()

    application = create_application(
        session_factory=session_factory,
        browser_manager="fake-browser",
    )

    assert isinstance(
        application.factory,
        ScraperFactory,
    )

    assert (
        application.factory.registry
        is application.registry
    )


def test_application_creates_pipeline_from_factory():
    session_factory = create_test_session()

    application = create_application(
        session_factory=session_factory,
        browser_manager="fake-browser",
    )

    assert isinstance(
        application.pipeline,
        ScrapePipeline,
    )

    assert (
        application.pipeline.factory
        is application.factory
    )


def test_application_uses_google_maps_by_default():
    session_factory = create_test_session()

    application = create_application(
        session_factory=session_factory,
        browser_manager="fake-browser",
    )

    assert (
        application.pipeline.source
        == "google_maps"
    )


def test_application_passes_browser_manager_to_scraper():
    session_factory = create_test_session()

    application = create_application(
        session_factory=session_factory,
        browser_manager="fake-browser",
    )

    assert (
        application.pipeline.scraper.browser_manager
        == "fake-browser"
    )


def test_application_custom_scraper_kwargs_can_override_browser_manager():
    session_factory = create_test_session()

    application = create_application(
        session_factory=session_factory,
        browser_manager="default-browser",
        scraper_kwargs={
            "browser_manager": "custom-browser",
        },
    )

    assert (
        application.pipeline.scraper.browser_manager
        == "custom-browser"
    )


def test_application_requires_session_factory():
    try:
        create_application(
            session_factory=None,
            browser_manager="fake-browser",
        )
    except ValueError as exc:
        assert str(exc) == (
            "session_factory is required."
        )
    else:
        raise AssertionError(
            "ValueError was not raised."
        )


def test_application_requires_browser_manager():
    session_factory = create_test_session()

    try:
        create_application(
            session_factory=session_factory,
            browser_manager=None,
        )
    except ValueError as exc:
        assert str(exc) == (
            "browser_manager is required."
        )
    else:
        raise AssertionError(
            "ValueError was not raised."
        )


def test_application_rejects_invalid_source_type():
    session_factory = create_test_session()

    try:
        create_application(
            session_factory=session_factory,
            browser_manager="fake-browser",
            source=123,
        )
    except TypeError as exc:
        assert str(exc) == (
            "source must be a string."
        )
    else:
        raise AssertionError(
            "TypeError was not raised."
        )


def test_application_rejects_empty_source():
    session_factory = create_test_session()

    try:
        create_application(
            session_factory=session_factory,
            browser_manager="fake-browser",
            source="   ",
        )
    except ValueError as exc:
        assert str(exc) == (
            "source cannot be empty."
        )
    else:
        raise AssertionError(
            "ValueError was not raised."
        )


def test_create_application_returns_composed_application():
    session_factory = create_test_session()

    application = create_application(
        session_factory=session_factory,
        browser_manager="fake-browser",
    )

    assert isinstance(
        application,
        Application,
    )

    assert application.registry is not None
    assert application.factory is not None
    assert application.pipeline is not None

