from pathlib import Path

import pytest

from exporters.base import BaseExporter
from exporters.service import ExportService


class FakeExporter(BaseExporter):
    def __init__(self):
        self.calls = []

    def export(self, data, output_path):
        self.calls.append(
            {
                "data": data,
                "output_path": output_path,
            }
        )
        return Path(output_path)


def test_export_service_routes_to_requested_exporter(tmp_path):
    csv_exporter = FakeExporter()
    json_exporter = FakeExporter()

    service = ExportService(
        exporters={
            "csv": csv_exporter,
            "json": json_exporter,
        }
    )

    data = [
        {"name": "Pizza Sara"},
    ]

    output_path = tmp_path / "businesses.csv"

    result = service.export(
        data=data,
        output_path=output_path,
        format_name="csv",
    )

    assert result == output_path
    assert len(csv_exporter.calls) == 1
    assert len(json_exporter.calls) == 0
    assert csv_exporter.calls[0]["data"] == data
    assert csv_exporter.calls[0]["output_path"] == output_path


def test_export_service_normalizes_format_name(tmp_path):
    exporter = FakeExporter()

    service = ExportService(
        exporters={
            "csv": exporter,
        }
    )

    output_path = tmp_path / "businesses.csv"

    result = service.export(
        data=[],
        output_path=output_path,
        format_name=" CSV ",
    )

    assert result == output_path
    assert len(exporter.calls) == 1


def test_export_service_rejects_unsupported_format(tmp_path):
    exporter = FakeExporter()

    service = ExportService(
        exporters={
            "csv": exporter,
        }
    )

    with pytest.raises(
        ValueError,
        match="Unsupported export format: json",
    ):
        service.export(
            data=[],
            output_path=tmp_path / "businesses.json",
            format_name="json",
        )


def test_export_service_requires_exporters_dictionary():
    with pytest.raises(
        TypeError,
        match="exporters must be a dictionary",
    ):
        ExportService([])


def test_export_service_rejects_empty_exporters():
    with pytest.raises(
        ValueError,
        match="exporters cannot be empty",
    ):
        ExportService({})


def test_export_service_rejects_invalid_exporter():
    with pytest.raises(
        TypeError,
        match="all exporters must be BaseExporter instances",
    ):
        ExportService(
            {
                "csv": object(),
            }
        )


def test_export_service_rejects_empty_format_name(tmp_path):
    exporter = FakeExporter()

    service = ExportService(
        exporters={
            "csv": exporter,
        }
    )

    with pytest.raises(
        ValueError,
        match="format_name cannot be empty",
    ):
        service.export(
            data=[],
            output_path=tmp_path / "businesses.csv",
            format_name="   ",
        )


def test_export_service_rejects_non_string_format_name(tmp_path):
    exporter = FakeExporter()

    service = ExportService(
        exporters={
            "csv": exporter,
        }
    )

    with pytest.raises(
        TypeError,
        match="format_name must be a string",
    ):
        service.export(
            data=[],
            output_path=tmp_path / "businesses.csv",
            format_name=None,
        )