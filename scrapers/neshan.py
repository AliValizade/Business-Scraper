import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen

from scrapers.base import BaseScraper
from core.states import ScraperState
from utils.logger import get_logger


logger = get_logger(__name__)


class NeshanAPIError(RuntimeError):
    """Raised when a Neshan API request fails."""

    def __init__(self, status_code, message):
        self.status_code = status_code
        super().__init__(message)


class NeshanScraper(BaseScraper):
    """API-based scraper for Neshan business/location search."""

    BASE_URL = "https://api.neshan.org"
    SEARCH_PATH = "/v3/search"
    GEOCODING_PATH = "/geocoding/v1"
    POI_DETAILS_PATH = "/v1/point"
    MAX_RESULTS = 30

    def __init__(
        self,
        browser_manager=None,
        api_key=None,
        http_get=None,
        max_results=None,
    ):
        super().__init__(browser_manager)

        self.api_key = (
            api_key
            if api_key is not None
            else os.getenv("NESHAN_API_KEY")
        )
        self.http_get = http_get or self._http_get
        self.max_results = (
            self.MAX_RESULTS
            if max_results is None
            else min(max_results, self.MAX_RESULTS)
        )

        self.search_keyword = None
        self.search_location = None
        self._businesses = []

        if not isinstance(self.max_results, int):
            raise TypeError("max_results must be an integer.")

        if self.max_results <= 0:
            raise ValueError("max_results must be greater than zero.")

    def _require_api_key(self):
        if not isinstance(self.api_key, str) or not self.api_key.strip():
            raise ValueError(
                "Neshan API key is required. "
                "Set NESHAN_API_KEY or pass api_key explicitly."
            )

    def _build_url(self, path, params):
        query = urlencode(params)
        return f"{self.BASE_URL}{path}?{query}"

    def _http_get(self, url):
        request = Request(
            url,
            headers={
                "Api-Key": self.api_key,
                "Accept": "application/json",
            },
            method="GET",
        )

        try:
            with urlopen(request, timeout=30) as response:
                return response.status, response.read().decode("utf-8")

        except HTTPError as error:
            try:
                body = error.read().decode("utf-8")
            except Exception:
                body = ""

            raise NeshanAPIError(
                error.code,
                f"Neshan API request failed with HTTP {error.code}: {body}",
            ) from error

        except URLError as error:
            raise NeshanAPIError(
                None,
                f"Neshan API connection failed: {error.reason}",
            ) from error

    def _get_json(self, path, params):
        self._require_api_key()

        url = self._build_url(path, params)
        status_code, body = self.http_get(url)

        if not 200 <= status_code < 300:
            raise NeshanAPIError(
                status_code,
                f"Neshan API returned HTTP {status_code}.",
            )

        try:
            return json.loads(body)
        except json.JSONDecodeError as error:
            raise NeshanAPIError(
                status_code,
                "Neshan API returned invalid JSON.",
            ) from error

    @staticmethod
    def _parse_location(location):
        if not isinstance(location, dict):
            return None, None

        try:
            latitude = float(location["latitude"])
            longitude = float(location["longitude"])
        except (KeyError, TypeError, ValueError):
            return None, None

        return latitude, longitude

    def _geocode_location(self, location):
        payload = {
            "address": str(location).strip(),
        }

        response = self._get_json(
            self.GEOCODING_PATH,
            {"json": json.dumps(payload, ensure_ascii=False)},
        )

        items = response.get("items") or []

        if not items:
            raise ValueError(
                f"Neshan could not resolve location '{location}'."
            )

        latitude, longitude = self._parse_location(
            items[0].get("location")
        )

        if latitude is None or longitude is None:
            raise ValueError(
                f"Neshan returned an invalid location for '{location}'."
            )

        return latitude, longitude

    def _search(self, query, latitude, longitude):
        search_query = {
            "term": query,
            "center": {
                "latitude": latitude,
                "longitude": longitude,
            },
        }

        response = self._get_json(
            self.SEARCH_PATH,
            {"q": json.dumps(search_query, ensure_ascii=False)},
        )

        items = response.get("items") or []

        return items[: self.max_results]

    def _get_poi_details(self, poi_hash):
        response = self._get_json(
            self.POI_DETAILS_PATH,
            {"hash": poi_hash},
        )

        if not isinstance(response, dict):
            raise NeshanAPIError(
                200,
                "Neshan POI Details returned an invalid response.",
            )

        return response

    @staticmethod
    def _extract_instagram(social_networks):
        if not isinstance(social_networks, list):
            return None

        for network in social_networks:
            if not isinstance(network, dict):
                continue

            name = str(
                network.get("name")
                or network.get("type")
                or ""
            ).lower()

            if "instagram" in name:
                return (
                    network.get("url")
                    or network.get("value")
                    or network.get("link")
                )

        return None

    def _map_business(self, item, details=None):
        details = details or {}

        search_location = item.get("location") or {}
        detail_location = details.get("location") or search_location

        latitude = detail_location.get("y")
        longitude = detail_location.get("x")

        try:
            latitude = float(latitude) if latitude is not None else None
        except (TypeError, ValueError):
            latitude = None

        try:
            longitude = (
                float(longitude)
                if longitude is not None
                else None
            )
        except (TypeError, ValueError):
            longitude = None

        layer = details.get("layer") or {}

        name = details.get("name") or item.get("title")
        category = (
            layer.get("title")
            or item.get("category")
            or item.get("type")
        )
        address = details.get("address") or item.get("address")

        social_networks = details.get("socialNetworks")
        instagram = self._extract_instagram(social_networks)

        return {
            "name": name,
            "category": category,
            "address": address,
            "phone": details.get("phoneNumber"),
            "website": details.get("website"),
            "instagram": instagram,
            "rating": None,
            "reviews_count": None,
            "latitude": latitude,
            "longitude": longitude,
            "source": "neshan",
            "source_id": item.get("poiHash"),
            "source_url": f"{self.BASE_URL}{self.SEARCH_PATH}",
            "google_maps_url": None,
            "search_keyword": self.search_keyword,
            "city": self.search_location,
        }

    def search(self, query, location):
        self.set_state(ScraperState.SEARCHING)

        self.search_keyword = query
        self.search_location = location
        self._businesses = []

        try:
            latitude, longitude = self._geocode_location(location)

            self.set_state(ScraperState.LOADING)

            items = self._search(
                query,
                latitude,
                longitude,
            )

            self._businesses = items

            logger.info(
                "Neshan search completed | query=%s | "
                "location=%s | results=%s",
                query,
                location,
                len(items),
            )

            return items

        except Exception:
            self.set_state(ScraperState.FAILED)

            logger.exception(
                "Neshan search failed | query=%s | location=%s",
                query,
                location,
            )
            raise

    def scrape(self):
        if not self._businesses:
            return []

        self.set_state(ScraperState.EXTRACTING)

        businesses = []

        for item in self._businesses[: self.max_results]:
            details = None
            poi_hash = item.get("poiHash")

            if poi_hash:
                try:
                    details = self._get_poi_details(poi_hash)
                except Exception as error:
                    logger.warning(
                        "Neshan POI enrichment failed | "
                        "poi_hash=%s | error=%s",
                        poi_hash,
                        error,
                    )

            try:
                businesses.append(
                    self._map_business(
                        item,
                        details=details,
                    )
                )
            except Exception:
                logger.exception(
                    "Neshan business mapping failed | item=%s",
                    item,
                )

        self.set_state(ScraperState.COMPLETED)

        logger.info(
            "Neshan scraping completed | businesses=%s",
            len(businesses),
        )

        return businesses
