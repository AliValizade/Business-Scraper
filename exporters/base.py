from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Iterable


class BaseExporter(ABC):
    """Base contract for all exporters."""

    @abstractmethod
    def export(
        self,
        data: Iterable[dict[str, Any]],
        output_path: str | Path,
    ) -> Path:
        """
        Export business data to the requested output path.

        Args:
            data: Iterable of business dictionaries.
            output_path: Destination file path.

        Returns:
            The final output path.

        Raises:
            NotImplementedError:
                If a subclass does not implement the export method.
        """
        raise NotImplementedError