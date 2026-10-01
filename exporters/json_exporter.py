import json
from datetime import date, datetime
from pathlib import Path
from typing import Any, Iterable

from exporters.base import BaseExporter


def _json_default(value: Any) -> Any:
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


class JSONExporter(BaseExporter):
    """Export business data to a JSON file."""

    def export(
        self,
        data: Iterable[dict[str, Any]],
        output_path: str | Path,
        metadata: dict[str, Any] | None = None,
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
                default=_json_default,
            )

        return output_path
