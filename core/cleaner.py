from urllib.parse import urlparse

from utils.phone import normalize_phone
from utils.text import (
    normalize_address,
    normalize_category,
    normalize_city,
    normalize_digits,
    normalize_keyword,
    normalize_name,
)


class BusinessCleaner:
    """
    Cleans and normalizes raw business data before
    persistence or deduplication.
    """

    TEXT_FIELDS = {
        "name": normalize_name,
        "category": normalize_category,
        "address": normalize_address,
        "city": normalize_city,
        "search_keyword": normalize_keyword,
    }

    def clean(self, business):
        if not isinstance(business, dict):
            raise TypeError(
                "Business data must be a dictionary."
            )

        cleaned = business.copy()

        self._clean_text_fields(cleaned)
        self._clean_phone(cleaned)
        self._clean_numeric_fields(cleaned)
        self._clean_urls(cleaned)

        return cleaned

    def _clean_text_fields(self, business):
        for field, normalizer in self.TEXT_FIELDS.items():
            if field in business:
                business[field] = normalizer(
                    business[field]
                )

    def _clean_phone(self, business):
        if "phone" in business:
            business["phone"] = normalize_phone(
                business["phone"]
            )

    def _clean_numeric_fields(self, business):
        if "rating" in business:
            business["rating"] = self._clean_rating(
                business["rating"]
            )

        if "reviews_count" in business:
            business["reviews_count"] = (
                self._clean_reviews_count(
                    business["reviews_count"]
                )
            )

        if "latitude" in business:
            business["latitude"] = self._clean_float(
                business["latitude"]
            )

        if "longitude" in business:
            business["longitude"] = self._clean_float(
                business["longitude"]
            )

    def _clean_rating(self, value):
        if value is None:
            return None

        try:
            if isinstance(value, str):
                value = normalize_digits(value)
                value = value.replace(",", ".")

            rating = float(value)

            if not 0 <= rating <= 5:
                return None

            return rating

        except (TypeError, ValueError):
            return None

    def _clean_reviews_count(self, value):
        if value is None:
            return None

        try:
            value = normalize_digits(value)

            if isinstance(value, str):
                value = value.replace(",", "")
                value = value.replace(".", "")
                value = value.strip()

            return int(value)

        except (TypeError, ValueError):
            return None

    def _clean_float(self, value):
        if value is None:
            return None

        try:
            value = normalize_digits(value)

            if isinstance(value, str):
                value = value.replace(",", ".")

            return float(value)

        except (TypeError, ValueError):
            return None

    def _clean_urls(self, business):
        for field in (
            "website",
            "instagram",
            "google_maps_url",
            "source_url",
        ):
            if field in business:
                business[field] = self._normalize_url(
                    business[field]
                )

    def _normalize_url(self, value):
        if value is None:
            return None

        value = str(value).strip()

        if not value:
            return None

        parsed = urlparse(value)

        if not parsed.scheme:
            return value

        return value