import json
from pathlib import Path
from typing import Any, Iterable

from exporters.base import BaseExporter


class JSONExporter(BaseExporter):
    """Export business data to a JSON file."""

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
            encoding="utf-8",
        ) as file:
            json.dump(
                rows,
                file,
                ensure_ascii=False,
                indent=2,
            )

        return output_path