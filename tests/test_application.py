from unittest.mock import Mock

import pytest

from app.application import Application
from core.request import ScrapeRequest


def test_application_requires_pipeline():
    with pytest.raises(
        ValueError,
        match="pipeline is required.",
    ):
        Application(
            pipeline=None,
        )


def test_application_stores_pipeline():
    pipeline = Mock()

    application = Application(
        pipeline=pipeline,
    )

    assert application.pipeline is pipeline


def test_application_run_creates_scrape_request():
    pipeline = Mock()

    pipeline.run.return_value = {
        "status": "COMPLETED",
    }

    application = Application(
        pipeline=pipeline,
    )

    result = application.run(
        location="مشهد",
        keywords=[
            "پیتزا",
            "فست فود",
        ],
    )

    assert result == {
        "status": "COMPLETED",
    }

    pipeline.run.assert_called_once()

    request = pipeline.run.call_args.kwargs[
        "request"
    ]

    assert isinstance(
        request,
        ScrapeRequest,
    )

    assert request.location == "مشهد"

    assert request.keywords == (
        "پیتزا",
        "فست فود",
    )


def test_application_run_passes_request_to_pipeline():
    pipeline = Mock()

    application = Application(
        pipeline=pipeline,
    )

    application.run(
        location="تهران",
        keywords=["رستوران"],
    )

    request = pipeline.run.call_args.kwargs[
        "request"
    ]

    assert request.location == "تهران"
    assert request.keywords == (
        "رستوران",
    )


def test_application_run_returns_pipeline_result():
    pipeline = Mock()

    expected_result = {
        "status": "COMPLETED",
        "total_found": 10,
        "total_new": 8,
    }

    pipeline.run.return_value = expected_result

    application = Application(
        pipeline=pipeline,
    )

    result = application.run(
        location="مشهد",
        keywords=["پیتزا"],
    )

    assert result is expected_result


def test_application_preserves_registry_and_factory():
    pipeline = Mock()
    registry = Mock()
    factory = Mock()

    application = Application(
        pipeline=pipeline,
        registry=registry,
        factory=factory,
    )

    assert application.registry is registry
    assert application.factory is factory

