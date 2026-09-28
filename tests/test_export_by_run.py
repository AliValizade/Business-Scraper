from types import SimpleNamespace
from unittest.mock import Mock

import pytest

from app.application import Application
from cli.commands import run_export_command
from cli.parser import create_parser
from core.errors import RunNotFoundError


class FakePipeline:
    def run(self, request):
        return {"status": "COMPLETED"}


def test_parser_accepts_run_id_for_export():
    parser = create_parser()

    args = parser.parse_args(
        [
            "export",
            "--run-id",
            "7",
            "--format",
            "csv",
            "--output",
            "exports/run7.csv",
        ]
    )

    assert args.command == "export"
    assert args.run_id == 7
    assert args.format_name == "csv"
    assert args.output_path == "exports/run7.csv"


def test_parser_defaults_run_id_to_none():
    parser = create_parser()

    args = parser.parse_args(
        [
            "export",
            "--format",
            "json",
            "--output",
            "exports/businesses.json",
        ]
    )

    assert args.run_id is None


def test_application_export_run_uses_associated_businesses():
    export_service = Mock()
    export_service.export.return_value = "exports/run7.csv"

    application = Application(
        pipeline=FakePipeline(),
        export_service=export_service,
    )

    businesses = [
        {"id": 2, "name": "Business B"},
        {"id": 5, "name": "Business E"},
    ]

    application.get_run_businesses = Mock(
        return_value=businesses
    )

    result = application.export_run(
        run_id=7,
        output_path="exports/run7.csv",
        format_name="csv",
    )

    application.get_run_businesses.assert_called_once_with(7)
    export_service.export.assert_called_once_with(
        data=businesses,
        output_path="exports/run7.csv",
        format_name="csv",
    )
    assert result == "exports/run7.csv"


def test_application_export_run_propagates_missing_run():
    application = Application(
        pipeline=FakePipeline(),
        export_service=Mock(),
    )

    application.get_run_businesses = Mock(
        side_effect=RunNotFoundError(42)
    )

    with pytest.raises(RunNotFoundError):
        application.export_run(
            run_id=42,
            output_path="exports/run42.json",
            format_name="json",
        )

    application.get_run_businesses.assert_called_once_with(42)


def test_run_export_command_exports_specific_run():
    application = Mock()

    args = SimpleNamespace(
        run_id=7,
        output_path="exports/run7.json",
        format_name="json",
    )

    expected = "exports/run7.json"
    application.export_run.return_value = expected

    result = run_export_command(
        args,
        application,
    )

    application.export_run.assert_called_once_with(
        run_id=7,
        output_path="exports/run7.json",
        format_name="json",
    )
    application.get_businesses.assert_not_called()
    assert result == expected


def test_run_export_command_preserves_all_business_export():
    application = Mock()

    data = [
        {"id": 1, "name": "Business A"},
        {"id": 2, "name": "Business B"},
    ]

    args = SimpleNamespace(
        run_id=None,
        output_path="exports/all.csv",
        format_name="csv",
    )

    application.get_businesses.return_value = data
    application.export.return_value = "exports/all.csv"

    result = run_export_command(
        args,
        application,
    )

    application.get_businesses.assert_called_once_with()
    application.export.assert_called_once_with(
        data=data,
        output_path="exports/all.csv",
        format_name="csv",
    )
    application.export_run.assert_not_called()
    assert result == "exports/all.csv"


def test_run_export_command_with_run_id_does_not_query_all_businesses():
    application = Mock()

    args = SimpleNamespace(
        run_id=3,
        output_path="exports/run3.csv",
        format_name="csv",
    )

    application.export_run.return_value = "exports/run3.csv"

    run_export_command(
        args,
        application,
    )

    application.get_businesses.assert_not_called()
