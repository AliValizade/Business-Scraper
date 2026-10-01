from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class ScrapeRequestDTO:
    location: str
    keywords: tuple[str, ...]
    max_results: int | None = None

    @classmethod
    def from_values(cls, location, keywords, max_results=None):
        return cls(
            location=location,
            keywords=tuple(keywords),
            max_results=max_results,
        )


@dataclass(frozen=True)
class ScrapeResultDTO:
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


@dataclass(frozen=True)
class BusinessDTO:
    id: int
    name: str
    category: str | None = None
    address: str | None = None
    city: str | None = None
    phone: str | None = None
    website: str | None = None
    instagram: str | None = None
    rating: float | None = None
    reviews_count: int | None = None
    latitude: float | None = None
    longitude: float | None = None
    google_maps_url: str | None = None
    source: str = ""
    source_id: str | None = None
    search_keyword: str | None = None
    scraped_at: datetime | None = None
    source_url: str | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None


@dataclass(frozen=True)
class RunDTO:
    id: int
    source: str
    city: str | None
    keyword: str | None
    started_at: datetime
    finished_at: datetime | None
    status: str
    total_found: int
    total_new: int
    total_updated: int
    total_duplicates: int
    total_errors: int
    error_message: str | None = None


@dataclass(frozen=True)
class ExportResultDTO:
    output_path: Any
    format_name: str
    exported_count: int | None = None


class LicenseStatus(str, Enum):
    UNLICENSED = "unlicensed"
    ACTIVE = "active"


@dataclass(frozen=True)
class LicenseInfoDTO:
    status: LicenseStatus
    product: str
    edition: str
    license_key: str | None = None
    activated_at: datetime | None = None
