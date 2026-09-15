import csv
from pathlib import Path
from typing import Any, Iterable

from exporters.base import BaseExporter


class CSVExporter(BaseExporter):
    """Export business data to a CSV file."""

    def export(
        self,
        data: Iterable[dict[str, Any]],
        output_path: str | Path,
    ) -> Path:
        output_path = Path(output_path)

        rows = list(data)

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        with output_path.open(
            "w",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            if not rows:
                return output_path

            fieldnames = self._get_fieldnames(rows)

            writer = csv.DictWriter(
                file,
                fieldnames=fieldnames,
                extrasaction="ignore",
            )

            writer.writeheader()
            writer.writerows(rows)

        return output_path

    @staticmethod
    def _get_fieldnames(
        rows: list[dict[str, Any]],
    ) -> list[str]:
        fieldnames = []

        for row in rows:
            for key in row:
                if key not in fieldnames:
                    fieldnames.append(key)

        return fieldnames