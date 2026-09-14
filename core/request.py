from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class ScrapeRequest:
    """
    Standardized input for a scraping operation.

    A request can contain one or multiple keywords
    for a single location.
    """

    location: str
    keywords: Sequence[str]

    def __post_init__(self):
        if not isinstance(self.location, str):
            raise TypeError("location must be a string.")

        if not self.location.strip():
            raise ValueError("location cannot be empty.")

        if isinstance(self.keywords, str):
            raise TypeError(
                "keywords must be a sequence of strings, "
                "not a single string."
            )

        if not self.keywords:
            raise ValueError(
                "keywords must contain at least one keyword."
            )

        normalized_keywords = []

        for keyword in self.keywords:
            if not isinstance(keyword, str):
                raise TypeError(
                    "each keyword must be a string."
                )

            keyword = keyword.strip()

            if not keyword:
                raise ValueError(
                    "keywords cannot contain empty values."
                )

            normalized_keywords.append(keyword)

        object.__setattr__(
            self,
            "location",
            self.location.strip(),
        )

        object.__setattr__(
            self,
            "keywords",
            tuple(normalized_keywords),
        )