from pathlib import Path
from typing import Any, Iterable

from exporters.base import BaseExporter


class ExportService:
    """Coordinate data export through registered exporters."""

    def __init__(
        self,
        exporters: dict[str, BaseExporter],
    ):
        if not isinstance(exporters, dict):
            raise TypeError("exporters must be a dictionary.")

        if not exporters:
            raise ValueError("exporters cannot be empty.")

        for format_name, exporter in exporters.items():
            if not isinstance(format_name, str):
                raise TypeError("export format names must be strings.")

            if not format_name.strip():
                raise ValueError(
                    "export format names cannot be empty."
                )

            if not isinstance(exporter, BaseExporter):
                raise TypeError(
                    "all exporters must be BaseExporter instances."
                )

        self.exporters = {
            format_name.strip().lower(): exporter
            for format_name, exporter in exporters.items()
        }

    def export(
        self,
        data: Iterable[dict[str, Any]],
        output_path: str | Path,
        format_name: str,
    ) -> Path:
        if not isinstance(format_name, str):
            raise TypeError("format_name must be a string.")

        format_name = format_name.strip().lower()

        if not format_name:
            raise ValueError("format_name cannot be empty.")

        exporter = self.exporters.get(format_name)

        if exporter is None:
            available_formats = ", ".join(
                sorted(self.exporters)
            )
            raise ValueError(
                f"Unsupported export format: {format_name}. "
                f"Available formats: {available_formats}"
            )

        return exporter.export(
            data=data,
            output_path=output_path,
        )