from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class ScrapeRequest:
    location: str
    keywords: tuple[str, ...]
    max_results: int | None = None
    source: str = "google_maps"
    access_mode: str = "web"
    api_key: str | None = None

    def __post_init__(self):
        if not isinstance(self.source, str):
            raise TypeError("source must be a string.")
        source = self.source.strip()
        if not source:
            raise ValueError("source cannot be empty.")

        if not isinstance(self.access_mode, str):
            raise TypeError("access_mode must be a string.")
        access_mode = self.access_mode.strip().lower()
        if access_mode not in {"web", "api"}:
            raise ValueError("access_mode must be 'web' or 'api'.")

        if self.api_key is not None and not isinstance(self.api_key, str):
            raise TypeError("api_key must be a string or None.")

        if not isinstance(self.location, str):
            raise TypeError("location must be a string.")

        location = self.location.strip()
        if not location:
            raise ValueError("location cannot be empty.")

        if not isinstance(self.keywords, Sequence) or isinstance(
            self.keywords, (str, bytes)
        ):
            raise TypeError("keywords must be a sequence of strings.")

        if not self.keywords:
            raise ValueError("keywords cannot be empty.")

        normalized_keywords = []

        for keyword in self.keywords:
            if not isinstance(keyword, str):
                raise TypeError("each keyword must be a string.")

            keyword = keyword.strip()

            if not keyword:
                raise ValueError("keywords cannot contain empty values.")

            normalized_keywords.append(keyword)

        if self.max_results is not None:
            if not isinstance(self.max_results, int):
                raise TypeError("max_results must be an integer or None.")

            if self.max_results <= 0:
                raise ValueError("max_results must be greater than zero.")

        object.__setattr__(self, "source", source)
        object.__setattr__(self, "access_mode", access_mode)
        object.__setattr__(self, "api_key", self.api_key.strip() if isinstance(self.api_key, str) else None)
        object.__setattr__(self, "location", location)
        object.__setattr__(self, "keywords", tuple(normalized_keywords))