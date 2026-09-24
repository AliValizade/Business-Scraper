from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class ScrapeResult:
    """Immutable result of a scraping operation."""

    status: str
    source: str
    location: str
    keywords: tuple[str, ...]
    run_id: int

    total_found: int = 0
    total_new: int = 0
    total_updated: int = 0
    total_duplicates: int = 0
    total_errors: int = 0

    error_message: str | None = None

    def __post_init__(self):
        if not isinstance(self.status, str):
            raise TypeError("status must be a string.")
        status = self.status.strip()
        if not status:
            raise ValueError("status cannot be empty.")

        if not isinstance(self.source, str):
            raise TypeError("source must be a string.")
        source = self.source.strip()
        if not source:
            raise ValueError("source cannot be empty.")

        if not isinstance(self.location, str):
            raise TypeError("location must be a string.")
        location = self.location.strip()
        if not location:
            raise ValueError("location cannot be empty.")

        if not isinstance(self.keywords, Sequence) or isinstance(
            self.keywords,
            (str, bytes),
        ):
            raise TypeError("keywords must be a sequence of strings.")

        if not self.keywords:
            raise ValueError("keywords cannot be empty.")

        if not isinstance(self.run_id, int):
            raise TypeError("run_id must be an integer.")

        if self.run_id <= 0:
            raise ValueError("run_id must be greater than zero.")

        normalized_keywords = []

        for keyword in self.keywords:
            if not isinstance(keyword, str):
                raise TypeError("each keyword must be a string.")

            keyword = keyword.strip()

            if not keyword:
                raise ValueError("keywords cannot contain empty values.")

            normalized_keywords.append(keyword)

        counters = {
            "total_found": self.total_found,
            "total_new": self.total_new,
            "total_updated": self.total_updated,
            "total_duplicates": self.total_duplicates,
            "total_errors": self.total_errors,
        }

        for field_name, value in counters.items():
            if not isinstance(value, int):
                raise TypeError(f"{field_name} must be an integer.")

            if value < 0:
                raise ValueError(f"{field_name} cannot be negative.")

        if self.error_message is not None:
            if not isinstance(self.error_message, str):
                raise TypeError("error_message must be a string or None.")

            error_message = self.error_message.strip()

            if not error_message:
                error_message = None
        else:
            error_message = None

        object.__setattr__(self, "status", status)
        object.__setattr__(self, "source", source)
        object.__setattr__(self, "location", location)
        object.__setattr__(
            self,
            "keywords",
            tuple(normalized_keywords),
        )
        object.__setattr__(self, "error_message", error_message)
        object.__setattr__(self, "run_id", self.run_id)