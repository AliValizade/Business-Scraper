from unittest.mock import Mock

import pytest

from app.application import Application

from core.request import ScrapeRequest
from core.result import ScrapeResult


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

    pipeline.run.return_value = ScrapeResult(
        status="COMPLETED",
        source="google_maps",
        location="مشهد",
        keywords=(
            "پیتزا",
            "فست فود",
        ),
        run_id=1,
    )

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

    assert isinstance(result, ScrapeResult)
    assert result.status == "COMPLETED"

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

    expected_result = ScrapeResult(
        status="COMPLETED",
        source="google_maps",
        location="مشهد",
        keywords=("پیتزا",),
        total_found=10,
        total_new=8,
        run_id=1,
    )

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


def test_application_export_delegates_to_export_service(tmp_path):
    class FakeExportService:
        def __init__(self):
            self.calls = []

        def export(
            self,
            data,
            output_path,
            format_name,
        ):
            self.calls.append(
                {
                    "data": data,
                    "output_path": output_path,
                    "format_name": format_name,
                }
            )

            return output_path

    class FakePipeline:
        def run(self, request):
            return {"status": "COMPLETED"}

    export_service = FakeExportService()

    from app.application import Application

    application = Application(
        pipeline=FakePipeline(),
        export_service=export_service,
    )

    data = [
        {"name": "Pizza Sara"},
    ]

    output_path = tmp_path / "businesses.csv"

    result = application.export(
        data=data,
        output_path=output_path,
        format_name="csv",
    )

    assert result == output_path
    assert export_service.calls == [
        {
            "data": data,
            "output_path": output_path,
            "format_name": "csv",
        }
    ]


def test_application_export_requires_export_service():
    class FakePipeline:
        def run(self, request):
            return {"status": "COMPLETED"}

    from app.application import Application

    application = Application(
        pipeline=FakePipeline(),
    )

    import pytest

    with pytest.raises(
        ValueError,
        match="export_service is not configured",
    ):
        application.export(
            data=[],
            output_path="output/test.csv",
            format_name="csv",
        )


def test_application_run_passes_max_results_to_request():
    pipeline = Mock()

    pipeline.run.return_value = ScrapeResult(
        status="COMPLETED",
        source="google_maps",
        location="مشهد",
        keywords=("رستوران",),
        run_id=1,
    )

    application = Application(
        pipeline=pipeline,
    )

    application.run(
        location="مشهد",
        keywords=["رستوران"],
        max_results=25,
    )

    request = pipeline.run.call_args.kwargs[
        "request"
    ]

    assert request.max_results == 25



def test_application_export_passes_metadata_to_export_service():
    export_service = Mock()

    application = Application(
        pipeline=Mock(),
        export_service=export_service,
    )

    data = [{"name": "Pizza Sara"}]

    application.export(
        data=data,
        output_path="output.xlsx",
        format_name="excel",
        metadata={"source": "google_maps"},
    )

    export_service.export.assert_called_once_with(
        data=data,
        output_path="output.xlsx",
        format_name="excel",
        metadata={"source": "google_maps"},
    )


def test_application_export_run_builds_excel_summary_metadata():
    export_service = Mock()
    export_service.export.return_value = "output/run.xlsx"

    application = Application(
        pipeline=Mock(),
        export_service=export_service,
    )

    application.get_run = Mock(
        return_value={
            "source": "google_maps",
            "city": "Mashhad",
            "keyword": "Fast Food",
            "started_at": "started",
            "finished_at": "finished",
            "status": "COMPLETED",
            "total_found": 2,
            "total_new": 2,
            "total_updated": 0,
            "total_duplicates": 0,
            "total_errors": 0,
            "error_message": None,
        }
    )
    application.get_run_businesses = Mock(
        return_value=[
            {"id": 1, "name": "Pizza Sara"},
            {"id": 2, "name": "Fast Food Center"},
        ]
    )

    result = application.export_run(
        run_id=7,
        output_path="output/run.xlsx",
        format_name="excel",
    )

    assert result == "output/run.xlsx"
    application.get_run.assert_called_once_with(7)
    application.get_run_businesses.assert_called_once_with(7)

    export_service.export.assert_called_once_with(
        data=[
            {"id": 1, "name": "Pizza Sara"},
            {"id": 2, "name": "Fast Food Center"},
        ],
        output_path="output/run.xlsx",
        format_name="excel",
        metadata={
            "source": "google_maps",
            "city": "Mashhad",
            "keyword": "Fast Food",
            "started_at": "started",
            "finished_at": "finished",
            "status": "COMPLETED",
            "total_found": 2,
            "total_new": 2,
            "total_updated": 0,
            "total_duplicates": 0,
            "total_errors": 0,
            "error_message": None,
            "exported_businesses": 2,
        },
    )


def test_application_export_run_does_not_add_metadata_for_csv():
    export_service = Mock()
    export_service.export.return_value = "output/run.csv"

    application = Application(
        pipeline=Mock(),
        export_service=export_service,
    )

    application.get_run_businesses = Mock(
        return_value=[{"id": 1, "name": "Pizza Sara"}]
    )

    application.export_run(
        run_id=7,
        output_path="output/run.csv",
        format_name="csv",
    )

    export_service.export.assert_called_once_with(
        data=[{"id": 1, "name": "Pizza Sara"}],
        output_path="output/run.csv",
        format_name="csv",
    )
