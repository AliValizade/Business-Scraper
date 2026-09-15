from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class ScrapeRequest:
    location: str
    keywords: tuple[str, ...]
    max_results: int | None = None

    def __post_init__(self):
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

        object.__setattr__(self, "location", location)
        object.__setattr__(self, "keywords", tuple(normalized_keywords))